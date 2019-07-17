import os
from collections import OrderedDict

from IPython.core.display import display
from ipywidgets import HTML

from nlp_pneumonia_utils import AnnotatedDocument, Annotation
from intervaltree import IntervalTree
import pandas as pd


class Evaluator:

    def __init__(self, tp=0, fp=0, tn=None, fn=0):
        self.tp = tp
        self.fp = fp
        self.tn = tn
        self.fn = fn
        #  a dictionary using a doc_name as a key, a list of false negative annotations as a value
        self.fns = OrderedDict()
        #  a dictionary using a doc_name as a key, a list of false positive annotations as a value
        self.fps = OrderedDict()
        pass

    def add_tp(self, n=1):
        self.tp += n

    def add_tn(self, n=1):
        if self.tn is None:
            self.tn = n
        else:
            self.tn += n

    def add_fp(self, n=1):
        self.fp += n

    def add_fn(self, n=1):
        self.fn += n

    def append_fps(self, doc_name, fps):
        if doc_name not in self.fps:
            self.fps[doc_name] = []
        self.fps[doc_name].extend(fps)

    def append_fns(self, doc_name, fns):
        if doc_name not in self.fns:
            self.fns[doc_name] = []
        self.fns[doc_name].extend(fns)

    def get_values(self):
        return self.tp, self.fp, self.fn, self.tn

    def display_values(self):
        df = pd.DataFrame({'B+': [self.tp, self.fn],
                           'B-': [self.fp, self.tn]},
                          index=['A+', 'A-'])
        return df

    def total(self):
        return self.tn + self.tp + self.fp + self.tn

    def get_recall(self):
        return round(100 * self.tp / (self.tp + self.fn)) / 100

    def get_precision(self):
        return round(100 * self.tp / (self.tp + self.fp)) / 100

    def get_f1(self):
        return round(200 * self.tp / (2 * self.tp + self.fp + self.fn)) / 100

    def get_iaa(self):
        return self.get_f1()

    def get_fns(self) -> dict:
        return self.fns

    def get_fps(self) -> dict:
        return self.fps

    # TODO
    def report(self):
        pass


def group_brat_annotations(lines):
    annotations = {}
    # BRAT FORMAT is:
    # NUMBER[TAB]TYPE[SPACE]START_INDEX[SPACE]END_INDEX[SPACE]SPANNED_TEXT
    for line in lines:
        line = str(line)
        if len(line.strip()) == 0:
            continue
        tab_tokens = line.split('\t')
        space_tokens = tab_tokens[1].split()
        anno = Annotation()
        anno.spanned_text = tab_tokens[-1]
        anno.type = space_tokens[0]
        anno.start_index = int(space_tokens[1])
        anno.end_index = int(space_tokens[-1])
        if anno.type not in annotations:
            annotations[anno.type] = []
        annotations[anno.type].append(anno)
    return annotations


def docs_reader(project_dir):
    annotation_map = {}
    doc_map = {}
    for name in sorted(os.listdir(project_dir)):
        basename = name.split('.')[0]
        if name.endswith('.txt'):
            with open(os.path.join(project_dir, name)) as f1:
                doc_map[basename] = f1.read()
            f1.close()
        elif name.endswith('.ann'):
            annotation_map[basename] = {}
            with open(os.path.join(project_dir, name)) as f2:
                annotation_map[basename] = group_brat_annotations(f2.readlines())
            f2.close()
    return doc_map, annotation_map


def compare_projects(dir1: str, dir2: str, compare_method: str, types=set()) -> dict:
    doc_map1, annotation_map1 = docs_reader(dir1)
    doc_map2, annotation_map2 = docs_reader(dir2)
    return doc_map1, compare(annotation_map1, annotation_map2, compare_method, types)


def compare(annotation_map1: dict, annotation_map2: dict, compare_method='relax', types=set()) -> dict:
    """
    :param annotation_map1: a dictionary with doc_name as the key, an AnnotatedDocument as the value
    :param annotation_map2:a dictionary with doc_name as the key, an AnnotatedDocument as the value (of reference annotator)
    :param compare_method: "strict" or "relax"
    :return: a dictionary of Evaluators (each Evaluator stores the compared results of one annotation type)
    """
    if len(annotation_map1) != len(annotation_map2):
        raise ValueError("The two input datasets don't have a equal amount of documents.")
        return None
    evaluators = {}
    # if you know the list of types that you will compare, you can set it up. Otherwise, it will go over all
    #  the annotations to find all the types
    if len(types) == 0:
        for grouped_annotations in annotation_map1.values():
            types.update(grouped_annotations.keys())
        for grouped_annotations in annotation_map2.values():
            types.update(grouped_annotations.keys())
    for doc_name, grouped_annotations in annotation_map1.items():
        if compare_method[0].lower().startswith('s'):
            strict_compare_one_doc(evaluators, doc_name, grouped_annotations, annotation_map2[doc_name], sorted(types))
        else:
            relax_compare_one_doc(evaluators, doc_name, grouped_annotations, annotation_map2[doc_name], sorted(types))

    return evaluators


#  consider a match only when the annotations' spans exactly match (both start and end are equal)
#  evaluator, annotations to be compared, reference annotations
def strict_compare_one_doc(evaluators: Evaluator, doc_name: str, grouped_annotations1: [], grouped_annotations2: [],
                           types):
    for type_name in types:
        if type_name not in evaluators:
            evaluators[type_name] = Evaluator()
        evaluator = evaluators[type_name]
        if type_name not in grouped_annotations1:
            if type_name in grouped_annotations2:
                evaluator.add_fn(len(grouped_annotations2[type_name]))
                evaluator.append_fns(doc_name, grouped_annotations2[type_name])
            continue
        annos_list_of_one_type = grouped_annotations1[type_name]

        if type_name not in grouped_annotations2 or len(grouped_annotations2[type_name]) == 0:
            evaluator.add_fp(len(annos_list_of_one_type))
            evaluator.append_fps(doc_name, annos_list_of_one_type)
            continue

        annos1 = sorted(annos_list_of_one_type, key=lambda x: x.start_index)
        annos2 = sorted(grouped_annotations2[type_name], key=lambda x: x.start_index)

        # Of course, we can try compare each one in a list against all in the other list. 
        # But here is an optimized way        
        # two pointers to track the two lists
        p1 = 0
        p2 = 0
        while p1 < len(annos1) and p2 < len(annos2):
            anno1 = annos1[p1]
            anno2 = annos2[p2]
            if anno1.start_index == anno2.start_index:
                if anno1.end_index == anno2.end_index:
                    evaluator.add_tp()
                else:
                    evaluator.add_fn()
                    evaluator.append_fns(doc_name, [anno2])

                p1 += 1
                p2 += 1
            elif anno1.start_index < anno2.start_index:
                p1 += 1
                evaluator.add_fp()
                evaluator.append_fps(doc_name, [anno1])
            elif anno1.start_index > anno2.start_index:
                p2 += 1
                evaluator.add_fn()
                evaluator.append_fns(doc_name, [anno2])

        if p1 < len(annos1):
            evaluator.add_fp(len(annos1) - p1)
            evaluator.append_fps(doc_name, annos1[p1:])
        elif p2 < len(annos2):
            evaluator.add_fn(len(annos2) - p2)
            evaluator.append_fns(doc_name, annos2[p2:])
    pass


def build_interval_tree(annos: []) -> IntervalTree:
    t = IntervalTree()
    for i in range(0, len(annos)):
        begin = annos[i].start_index
        end = annos[i].end_index
        t[begin:end] = i
    return t


def relax_compare_one_doc(evaluators: Evaluator, doc_name: str, grouped_annotations1: [], grouped_annotations2: [],
                          types):
    for type_name in types:
        if type_name not in evaluators:
            evaluators[type_name] = Evaluator()
        evaluator = evaluators[type_name]
        if type_name not in grouped_annotations1:
            if type_name in grouped_annotations2:
                evaluator.add_fn(len(grouped_annotations2[type_name]))
                evaluator.append_fns(doc_name, grouped_annotations2[type_name])
            continue
        annos_list_of_one_type = grouped_annotations1[type_name]

        if type_name not in grouped_annotations2 or len(grouped_annotations2[type_name]) == 0:
            evaluator.add_fp(len(annos_list_of_one_type))
            evaluator.append_fps(doc_name, annos_list_of_one_type)
            continue
        # we use interval tree to find the overlapped annotations
        # you can try using a similar compare method used in the strict match, but the logic will be way more
        # complicated to implement, when dealing with multiple to one or one to multiple overlaps.
        annos1_tree = build_interval_tree(annos_list_of_one_type)
        overlapped_ids = set()
        for anno2 in grouped_annotations2[type_name]:
            overlapped = annos1_tree[anno2.start_index:anno2.end_index]
            if len(overlapped) == 0:
                evaluator.add_fn()
                evaluator.append_fns(doc_name, [anno2])
            else:
                evaluator.add_tp()
                overlapped_ids.update([interval.data for interval in overlapped])
        # check what remains in anno1 = false positives
        remain_ids = [i for i in range(0, len(annos_list_of_one_type)) if i not in overlapped_ids]
        if len(remain_ids) > 0:
            evaluator.add_fp(len(remain_ids))
            evaluator.append_fps(doc_name, [annos_list_of_one_type[i] for i in remain_ids])

        # if doc_name in evaluator.fns:
        #     evaluator.fns[doc_name] = sorted(evaluator.fns[doc_name], key=lambda x: x.start_index)
        #
        # if doc_name in evaluator.fps:
        #     evaluator.fps[doc_name] = sorted(evaluator.fps[doc_name], key=lambda x: x.start_index)
    pass


def show_annotations(doc_annotations, doc_map, annotator_a, annotator_b, width=900, height=400):
    if len(doc_annotations) == 0:
        print('\tNo documents to display.')
        return
    div_config1 = '<div style="background-color:#f9f9f9;padding-left:10px;' \
                  'width: ' + str(width - 23) + 'px; ">'
    div_config2 = '<div style="background-color:#f9f9f9;padding:10px; ' \
                  'width: ' + str(width) + 'px; height: ' + str(height) + 'px; overflow-y: scroll;">'
    html = ["<html>", div_config1, "<table width=100% >",
            "<col style=\"width:25%\"><col style=\"width:75%\">", "</div>",
            "<tr><th style=\"text-align:center\">document name</th><th style=\"text-align:center\">Snippets</th></table></div>",
            div_config2,
            "<table width=100% ><col style=\"width:25%\"><col style=\"width:75%\">"]
    for doc_name, annotations in doc_annotations.items():
        html.extend(show_one_doc_annotations(doc_name, doc_map[doc_name], annotations, annotator_a, annotator_b))
    html.append("</table></div>")
    html.append("</html>")
    return display(HTML(''.join(html)))


def show_one_doc_annotations(doc_name, doc_text, annotations, annotator_a, annotator_b):
    from pyConTextNLP.display.html import __insert_color
    html = []
    color = 'blue'
    window_size = 50
    html.append("<tr>")
    html.append("<td style=\"text-align:left\">{0}</td>".format(doc_name))
    html.append(
        "<td><a href=\"https://brat.jupyter.med.utah.edu/diff.xhtml?diff=%2Fstudent_folders%2F" + annotator_a + "%2F#/student_folders/" + annotator_b + "/" + doc_name + "\" target=\"_blank\">document view</a></td>")
    html.append("</tr>")
    for anno in annotations:
        #           make sure the our snippet will be cut inside the text boundary
        begin = anno.start_index - window_size
        end = anno.end_index + window_size
        begin = begin if begin > 0 else 0
        end = end if end < len(doc_text) else len(doc_text)
        #           render a highlighted snippet
        cell = __insert_color(doc_text[begin:end], [anno.start_index - begin, anno.end_index - end], color)
        #           add the snippet into table
        html.append("<tr>")
        html.append("<td></td>")
        html.append("<td style=\"text-align:left\">{0}</td>".format(cell))
        html.append("</tr>")
    return html
