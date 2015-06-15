'''
information.py
'''
__all__ = ['entropy', 'symbols_to_prob', 'combine_symbols', 'mi', 'cond_mi', 'mi_chain_rule']
import numpy as np
import pdb 

def entropy(data=None, prob=None, errorVal=1e-5):
    '''
    given a probability distribution (prob) or an interable of symbols (data) compute and
    return its entropy

    inputs:
    ------
        data:       iterable of symbols

        prob:       iterable with probabilities
        
        errorVal:   if prob is given, 'entropy' checks that the sum is about 1.
                    It raises an error if abs(sum(prob)-1) >= errorVal
    '''
    
    #pdb.set_trace()
    if prob is None and data is None:
        raise ValueError("%s.entropy requires either 'prob' or 'data' to be defined"%(__name__))

    if prob is not None and data is not None:
        raise ValueError("%s.entropy requires only 'prob' or 'data to be given but not both"%(__name__))

    if prob is not None and not isinstance(prob, np.ndarray):
        raise TypeError("'entropy' in '%s' needs 'prob' to be an ndarray"%(__name__)) 

    if prob is not None and abs(prob.sum()-1) > errorVal:
        raise ValueError("parameter 'prob' in '%s.entropy' should sum to 1"%(__name__))
    

    if data is not None:
        prob = symbols_to_prob(data)
    
    # compute the log2 of the probability and change any -inf by 0s
    logProb = np.log2(prob)
    logProb[logProb==-np.inf] = 0
    
    # return dot product of logProb and prob
    return -1.0* np.dot(prob, logProb)


def symbols_to_prob(symbols):
    '''
    Return the probability distribution of symbols. Only probabilities are returned and in random order, 
    you don't know what the probability of a given label is but this can be used to compute entropy

    input:
        symbols:     iterable of hashable items
                     works well if symbols is a zip of iterables
    '''
    from collections import Counter
    myCounter = Counter
    
    #pdb.set_trace()
    # count number of occurrances of each simbol in *argv (return as list of just the count)
    asList = list(myCounter(symbols).values())

    # total count of symbols; float to prevent integer division in next line
    N = np.float(sum(asList))

    return np.array([n/N for n in asList])

def combine_symbols(*args):
    '''
    Combine different symbols into a 'super'-symbol

    args can be an iterable of iterables that support hashing

    see example for 2D ndarray input
    
    usage:
        1) combine two symbols, each a number into just one symbol
        x = numpy.random.randint(0,4,1000)
        y = numpy.random.randint(0,2,1000)
        z = combine_symbols(x,y)

        2) combine a letter and a number
        s = 'abcd'
        x = numpy.random.randint(0,4,1000)
        y = [s[randint(4)] for i in range(1000)]
        z = combine_symbols(x,y)

        3) suppose you are running an experiment and for each sample, you measure 3 different
        properties and you put the data into a 2d ndarray such that:
            samples_N, properties_N = data.shape
        
        and you want to combine all 3 different properties into just 1 symbol
        In this case you have to find a way to impute each property as an independent array
            
            combined_symbol = combine_symbols(*data.T)

        
        4) if data from 3) is such that:
            properties_N, samples_N  = data.shape
        
        then run:

            combined_symbol = combine_symbols(*data)

    '''
    #pdb.set_trace()
    for arg in args:
        if len(arg)!=len(args[0]):
            raise ValueError("combine_symbols got inputs with different sizes")

    return tuple(zip(*args))


def mi(x, y):
    '''
    compute and return the mutual information between x and y
    
    inputs:
    -------
        x, y:   iterables of hashable items
    
    output:
    -------
        mi:     float

    Notes:
    ------
        if you are trying to mix several symbols together as in mi(x, (y0,y1,...)), try
                
        info[p] = _info.mi(x, info.combine_symbols(y0, y1, ...) )
    '''
    #pdb.set_trace()
    # dict.values() returns a view object that has to be converted to a list before being
    # converted to an array
    # the following lines will execute properly in python3, but not python2 because there
    # is no zip object
    try:
        if isinstance(x, zip):
            x = list(x)
        if isinstance(y, zip):
            y = list(y)
    except:
        pass

    probX = symbols_to_prob(x)
    probY = symbols_to_prob(y)
    probXY = symbols_to_prob(zip(x, y))

    return entropy(prob=probX) + entropy(prob=probY) - entropy(prob=probXY)

def cond_mi(x, y, z):
    '''
    compute and return the mutual information between x and y given z, I(x, y | z)
    
    inputs:
    -------
        x, y, z:   iterables with discrete symbols
    
    output:
    -------
        mi:     float

    implementation notes:
    ---------------------
        I(x, y | z) = H(x | z) - H(x | y, z)
                    = H(x, z) - H(z) - ( H(x, y, z) - H(y,z) )
                    = H(x, z) + H(y, z) - H(z) - H(x, y, z)
    '''
    #pdb.set_trace()
    # dict.values() returns a view object that has to be converted to a list before being converted to an array
    probXZ = symbols_to_prob(combine_symbols(x, z))
    probYZ = symbols_to_prob(combine_symbols(y, z))
    probXYZ =symbols_to_prob(combine_symbols(x, y, z))
    probZ = symbols_to_prob(z)

    return entropy(prob=probXZ) + entropy(prob=probYZ) - entropy(prob=probXYZ) - entropy(prob=probZ)

def mi_chain_rule(X, y):
    '''
    Decompose the information between all X and y according to the chain rule and return all the terms in the chain rule.
    
    Inputs:
    -------
        X:          iterable of iterables. You should be able to compute [mi(x, y) for x in X]

        y:          iterable of symbols

    output:
    -------
        ndarray:    terms of chaing rule

    Implemenation notes:
        I(X; y) = I(x0, x1, ..., xn; y)
                = I(x0; y) + I(x1;y | x0) + I(x2; y | x0, x1) + ... + I(xn; y | x0, x1, ..., xn-1)
    '''
    
    # allocate ndarray output
    chain = np.zeros(len(X))

    # first term in the expansion is not a conditional information, but the information between the first x and y
    chain[0] = mi(X[0], y)
    
    #pdb.set_trace()
    for i in range(1, len(X)):
        chain[i] = cond_mi(X[i], y, X[:i])
        
    return chain
    