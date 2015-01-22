import imp

def load_cluster(cluster_arg):
    path = cluster_arg[ 0 ]
    param_str = cluster_arg[ 1 ]

    mod = imp.load_source( "cluster", path )

    return mod.ClusterDispatcher( param_str )
