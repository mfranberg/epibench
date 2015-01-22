import subprocess

class ClusterDispatcher:
    def __init__(self, param_str):
        self.ncores = int( param_str )

    def num_cores(self):
        return self.ncores

    def submit(self, cmd):
        subprocess.check_call( cmd )
