import ipywidgets
from IPython.display import display,clear_output, HTML
from collections import OrderedDict
def single_choice(option_explanations, desc, func=None):
    opts=ipywidgets.RadioButtons(
        options=list(option_explanations.keys()),
        description=desc,
        layout=ipywidgets.Layout(width='600px')
    )

    button = ipywidgets.Button(description="Submit")
    def click(b):        
        clear_output(wait=True)
        if func is not None:
            display(func)
        display(HTML('<html><body><span style="color: green;">'+option_explanations[opts.value]+'<span></body></html>'))

    button.on_click(click)
    if func is not None:
        display(func)
        display(opts)
        display(button)
    else:
        display(opts)
        display(button)
    
def error_analyses_1():
    option_explanations=OrderedDict()
    option_explanations['Negative in both gold reference and your prediction']='The 3rd answer is correct.'
    option_explanations['Negative in gold reference, but positive in your prediction']='The 3rd answeris correct.'
    option_explanations['Positive in gold reference, but negative in your prediction']='Correct!'
    option_explanations['Positive in both gold reference and your prediction']='The 3rd answer is correct.'    
    single_choice(option_explanations,'False negative means:')
    
    
def error_analyses_2():
    option_explanations=OrderedDict()
    option_explanations['list']='<b>"list_false_negatives"</b> will return a dictionary, which keys are the document names and values are the annotated documents.'
    option_explanations['array']='<b>"list_false_negatives"</b> will return a dictionary, which keys are the document names and values are the annotated documents.'
    option_explanations['dictionary']='Correct!'
    single_choice(option_explanations,'Which is corret:',\
                 HTML('''<html><body>What type of data will be returned by the function <b>"list_false_negatives"</b>?</body></html>'''))
    
def error_analyses_3():
    option_explanations=OrderedDict()
    option_explanations['is']='This word is too general. You will likely get 100% recall, but very bad precision.'
    option_explanations['lobe']='Try again'
    option_explanations['patchy opacity']='This is a better answer'
    option_explanations['consolidation']='Correct'
    single_choice(option_explanations,'Choose best keyword:', HTML('''<html><body>If you see the following expert annotation in gold reference, but your KeywordClassifier predict the corresponding document as negative answer. Which keyword above is the best choice to add in your KeywordClassifier?<br/><br/>The mediastinal and hilar contours are
unremarkable. There is <span style="color: blue;">patchy opacity at the left lower lobe representing
either atelectasis or consolidation</span>. No definite free air is identified.</body></html>'''))    
    
def doc_classify_1():
    option_explanations=OrderedDict()
    option_explanations['A']='The last answer is correct.'
    option_explanations['B']='The last answer is correct.'
    option_explanations['C']='The last answer is correct.'
    option_explanations['D']='Correct!'
    single_choice(option_explanations,'Choose the best answer:',\
                 HTML('''<html><body>If you see a rule for the DocumentClassifier only has one item: <b>"indicate_pneumonia"</b>, what does this rule means?:
<ul>
  <li><b>A</b>: If find an annotation with type "indicate_pneumonia", conclude 1.</li>
  <li><b>B</b>: If find an annotation with any type, conclude "indicate_pneumonia".</li>
  <li><b>C</b>: No matter what, always conclude "indicate_pneumonia".</li>
  <li><b>D</b>: If no above rule is met, conclude "indicate_pneumonia".</li>
</ul>  
</body></html>'''))    

    
def doc_classify_2():
    option_explanations=OrderedDict()
    option_explanations['A']='The last answer is correct.'
    option_explanations['B']='The last answer is correct.'
    option_explanations['C']='This answer is good, but the last one is more precise.'
    option_explanations['D']='Correct!'
    single_choice(option_explanations,'Choose the best answer:',\
                 HTML('''<html><body>If you see a rule for the DocumentClassifier has two items: <b>"possible_diabetes,high_glucose_test"</b>, what does this rule means?:
<ul>
  <li><b>A</b>: If find a string "high_glucose_test" in the document, conclude "possible_diabetes".</li>
  <li><b>B</b>: If find an annotation with type "possible_diabetes", suggest "high_glucose_test".</li>
  <li><b>C</b>: If find an annotation with type "high_glucose_test", conclude "possible_diabetes".</li>
  <li><b>D</b>: If no above rule is met and find an annotation with type "high_glucose_test", conclude "indicate_pneumonia".</li>
</ul>  
</body></html>'''))
    
def doc_classify_3():
    option_explanations=OrderedDict()
    option_explanations['A']='The last answer is correct.'
    option_explanations['B']='The last answer is correct.'
    option_explanations['C']='Try again.'
    option_explanations['D']='Correct!'
    single_choice(option_explanations,'Choose the best answer:',\
                 HTML('''<html><body>If you see a feature inference rule: <b>"possible_anemia,anemia,probable_existence"</b>, what will this rule do?:
<ul>
  <li><b>A</b>: If find an annotation with type "anemia", conclude "possible_anemia".</li>
  <li><b>B</b>: If find an annotation with type "anemia", "definite_existence" or "probable_existence", conclude "possible_anemia".</li>
  <li><b>C</b>: If find an annotation with type "anemia" and with a modifier value either "definite_existence" or "probable_existence", conclude "possible_anemia".</li>
  <li><b>D</b>: If find an annotation that has type "anemia" and its modifier values include "probable_existence", conclude "possible_anemia".</li>
</ul>  
</body></html>'''))  
    
def error_analyses_7():
    option_explanations=OrderedDict()
    option_explanations['A']='Try again.'
    option_explanations['B']='Try again.'
    option_explanations['C']='Try again.'
    option_explanations['D']='Correct!'
    single_choice(option_explanations,'Choose the best answer:',\
                 HTML('''<html><body>When you doing error analyses, if you see following pyConText graph plot: <img src="images/Selection_008.png"> <br/> and following snippet:<img src="images/Selection_009.png">, what can you conclude?<br/>
<ul>
  <li><b>A</b>: This is a false positive error</li>
  <li><b>B</b>: This is a false negative error.</li>
  <li><b>C</b>: This is correct.</li>
  <li><b>D</b>: Not enough information to make a conclusion.</li>
</ul>  
</body></html>'''))      
    
def error_analyses_8():
    option_explanations=OrderedDict()
    option_explanations['A']='Try again.'
    option_explanations['B']='Try again.'
    option_explanations['C']='Please don\'t waste your time.'
    option_explanations['D']='Correct!'
    single_choice(option_explanations,'Choose the best answer:',\
                 HTML('''<html><body>In the question above, what may be the cause?<br/>
<ul>
  <li><b>A</b>: "AMBIVALENT_EXISTENCE" is excluded by DocumentClassifier</li>
  <li><b>B</b>: "INDICATION" is excluded by pyConText.</li>
  <li><b>C</b>: "pneumonia" is colored orange.</li>
  <li><b>D</b>: "man" should not be a "DEFINITE_NEGATED_EXISTENCE" clue.</li>
</ul>  
</body></html>'''))      
    
    
    
def error_analyses_9():
    option_explanations=OrderedDict()
    option_explanations['A']='Try again.'
    option_explanations['B']='Try again.'
    option_explanations['C']='Please don\'t waste your time.'
    option_explanations['D']='Correct!'
    single_choice(option_explanations,'Choose the best answer:',\
                 HTML('''<html><body>In the question above, what should we do next?<br/>
<ul>
  <li><b>A</b>: delete the rule that conclude "AMBIVALENT_EXISTENCE" as negative answer in our DocumentClassifier rule file</li>
  <li><b>B</b>: add "man" in our target rule file.</li>
  <li><b>C</b>: add "pneumonia" in our target rule file.</li>
  <li><b>D</b>: remove the rule like "man&nbsp;&nbsp;&nbsp;&nbsp;DEFINITE_NEGATED_EXISTENCE&nbsp;...." in our modifier rule file.</li>
</ul>  
</body></html>'''))      