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