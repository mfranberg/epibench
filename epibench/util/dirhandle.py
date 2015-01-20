import os
import errno

def mkdir_p(path):
    try:
        os.makedirs( path )
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir( path ):
            pass
        else: raise

def setup_file(output_dir, subdir, result_file):
    output_subdir = os.path.join( output_dir, subdir )
    mkdir_p( output_subdir )
    
    return os.path.join( output_subdir, result_file )

def setup_dir(output_dir, subdir1, subdir2):
    output_subdir = os.path.join( output_dir, subdir1, subdir2 )
    mkdir_p( output_subdir )

    return output_subdir
