import subprocess
import tempfile

def num_cores():
    return 2

def submit(cmd):
    SUBMIT_SCRIPT = "#!/bin/bash -l\n{0}\n"
    script_file, script_path = tempfile.mkstemp( )
    with open( script_path, "w" ) as script_file:
        script_file.write( SUBMIT_SCRIPT.format( " ".join( cmd ) ) )

    subprocess.check_call( [ "sbatch", script_path ] )
