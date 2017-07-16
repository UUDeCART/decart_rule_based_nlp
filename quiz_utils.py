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
        print(option_explanations[opts.value])

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
    option_explanations['list']='"list_false_negatives" will return a dictionary, which keys are the document names and values are the annotated documents.'
    option_explanations['array']='"list_false_negatives" will return a dictionary, which keys are the document names and values are the annotated documents.'
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
    
    
    
    