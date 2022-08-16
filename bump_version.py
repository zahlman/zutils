#!/usr/bin/env python3
import glob, string, subprocess, sys
import toml


def get_build():
    return subprocess.check_output(
        ('git', 'rev-list', 'head', '--count')
    ).decode('utf-8').strip()


def poetry_version(rule):
    return subprocess.check_output(
        ('poetry', 'version', rule), shell=True
    ).decode('utf-8').split()[-1]


def fix_toml(version):
    with open('pyproject.toml') as src:
        data = toml.load(src)
    data['tool']['poetry']['version'] = version
    with open('pyproject.toml', 'w') as dest:
        toml.dump(data, dest)


# attempt to replace assignments to __version__ in the source file.
def set_version(filename, version_text):
    with open(filename) as source:
        data = [
            f'__version__ = "{version_text}"\n'
            if line.startswith('__version__')
            else line
            for line in source
        ]
    with open(filename, 'w') as dest:
        dest.writelines(data)


def update_version(bump_method, update_build):
    with open('pyproject.toml') as src:
        old_version = toml.load(src)['tool']['poetry']['version']
    old_version, old_plus, old_build = old_version.partition('+')
    if not bump_method:
        new_version, plus, build = old_version, old_plus, old_build
    else:
        try:
            new_version = poetry_version(bump_method)
            new_version, plus, build = new_version.partition('+')
        except subprocess.CalledProcessError:
            print('Failed.')
            return
    if update_build == 'build':
        plus, build = '+', get_build()
    elif update_build == '':
        plus, build = old_plus, old_build
    # if update_build == 'nobuild', the build was already stripped by Poetry.
    fixed_version = f'{new_version}{plus}{build}'
    if fixed_version != new_version:
        fix_toml(fixed_version)
    # recursively search, but ignore the current folder
    for src in glob.glob('**/*.py'):
        set_version(src, fixed_version)
    return fixed_version


usage = [
    'usage: bump_version [<version>] [build | nobuild]',
    '',
    'Invokes `poetry version <version>` (if specified), then cleans up.',
    'If `build` is specified and there is no build string, one is added;',
    'if `nobuild` is specified, any existing build string is removed;',
    'otherwise, the previous build string (if any) is preserved.',
    'All source files are searched for lines that start with `__version__`',
    'and these are replaced with an assignment of the new version string.'
]


def _is_build_arg(arg):
    return arg in {'build', 'nobuild'}


if __name__ == '__main__':
    try:
        program, *args = sys.argv
        if len(args) > 2:
            raise ValueError # extra args
        elif len(args) == 2:
            version, build = args
            if not _is_build_arg(build):
                raise ValueError
        elif len(args) == 1:
            arg = args[0]
            version, build = ('', arg) if _is_build_arg(arg) else (arg, '')
        else:
            assert len(args) == 0
            version, build = '', ''
    except:
        print(*usage, sep='\n')
    else:
        result = update_version(version, build)
        print(f'Version is now {result}.')
        print('You may want to `git add .` and `git commit --amend`')
        print('the changes, if any. Also consider making a tag.')
