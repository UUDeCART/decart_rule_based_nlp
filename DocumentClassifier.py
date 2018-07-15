import csv
import os
from pyConTextNLP.utils import get_document_markups

from itemData import get_item_data
from nlp_pneumonia_utils import markup_context_document
from visual import convertMarkups2DF


class DocumentClassifier(object):
    def __init__(self, targets=None, modifiers=None, feature_inference_rule=None, document_inference_rule=None,
                 expected_values=None, save_markups=True):
        self.document_inferencer = DocumentInferencer(document_inference_rule)
        self.feature_inferencer = FeatureInferencer(feature_inference_rule)
        self.conclusions = []
        self.modifiers = modifiers
        self.targets = targets
        self.save_markups = save_markups
        self.expected_values = [value.lower() for value in expected_values]
        self.saved_markups_map = dict()
        self.last_doc_name = ''

        if modifiers is not None and targets is not None:
            if isinstance(modifiers, str) and isinstance(targets, str):
                if (modifiers.endswith('.csv') or modifiers.endswith('.tsv') or modifiers.endswith(
                        '.txt') or modifiers.endswith('.yml')) \
                        and (targets.endswith('.csv') or targets.endswith('.tsv') or targets.endswith(
                    '.txt') or targets.endswith('.yml')):
                    self.setModifiersTargetsFromFiles(modifiers, targets)
            else:
                self.setModifiersTargets(modifiers, targets)

    def setModifiersTargets(self, modifiers, targets):
        self.modifiers = modifiers
        self.targets = targets

    def setModifiersTargetsFromFiles(self, modifiers_file, targets_file):
        self.targets = get_item_data(targets_file)
        self.modifiers = get_item_data(modifiers_file)

    def reset_saved_predictions(self):
        self.saved_markups_map = {}
        self.save_markups = True
        self.expected_value = None

    def predict(self, doc, doc_name='t_m_p.txt'):
        self.last_doc_name = doc_name
        doc_conclusion = self.classify_doc(doc, doc_name)
        if doc_conclusion in self.expected_values:
            return 1
        return 0

    def eval(self, gold_docs):
        import sklearn
        import pandas as pd
        fn_docs = []
        fp_docs = []
        prediction_metrics = []
        gold_labels = [x.positive_label for x in gold_docs.values()]
        pred_labels = []
        print('Start to evaluate against reference standards...')
        for doc_name, gold_doc in gold_docs.items():
            gold_label = gold_doc.positive_label
            pred_label = self.predict(gold_doc.text, doc_name)
            pred_labels.append(pred_label)
            #       Differentiate false positive and false negative error
            if gold_label == 0 and pred_label == 1:
                fp_docs.append(doc_name)
            elif gold_label == 1 and pred_label == 0:
                fn_docs.append(doc_name)

        precision = sklearn.metrics.precision_score(gold_labels, pred_labels)
        recall = sklearn.metrics.recall_score(gold_labels, pred_labels)
        f1 = sklearn.metrics.f1_score(gold_labels, pred_labels)
        # Let's use Pandas to make a confusion matrix for us
        confusion_matrix_df = pd.crosstab(pd.Series(gold_labels, name='Actual'),
                                          pd.Series(pred_labels, name='Predicted'))
        prediction_metrics.append('Precision : {0:.3f}'.format(precision))
        prediction_metrics.append('Recall :    {0:.3f}'.format(recall))
        prediction_metrics.append('F1:         {0:.3f}'.format(f1))

        return fn_docs, fp_docs, '\n'.join(prediction_metrics), confusion_matrix_df[[1, 0]].reindex([1, 0])

    def predict_against(self, doc, expected_values, doc_name='t_m_p.txt'):
        doc_conclusion = self.classify_doc(doc, doc_name)
        if doc_conclusion in expected_values:
            return 1
        return 0

    def classify_doc(self, doc, doc_name='t_m_p.txt'):
        self.last_doc_name = doc_name
        if self.modifiers is None or self.targets is None:
            print('DocumentClassifier\'s "modifiers" and/or "targets" has not been set yet.\n' +
                  'Use function: setModifiersTargets(modifiers, targets) or setModifiersTargetsFromFiles(modifiers_file,' + 'targets_file) to set them up.')
        context_doc = markup_context_document(doc, self.modifiers, self.targets)
        if doc_name is not None and self.save_markups and len(context_doc.getDocumentGraph().nodes()) > 0:
            self.saved_markups_map[doc_name] = context_doc
        markups = get_document_markups(context_doc)
        annotations, relations, doc_txt = convertMarkups2DF(markups)
        matched_conclusion_types = self.feature_inferencer.process(annotations, relations)
        doc_conclusion = self.document_inferencer.process(matched_conclusion_types)
        return doc_conclusion

    def get_last_context_doc(self):
        if self.last_doc_name in self.saved_markups_map:
            return self.saved_markups_map[self.last_doc_name]
        else:
            return None


class FeatureInferencer(object):
    match_checker = dict()
    inference_map = dict()
    rule_conclusion_types = []
    rule_source_types = []

    def __init__(self, ruleFile, header_lines=0, delimiter=','):
        rules = read_csv_rules(ruleFile, lower=True, header_lines=header_lines, delimiter=delimiter)
        self.match_checker.clear()
        self.inference_map.clear()
        inference_map = self.inference_map
        match_checker = self.match_checker
        rule_id = 0
        for rule in rules:
            conclusion_type = rule[0]
            source_type = rule[1]
            self.rule_conclusion_types.append(conclusion_type)
            self.rule_source_types.append(source_type)
            condition_values = rule[2:]
            if source_type not in match_checker:
                match_checker[source_type] = dict()
                inference_map[source_type] = dict()
            match_checker[source_type][rule_id] = set(condition_values)
            inference_map[source_type][rule_id] = conclusion_type
            rule_id += 1
        pass

    def process(self, annotations, relations):
        matched_conclusion_types = []
        inference_map = self.inference_map
        match_checker = self.match_checker
        sorted_modifiers = dict()
        annotations_idx = annotations.set_index('markup_id')
        target_markups = annotations[annotations['vis_category'] == 'Target']
        targets = set(target_markups['markup_id'].tolist())
        # match the source target type and modifier value pairs (relations)
        # get a dictionary of matched rule_ids with corresponding total number of matched condition modifier values
        for relation_id, relation in relations.iterrows():
            relation_type = relation['type']
            # not using relation['arg1_cate'] here, because for visualization purpose,
            # the relation['arg1_cate'] (modifier_type) has been unified to 'Modifier'
            target_id = relation['arg2_id']
            if relation['arg1_cate'] != 'Modifier':
                # if this is a termination relation, skip
                continue
            if target_id not in sorted_modifiers:
                sorted_modifiers[target_id] = set()
            sorted_modifiers[target_id].add(relation_type)

        for target_id, modifiers in sorted_modifiers.items():
            source_type = annotations_idx.loc[target_id, 'type']
            for rule_id, modifiers_in_rule in match_checker[source_type].items():
                if modifiers_in_rule == modifiers or modifiers_in_rule == set(''):
                    matched_conclusion_types.append(inference_map[source_type][rule_id])
                    targets.remove(target_id)

        for source_type, matcher in match_checker.items():
            for rule_id, condition_values in matcher.items():
                if len(condition_values) == 0:
                    for anno in annotations:
                        if anno['type'] == source_type:
                            matched_conclusion_types.append(inference_map[source_type][rule_id])

        for target_id in targets:
            type = annotations.loc[annotations['markup_id'] == target_id, 'type'].iloc[0]
            matched_conclusion_types.append(type)
        return matched_conclusion_types


class DocumentInferencer(object):
    rule_matchers = dict()
    doc_conclusions = []
    expected_evidence_types = set()
    default_conclusion = 'NEG_DOC'

    def __init__(self, ruleFile, header_lines=0, delimiter=','):
        rules = read_csv_rules(ruleFile, lower=True, header_lines=header_lines, delimiter=delimiter)
        rule_id = 0
        for rule in rules:
            doc_type = rule[0]
            # if no evidence type required, this is the default document conclusion type
            if len(rules) == 1:
                self.default_conclusion = doc_type
                continue
            self.doc_conclusions.append(doc_type)
            matcher = set(rule[1:])
            # save this for optimizing FeatureInferencer processing
            self.expected_evidence_types.update(rule[1:])
            self.rule_matchers[rule_id] = matcher
            rule_id += 1
        pass

    def process(self, matched_conclusion_types):
        for rule_id, matcher in self.rule_matchers.items():
            if matcher.issubset(matched_conclusion_types):
                return self.doc_conclusions[rule_id]
        return self.default_conclusion


def read_csv_rules(file_str, lower=True, header_lines=0, delimiter=','):
    rows = []
    inputObject = file_str
    line_number = -1
    if file_str.endswith('.csv'):
        pwd = os.getcwd()
        if pwd not in file_str:
            file_str = os.path.join(pwd, file_str)
        line_number = -1
        inputObject = open(file_str)
    else:
        inputObject = file_str.split('\n')
        header_lines = -1
    csvReader = csv.reader(inputObject, delimiter=delimiter)
    for row in csvReader:
        if len(row) == 0 or row[0].strip().startswith('#'):
            continue
        line_number += 1
        # skip header lines, empty lines and comments lines
        if line_number <= header_lines:
            continue
        if lower:
            rows.append([cell.lower() for cell in row])
        else:
            rows.append(row)
    if file_str.endswith('.csv'):
        inputObject.close()
    return rows


# All the rule will be processed no matter in which order saved in this file
# Rules with more modifier values (conditions) have higher priority

# this implementation is more efficient when inference rules are too many

# the rule definition is different from the other implemention, where this need to list all the
# possible combinations of modifiers that including the evidence modifier.
class FeatureInferencer2(object):
    match_checker = dict()
    inference_map = dict()
    rule_conclusion_types = []
    rule_source_types = []

    def __init__(self, ruleFile, header_lines=0, delimiter=','):
        rules = read_csv_rules(ruleFile, header_lines=header_lines, delimiter=delimiter)
        self.match_checker.clear()
        self.inference_map.clear()
        inference_map = self.inference_map
        match_checker = self.match_checker
        rule_id = 0
        for rule in rules:
            conclusion_type = rule[0]
            source_type = rule[1]
            self.rule_conclusion_types.append(conclusion_type)
            self.rule_source_types.append(source_type)
            condition_values = rule[2:]
            if source_type not in inference_map:
                inference_map[source_type] = dict()
            for value in condition_values:
                if value not in inference_map[source_type]:
                    inference_map[source_type][value] = set()
                inference_map[source_type][value].add(rule_id)
                if rule_id not in match_checker:
                    match_checker[rule_id] = 1
                else:
                    match_checker[rule_id] += 1
            rule_id += 1
        pass

    def process(self, annotations, relations):
        matched_conclusion_types = set()
        inference_map = self.inference_map
        match_checker = self.match_checker
        match_counters = dict()
        annotations_idx = annotations.set_index('markup_id')
        # match the source target type and modifier value pairs (relations)
        # get a dictionary of matched rule_ids with corresponding total number of matched condition modifier values
        for relation_id, relation in relations.iterrows():
            relation_type = relation['type']
            # not using modifier_type, because for visualizaiton purpose, the modifier_type has been unified to 'Modifier'
            # modifier_type = relation['arg1_cate']
            target_id = relation['arg2_id']
            target_type = annotations_idx.loc[target_id, 'type']
            if target_type in inference_map and relation_type in inference_map[target_type]:
                for rule_id in inference_map[target_type][relation_type]:
                    # if you know what you are expecting, and this conclusion type is not in your expectation list, ignore it
                    if target_id not in match_counters:
                        match_counters[target_id] = dict()
                    match_counter = match_counters[target_id]
                    if rule_id not in match_counter:
                        match_counter[rule_id] = 1
                    else:
                        match_counter[rule_id] += 1

        # check the total number of matched condition modifier values of each rule,
        # to see if the number matches the definition and solve the confliction
        previous_matched_rule_id = -1
        for match_counter in match_counters.values():
            for rule_id in match_counter.keys():
                if match_counter[rule_id] == match_checker[rule_id]:
                    source_type = self.rule_source_types[rule_id]
                    if previous_matched_rule_id == -1 or match_counter[previous_matched_rule_id] <= match_checker[
                        rule_id]:
                        # if multiple rules are matched for the same source target type,
                        # prioritize the longer matches-- more detailed modifier values
                        previous_matched_rule_id = rule_id
            if previous_matched_rule_id > -1:
                matched_conclusion_types.add(self.rule_conclusion_types[previous_matched_rule_id])
        return matched_conclusion_types
