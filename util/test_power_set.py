from abusing_lists import powerset

l = [1, 2, 3, 4, 5, 6, 7, 8]
sets = powerset(l)
for set in list(sets):
    print(set)
