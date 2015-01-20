from itertools import izip_longest, product

def grouper(n, iterable, fillvalue=None):
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)
