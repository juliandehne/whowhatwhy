# Data format

- the data needs to lie in the folder mm as a File FunctionPhrases.csv
- the data needs to be comma seperated
- the cells are quoted with ""
- a longer string n-gram is marked with '' which will be recoded to "" after reading the csv for the api

# Mapping moderation

- find terms that reflect stepping out of the moderation
  - referencing the subreddit
  - referencing previous posts
  - using group references "we should", "you all are saying"
  - referencing the discussion "this discussion"
- find terms that reference moderating function
  - agenda control: stay on topic