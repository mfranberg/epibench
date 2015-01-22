import subprocess

def num_cores():
    return 2

def submit(cmd):
    subprocess.check_call( cmd )
