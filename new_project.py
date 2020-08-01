import os, string, subprocess, sys


ALLOWED = string.ascii_lowercase + '-_'
GOOD_START = tuple(string.ascii_lowercase)


PY_GITIGNORE = [
    '# Byte-compiled / optimized / DLL files',
    '__pycache__/',
    '*.py[cod]',
    '',
    '# gVim',
    '*.swp',
    '*~',
    '',
    '# pip',
    '*.egg-info'
]


# Things stored in `local/` will be ignored by git, while the main
# .gitignore doesn't need updating.
LOCAL_GITIGNORE = ['*']


def valid(name):
    return all(c in ALLOWED for c in name) and name.startswith(GOOD_START)


def cmd(*args, shell=False):
    try:
        subprocess.check_output(args, shell=shell)
        return True
    except subprocess.CalledProcessError:
        return False


def write(template, filename, *folders):
    path = os.path.join(*folders)
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, filename), 'w') as f:
        for line in template:
            f.write(line + '\n')


def main(projectname=None, *_):
    if projectname is None:
        projectname = input('Name of project: ')
    if not valid(projectname):
        print('Invalid project name. Aborting.')
        return
    if not cmd('poetry', 'new', projectname, shell=True):
        print('Poetry not available. Will attempt git setup anyway.')
    if not cmd('git', 'init', projectname):
        print('Git not available. Bailing out.')
        return
    write(PY_GITIGNORE, '.gitignore', projectname)
    write(LOCAL_GITIGNORE, '.gitignore', projectname, 'local')
    os.chdir(projectname)
    cmd('git', 'add', '.')
    cmd('git', 'commit', '-m', 'Initial commit')


if __name__ == '__main__':
    main(*sys.argv[1:])
