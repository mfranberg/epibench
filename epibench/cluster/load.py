import imp

def load_cluster(path):
    print path
    mod = imp.load_source( "cluster", path )

    assert mod.num_cores != None
    assert mod.submit != None


    return mod
