from itertools import izip_longest, product

def grouper(n, iterable, fillvalue=None):
    args = [iter(iterable)] * n

    if fillvalue:
        return izip_longest(fillvalue=fillvalue, *args)
    else:
        return map( lambda x: filter( lambda y: y != None, x ), izip_longest( fillvalue=None, *args ) )
    
