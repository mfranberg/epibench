import subprocess

class ClusterDispatcher:
    def num_cores(self):
        return 1

    def submit(self, cmd):
        subprocess.check_call( cmd )
