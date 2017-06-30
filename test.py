import re

x = 'abc7777777777788888888888888abcabc88888888abc'
y = re.sub('^abc', '', x)
print y