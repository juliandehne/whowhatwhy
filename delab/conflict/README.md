# Classifier for Moderation Context and Conflict Detection

The main idea is that there are different types of situations where moderation is needed:
- a relationship focused conflict may need mediation
- an issue focused conflict of interest may need arbitration
- moderation can only be found if there is a conflict (of opinion/interests/personalities/intended focus of attention)

# Approach

1. conflict labeling
- compute conversation triples (three subsequent replies)
- (optional) filter conversation triple by high toxicity (and low group adherence)
- present conversation triples  for labeling
- label if there is a conflict (between min two parties)
- label if the participants have adversarial positions (between min two parties)
- label if participant use arguments to support their position (between min two parties)
- label if the relationship between the participants plays a role (i.e. insults, group labeling)

2. conflict classification
- write a classifier that places triples in the field of relationship and interests
- measure accuracy

3. cross-validation with networks as proxy for group adherence and positions
- check if low group adherence can predict conflict
- check if high group adherence leads to low adversarial positions

4. write a prediction algorithm for moderation
- that places moderation as a bridge between high conflict queues of triples and low conflict queues of triples
5. write a moderation bot that uses context conflict type predictions to produce moderation, therapy, diplomacy or arbitration
