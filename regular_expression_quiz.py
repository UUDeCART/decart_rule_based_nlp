def which_a_string_not_matched(s):
	if not isinstance(s, str):
		return 'Please pass a string to this function.'
		
	if s == 'a':
		return 'The string "a" is the correct answer.  Since the function uses the + quantifier that means there must be at least one "h" character after an "a"'
	if 'a' not in s:
		return 'There should be at least one character "a" in your answer since the regular expression expects one "a"'
	else:
		return 'The + quantifier means that there will be one or more the character that it modifies to its left.  Please try again.'