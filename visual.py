import ipywidgets
from IPython.display import display, HTML
import csv
import matplotlib
import pandas as pd
import json
import math
from pyConTextNLP.utils import get_document_markups

from itemData import get_item_data


# convert a document markups into dataframes
def convertMarkups2DF(markups, annotations=None, relations=None, filter_no_markup_txt=True):
    if annotations is None:
        annotations = pd.DataFrame(columns=['markup_id', 'vis_category', 'start', 'end', 'txt', 'type'])
    if relations is None:
        relations = pd.DataFrame(columns=['relation_id', 'type', 'arg1_cate', 'arg1_id', 'arg2_cate', 'arg2_id'])
    node_dic = dict()
    doc_txt = ''
    for markup in markups:
        txt = markup.graph['__txt']
        offset = len(doc_txt)
        if len(markup) > 0:
            annotations, relations = convertMarkup2DF(markup, offset, annotations, relations, node_dic)
        if (not filter_no_markup_txt) or len(markup) > 0:
            doc_txt += '\n' + txt
    return annotations, relations, doc_txt


# convert a snippet markups into dataframes
def convertMarkup2DF(markup, offset=0, annotations=None, relations=None, node_dic=dict()):
    if annotations is None:
        annotations = pd.DataFrame(columns=['markup_id', 'vis_category', 'start', 'end', 'txt', 'type'])
    if relations is None:
        relations = pd.DataFrame(columns=['relation_id', 'type', 'arg1_cate', 'arg1_id', 'arg2_cate', 'arg2_id'])
    for node in markup.nodes():
        add_node(node_dic, annotations, node, offset, markup.graph['__txt'])

    for e in markup.edges():
        modifier_type = e[0].getConTextCategory().title()
        target_type = e[1].getConTextCategory().title()
        if target_type == 'Modifier':
            modifier_type = 'Termination'

        add_node(node_dic, annotations, e[0], offset, markup.graph['__txt'])
        add_node(node_dic, annotations, e[1], offset, markup.graph['__txt'])

        modifier_id = node_dic[gen_doc_node_id(e[0], offset)]
        target_id = node_dic[gen_doc_node_id(e[1], offset)]

        annotations.loc[modifier_id, 'vis_category'] = modifier_type

        # put the modifier's name on the edge rather than the context clue's markup
        # annotations.loc[modifier_id, 'type'] = 'Modifier'

        relation_id = len(relations)
        relations.loc[relation_id] = ['R' + str(relation_id), e[0].getCategory()[0],
                                      modifier_type, 'T' + str(modifier_id),
                                      target_type, 'T' + str(target_id)]
    return annotations, relations


def gen_doc_node_id(node, offset):
    return str(node.getTagID()) + str(node.getSpan()[0] + offset)


def add_node(node_dic, annotations_df, node, offset, txt):
    origin_id = gen_doc_node_id(node, offset)
    if origin_id not in node_dic:
        node_id = len(node_dic)
        markup_id = 'T' + str(node_id)
        node_dic[origin_id] = node_id
        type = node.getCategory().pop()
        category = node.getConTextCategory().title()
        annotations_df.loc[node_id] = [markup_id, category, node.getSpan()[0] + offset, node.getSpan()[1] + offset,
                                       txt[node.getSpan()[0]:node.getSpan()[1]], type]
    pass


class Vis():
    def __init__(self, context_file='KB/pneumonia_modifiers.tsv', lib_dir='',
                 file_name="x.html", tmp_dir='tmp/'):
        self.relation_def = self.read_context_types(context_file)
        self.file_name = file_name
        self.tmp_dir = tmp_dir
        self.template = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
            <html>
            
            <head>
                <meta http-equiv="content-type" content="text/html; charset=UTF-8">
                <title>Brat Embedding {file_name}</title>
                <link rel="stylesheet" type="text/css" href="{lib_dir}css/style-vis.css">
                <script type="text/javascript" src="{lib_dir}js/head.js"></script>
                <script type="text/javascript">
              function resizeIframe(obj) {
                obj.style.height = obj.contentWindow.document.body.scrollHeight + 'px';
              }
            </script>
            </head>
            
            <body>
            
            <!-- load all the libraries upfront, which takes forever. -->
            <script type="text/javascript" src="{lib_dir}js/brat_loader.js"></script>
            
            <script type="text/javascript">
            
            var collData = {
                entity_types: [ {
                        type   : 'Target',
                        labels : ['Target', 'Tar'],
                        // Blue is a nice colour for a person?
                        bgColor: '#7fa2ff',
                        // Use a slightly darker version of the bgColor for the border
                        borderColor: 'darken'
                },
                 {
                        type   : 'Modifier',
                        labels : ['Modifier', 'Mod'],
                        // Blue is a nice colour for a person?
                        bgColor: 'lightgreen',
                        // Use a slightly darker version of the bgColor for the border
                        borderColor: 'darken'
                },
                 {
                        type   : 'Termination',
                        labels : ['Termination', 'Termi'],
                        // Blue is a nice colour for a person?
                        bgColor: 'orange',
                        // Use a slightly darker version of the bgColor for the border
                        borderColor: 'darken'
                }]
            };
            
            {relationship}
            
            {docData}
            
            </script>
            <p>Rendering: {file_name} ...</p>
            <div id="embedding-entity-example"></div>
            <script type="text/javascript">
                head.ready(function() {
                    Util.embed('embedding-entity-example', $.extend({}, collData),
                            $.extend({}, docData), webFontURLs);
                });
            </script>
            
            </body>
            </html>
            '''
        self.template = self.template.replace('{lib_dir}', lib_dir)
        self.template = self.template.replace('{relationship}', self.relation_def)
        pass

    # read modifier types from context file, generate relation definition variable collData['relation_types'] for Brat
    def read_context_types(self, context_file):
        context_types = set()
        for context_item in get_item_data(context_file):
            for type in context_item.getCategory():
                context_types.add(type)
        return self.gen_relation_def(context_types)

    # from a list of type names, generate relation definition variable collData['relation_types'] for Brat
    def gen_relation_def(self, context_types):
        relation_temp = '''{
                type     : '{type}',
                labels   : ['{type}', '{abb}'],
                color    : '{color}',
                args     : [
                    {role: 'Modifier', targets: ['Modifier'] },
                    {role: 'Target',  targets: ['Target'] } 
                ]
            }'''
        # use '{type}_t' to differentiate the type definition. At js data generation stage, this will
        # be done in function serialize_to_js
        term_temp = '''{
                type     : '{type}_t',
                labels   : ['{type}', '{abb}'],
                color    : '{color}',
                args     : [
                    {role: 'Termination', targets: ['Termination'] },
                    {role: 'Modifier',  targets: ['Modifier'] } 
                ]
            }'''

        colors = set()
        # use matplotlib colors
        for name, hex in matplotlib.colors.cnames.items():
            hex_str = str(hex)
            # exclude too bright colors
            if self.luminance(hex_str) < 180:
                colors.add(str(hex_str))
        header = "collData['relation_types'] = [ "
        ender = "];"
        elements = []
        for type in context_types:
            color = colors.pop()
            abb = type[:3]
            if '_' in type:
                abb = ''.join(token[:1] for token in type.split('_'))
            ele = relation_temp.replace('{type}', type) \
                .replace('{abb}', abb) \
                .replace('{color}', color)
            elements.append(ele)
            # re-drawing termination terms
            color = colors.pop()
            ele = term_temp.replace('{type}', type) \
                .replace('{abb}', abb) \
                .replace('{color}', color)
            elements.append(ele)
        defs = header + ','.join(elements) + ender
        return defs

    # compute the luminance
    def luminance(self, hex):
        rgb = self.hex2rgb(hex)
        return (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])

    # convert hex to rgb
    def hex2rgb(self, hex):
        h = hex.lstrip('#')
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    def visualize_context_graph(self, context_document):
        html, doctxt, total_annotations = self.gen_html_from_context_doc(context_document)
        self.write_html(html)
        html = '''
		      <iframe src = "{file_loc}" frameborder="0" width = "855" height = "150">
		         Sorry your browser does not support inline frames.
		      </iframe>'''.replace('{file_loc}', self.tmp_dir + self.file_name)
        display(HTML(html))
        pass

    def visualize_dfs(self, txt, markups, relations):
        html = self.gen_html_from_dfs(txt, markups, relations)
        self.write_html(html)
        html = '''<iframe src = "{file_loc}" frameborder="0" width = "855" height = "150">
				Sorry your browser does not support inline frames.
				</iframe>'''.replace('{file_loc}', self.tmp_dir + self.file_name)
        display(HTML(html))
        pass

    def write_html(self, html, file_name=None):
        if file_name is None:
            file_name = self.file_name
        f = open(self.tmp_dir + file_name, "w")
        f.write(html.replace('{file_name}', file_name))
        f.close()
        pass

    def gen_html_from_context_doc(self, doc, filter_no_markup_txt=True):
        annotations, relations, doc_txt = convertMarkups2DF(get_document_markups(doc))
        html = self.gen_html_from_dfs(doc_txt[1:], annotations, relations)
        return html, doc_txt, len(annotations)

    def gen_html_from_context_markup(self, markup):
        txt = markup.graph['__txt']
        annotations, relations = convertMarkup2DF(markup)
        html = self.gen_html_from_dfs(txt, annotations, relations)
        return html

    def gen_html_from_dfs(self, txt, annotations_df, relations_df):
        docData = self.serialize_to_js(txt, annotations_df, relations_df)
        html = self.template.replace('{docData}', 'var docData=' + docData)
        return html

    def serialize_to_js(self, txt, annotations_df, relations_df):
        entities = []
        for key, e in annotations_df.iterrows():
            entities.append([e['markup_id'], e['vis_category'], [[e['start'], e['end']]]])
        # ['R1', 'Anaphora', [['Anaphor', 'T2'], ['Entity', 'T1']]]
        relations = []
        for key, r in relations_df.iterrows():
            relation_type = r['type']
            if r['arg1_cate'] == 'Termination':
                relation_type += '_t'
            relations.append([r['relation_id'], relation_type, [
                [r['arg1_cate'], r['arg1_id']],
                [r['arg2_cate'], r['arg2_id']]
            ]])
        doc_data = {'text': txt, 'entities': entities, 'relations': relations}
        json_data = json.dumps(doc_data)
        return json_data


# viz = Vis('KB/fam_modifiers.tsv')
# print(viz.template)

def snippets_markup(annotated_doc_map, display_types={'EVIDENCE_OF_PNEUMONIA'}, width=900, height=400):
    if len(annotated_doc_map) == 0:
        print('No documents to display.')
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
    for doc_name, anno_doc in annotated_doc_map.items():
        html.extend(snippet_markup(doc_name, anno_doc, display_types))
    html.append("</table></div>")
    html.append("</html>")
    return ''.join(html)


def snippet_markup(doc_name, anno_doc, display_types={'EVIDENCE_OF_PNEUMONIA'}):
    from pyConTextNLP.display.html import __sort_by_span
    from pyConTextNLP.display.html import __insert_color
    html = []
    color = 'blue'
    window_size = 50
    html.append("<tr>")
    html.append("<td style=\"text-align:left\">{0}</td>".format(doc_name))
    html.append("<td></td>")
    html.append("</tr>")
    for anno in anno_doc.annotations:
        if anno.type in display_types:
            #           make sure the our snippet will be cut inside the text boundary
            begin = anno.start_index - window_size
            end = anno.end_index + window_size
            begin = begin if begin > 0 else 0
            end = end if end < len(anno_doc.text) else len(anno_doc.text)
            #           render a highlighted snippet
            cell = __insert_color(anno_doc.text[begin:end], [anno.start_index - begin, anno.end_index - end], color)
            #           add the snippet into table
            html.append("<tr>")
            html.append("<td></td>")
            html.append("<td style=\"text-align:left\">{0}</td>".format(cell))
            html.append("</tr>")
    return html


def view_pycontext_output(input, vis=Vis()):
    if input is None:
        print('No markups to display.')
        return
    if isinstance(input, dict):
        view_pycontext_outputs(input, vis)
    else:
        view_pycontext_single_output(input, vis)


def view_pycontext_outputs(processed_docs, vis=Vis()):
    doc_names = []
    docs_text = {}
    annotation_counts = {}
    if len(processed_docs) == 0:
        print('No documents to view.')
        return

    for doc_name, doc in processed_docs.items():
        html, doc_text, total_annotations = vis.gen_html_from_context_doc(doc)
        docs_text[doc_name] = doc_text
        annotation_counts[doc_name] = total_annotations
        vis.write_html(html, doc_name + '.html')
        doc_names.append(doc_name)

    @ipywidgets.interact(i=ipywidgets.IntSlider(min=0, max=len(doc_names) - 1))
    def _view_markup(i):
        doc_name = doc_names[i]
        text = docs_text[doc_name]
        total_annotations = annotation_counts[doc_name]
        html = '''
		      <iframe src = "tmp/{}.html" frameborder="0" width = "850" height = "{}">
		         Sorry your browser does not support inline frames.
		      </iframe>'''.format(doc_name, estimate_page_height(text, total_annotations))
        display(HTML(html))

    pass


def view_pycontext_single_output(processed_doc, vis=Vis()):
    html, doc_text, total_annotations = vis.gen_html_from_context_doc(processed_doc)
    vis.write_html(html, 'x.html')
    html = '''
			      <iframe src = "tmp/x.html" frameborder="0" width = "850" height = "{}">
			         Sorry your browser does not support inline frames.
			      </iframe>'''.format(estimate_page_height(doc_text, total_annotations))
    display(HTML(html))


def estimate_page_height(text, total_annotations):
    counter = 0
    for line in text.split('\n'):
        wrapped = math.ceil(len(line) / 150)
        counter = counter + 1 if wrapped == 0 else counter + wrapped
    res = counter * 25 + total_annotations * 35 + 20
    # print(str(counter)+'* 25+'+str(total_annotations)+'*35='+str(res))
    return res


def display_doc_text(docs, height=300):
    doc_names = list(docs.keys())

    @ipywidgets.interact(i=ipywidgets.IntSlider(min=0, max=len(doc_names) - 1))
    def _view_markup(i):
        doc_name = doc_names[i]
        print("document name: " + doc_name)
        text = docs[doc_name].text.strip().replace('\\s*\\n\\s*(\\s*\\n\\s*)+', '\n\n').replace('\n', '<br/>')
        scrollPrint(text, height)

    pass


def scrollPrint(txt, height=300):
    html = []
    html.append('<div style=" height: ' + str(height) + 'px; overflow-y: scroll;">')
    if isinstance(txt, str):
        html.append(txt.replace('\n', '<br/>'))
    elif isinstance(txt, list):
        html.extend(txt)
    html.append('</div>')
    display(HTML(''.join(html)))
