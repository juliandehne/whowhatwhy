import re

text = "@angeldruckt @TwraSun Ich fürchte, das muss man, und zwar sehr eingehend. Ekel mag dabei unvermeidbar sein"
# Remove all mentions (@...) from the text
text_without_mentions = re.sub(r'@\w+', '', text)

print(text_without_mentions)
