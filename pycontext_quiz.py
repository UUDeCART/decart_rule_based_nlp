def identify_target_category(s):
	if not isinstance(s, str):
		return 'Please pass a string to this function.'
		
	if s == 'PROFESSION':
		return 'CORRECT.  The string "PROFESSION" is the category in this case'
	elif 'doctor' in s:
		return 'INCORRECT.  It looks like you may have passed in either the regular form or the regular expression'
	else:
		return 'INCORRECT.  Please try again.  See the documentation above for pyConText itemData ordering'
		
def file_delimiter_quiz(s):
	if not isinstance(s, str):
		return 'Please pass a string to this function.'
		
	if s == '\t':
		return 'CORRECT.  Tab ("\t") is the default delimiter for pyConText files'
	elif s == ',':
		return 'INCORRECT. While commas are often used for delimiting, they can also be found in targets and modifiers so a different character is used'
	else:
		return 'INCORRECT.  Try again.  Open the file and look at it again.  What character does it look like?'
		
def modifier_directionality_quiz(s):
	if not isinstance(s, str):
		return 'Please pass a string to this function.'
		
	if s == 'backward':
		return 'CORRECT.  Since this will modifier targets before it, it would properly modify pnuemonia in the sentence : "Pneumonia was ruled out"'
	elif s == 'forward' or s == 'bidirectional':
		return 'INCORRECT.  Most grammar constructions would not be likely for a target to come after this modifier.  Does this sentence back sense ? "was ruled out pneumonia"'
	elif s == 'terminate':
		return 'INCORRECT.  This phrase does not seem to behave like a terminate.  It seems to change the status of some surrounding concepts'
	else:
		return 'INCORRECT.  It is not clear what you passed in.  Please see the list of possible answers'
		
def second_most_frequent_modifier_quiz(s):
	if not isinstance(s, str):
		return 'Please pass a string to this function.'
		
		
	if s == 'DEFINITE_NEGATED_EXISTENCE':
		return 'CORRECT.  There are a lot of modifiers to handle negated contexts'
	elif s in ['PROBABLE_NEGATED_EXISTENCE', 'PROBABLE_EXISTENCE', 'HISTORICAL']:
		return 'INCORRECT.  There are a lot of this category, but there is one that occurs more frequently'
	else:
		return 'INCORRECT.  Please try again with one of the options listed above'