"""
the idea here is to establish a baseline what to measure the author presence measures against.
- a simple probability distribution of having seen a tweet based on reply distance and root distance
- both reply and root distance prob should start with 1 and decrease by half each step, vision prob is the means between
  the two measurements. Experiment with an alpha between 0.1 and 0.3 that is distracted from the original root distance score (1)
- not sure about the time delta influence (or whether it should be included),
    maybe normalize time delta and multiply it given factor beta. Choose beta so that it does not change the order of
    reply or root hierarchy influences
"""