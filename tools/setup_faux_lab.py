"""Install the official local runner in a project venv and initialise its managed SDK.

This is local setup only. It never authenticates or submits to the platform.
The official CLI downloads WASI SDK, CMake and Ninja; internet access is required.
"""
from pathlib import Path
import os
import subprocess
import venv
ROOT=Path(__file__).resolve().parents[1]
env=ROOT/'.venv-faux'
venv.EnvBuilder(with_pip=True).create(env)
bin_dir=env/('Scripts' if os.name=='nt' else 'bin')
python=bin_dir/('python.exe' if os.name=='nt' else 'python')
cli=bin_dir/('cambc.exe' if os.name=='nt' else 'cambc')
subprocess.run([str(python),'-m','pip','install','-r',str(ROOT/'requirements-faux-lab.txt')],check=True)
subprocess.run([str(cli),'init','--yes',str(ROOT)],check=True,
               env=dict(os.environ,CAMBC_CACHE=str(ROOT/'.engine-cache')))
print('Local runner:',cli)
