from constraint import *

possible_conversations = list(range(100000))
# print(possible_conversations)

problem = Problem()
problem.addVariable("c", possible_conversations)
problem.addVariable("m", list(range(10000)))
problem.addVariable("d", list(range(20)))
problem.addVariable("h", [1, 2, 3])
problem.addVariable("s", list(range(200)))

# von 10 Konversationen sind etwa 2 moderationsbedürftig
problem.addConstraint(lambda c, m: c / 5 == m, ("c", "m"))
# maximal drei Monate
problem.addConstraint(lambda d: d < 100, ("d",))
# maximal 500 Studierende
problem.addConstraint(lambda s: s < 500, ("s",))
# mindestens 500 moderierende Beiträge
problem.addConstraint(lambda m: m > 500, ("m",))
# maximal 200 downloadable conversations pro Tag (reddit 2x 50, mastodon 2*50)
problem.addConstraint(lambda d, c: d * 200 == c, ("d", "c"))
# studis annotieren 20 Conversationen in einer Stunde
problem.addConstraint(lambda c, h, d, s: c == h * d * s * 20, ("c", "h", "d", "s"))
# die Kosten sind
problem.addConstraint(lambda h, s, d: h * s * d * 12 < 12000, ("h", "s", "d"))
# problem.addConstraint(MinSumConstraint(), ("d", "c"))
print(problem.getSolutions())
