import re

def which_a_string_not_matched(s):
	if not isinstance(s, str):
		return 'Please pass a string to this function.'
		
	if s == 'a':
		return 'The string "a" is the correct answer.  Since the function uses the + quantifier that means there must be at least one "h" character after an "a"'
	if 'a' not in s:
		return 'There should be at least one character "a" in your answer since the regular expression expects one "a"'
	else:
		return 'The + quantifier means that there will be one or more the character that it modifies to its left.  Please try again.'
		
def test_infiltrates_expression(s):

	if not isinstance(s, str):
		return 'Please pass a string for a regular expression to this function.'
		

	expected_matches = ['infiltrate', 'infiltrates']
	unexpected_matches = ['infiltrat', 'infiltratess']
	
	for expected in expected_matches:
		matches = re.findall(s, expected)
		if len(matches) == 0:
			return 'INCORRECT.  Your expression failed to match the string [{0}].  Please try again.'.format(expected)
			
	for unexpected in unexpected_matches:
		matches = re.findall(s, unexpected)
		if len(matches) > 0:
			return 'INCORRECT.  Your expression matched an unexpected string : [{0}].  Please try again.'.format(unexpected)
			
	if '?' not in s:
		return 'Hmmm... While not required, your expression did not use a "?".  Please try using a regular expression which the special character "?" which will help in this task'
			
	return 'CORRECT.  Your expression seemed to match expected results.'