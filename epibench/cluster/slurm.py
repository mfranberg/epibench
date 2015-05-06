import subprocess
import tempfile

class ClusterDispatcher:
    def __init__(self, params):
        param_list = params.strip( ).split( )
        self.ncores = int( param_list[ 0 ] )

        self.sbatch_params = [ ]
        if len( param_list ) > 1:
            self.sbatch_params = param_list[ 1: ]

    def num_cores(self):
        return self.ncores

    def submit(self, cmd):
        SUBMIT_SCRIPT = "#!/bin/bash -l\n{0}\n"
        script_file, script_path = tempfile.mkstemp( )
        with open( script_path, "w" ) as script_file:
            script_file.write( SUBMIT_SCRIPT.format( " ".join( cmd ) ) )
        
        cmd = [ "sbatch" ]
        cmd.extend( self.sbatch_params )
        cmd.append( script_path )

        subprocess.check_call( cmd )
