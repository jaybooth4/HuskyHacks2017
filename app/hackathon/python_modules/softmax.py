import math

vals = [1.2,1.6,1.5]

def recip(x): return 1.0/x

def softmax(scores):
    denom = sum(list(map(lambda x: math.exp(x), scores)))
    return [x/denom for x in list(map(lambda x: math.exp(x), scores))]


print softmax(list(map(recip, vals)))
