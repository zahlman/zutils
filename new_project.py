#!/usr/bin/env python3
import os, shutil, string, subprocess, sys


HERE = os.path.split(os.path.abspath(__file__))[0]
ALLOWED = string.ascii_lowercase + '-_'
GOOD_START = tuple(string.ascii_lowercase)


def valid(name):
    return all(c in ALLOWED for c in name) and name.startswith(GOOD_START)


def cmd(*args, shell=False):
    try:
        subprocess.check_output(args, shell=shell)
        return True
    except subprocess.CalledProcessError:
        return False


def copy(srcname, *dstpath):
    os.makedirs(os.path.join(*dstpath[:-1]), exist_ok=True)
    shutil.copy(os.path.join(HERE, srcname), os.path.join(*dstpath))


def main(projectname=None, *_):
    if projectname is None:
        projectname = input('Name of project: ')
    if not valid(projectname):
        print('Invalid project name. Aborting.')
        return
    # On Windows, `shell=True` is necessary because it's a batch script.
    # On Linux, not only is that not apparently necessary for shell scripts,
    # but it messes up when the input is pre-tokenized.
    if not cmd('poetry', 'new', projectname, shell=(os.name == 'nt')):
        print('Poetry not available, or project already exists. Aborting.')
        return
    if not cmd('git', 'init', projectname):
        print('Git not available. Aborting.')
        return
    copy('py_gitignore.txt', projectname, '.gitignore')
    copy('local_gitignore.txt', projectname, '.local', '.gitignore')
    # A blank script that can be configured later for acceptance testing.
    copy('run-acceptance-test', projectname, '.local', 'run-acceptance-test')
    copy('bump_version.py', projectname, '.local', 'bump_version.py')
    os.chdir(projectname)
    cmd('git', 'add', '.')
    cmd('git', 'commit', '-m', 'Initial commit')


if __name__ == '__main__':
    main(*sys.argv[1:])
