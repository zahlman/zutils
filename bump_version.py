import glob, string, subprocess, sys


PRERELEASE_ALLOWED = ''.join((
    string.ascii_uppercase, string.ascii_lowercase, string.digits, '.-'
))


def build_number():
    # Let the exception fall through if git is not available.
    return subprocess.check_output(
        ('git', 'rev-list', 'head', '--count')
    ).decode('utf-8').strip()


def parse_version(s):
    s, _,  build = s.partition('+')
    s, _, prerelease = s.partition('-')
    major, minor, patch = s.split('.')
    return int(major), int(minor), int(patch), prerelease, build


def format_version(major, minor, patch, prerelease, build):
    p = '-' if prerelease else ''
    b = '+' if build else ''
    return f'{major}.{minor}.{patch}{p}{prerelease}{b}{build}'


def bump(data, how, update_build):
    major, minor, patch, prerelease, build = data
    # If build numbers are used, update on every kind of bump.
    build = build_number() if update_build else ''
    if how == 'major':
        major, minor, patch, prerelease = major + 1, 0, 0, ''
    elif how == 'minor':
        minor, patch, prerelease = minor + 1, 0, ''
    elif how == 'patch':
        patch, prerelease = patch + 1, ''
    elif how == 'final':
        prerelease = '' # since we can't specify that directly
    elif how is not None:
        prerelease = ''.join(x for x in how if x in PRERELEASE_ALLOWED)
    return major, minor, patch, prerelease, build


# Look for a quoted string on a line that starts with the tag.
# A semver string can't contain quotes, so parsing is simple.
def get_version(filename, tag):
    with open(filename) as source:
        for line in source:
            if line.startswith(tag):
                return line.split('"')[1]
    return '0.1.0' # probably the most sensible default


# attempt to replace the version in the file. Very naive to contents.
def set_version(filename, tag, version):
    with open(filename) as source:
        data = [
            f'{tag} = "{version}"\n' if line.startswith(tag) else line
            for line in source 
        ]
    with open(filename, 'w') as dest:
        dest.writelines(data)


def update_version(bump_method, update_build):
    version_text = get_version('pyproject.toml', 'version')
    version = bump(parse_version(version_text), bump_method, update_build)
    version_text = format_version(*version)
    print(f'Updating to version {version_text}.')
    set_version('pyproject.toml', 'version', version_text)
    # recursively search, but ignore the current folder
    for src in glob.glob('**/*.py'):
        set_version(src, '__version__', version_text)


usage = [
    'usage:',
    '    bump_version major [nobuild]',
    '    -> updates to next major version and clears prerelease string.',
    '    bump_version minor [nobuild]',
    '    -> updates to next minor version and clears prerelease string.',
    '    bump_version patch [nobuild]',
    '    -> updates to next patch version and clears prerelease string.',
    '    bump_version final [nobuild]',
    '    -> clears prerelease string.',
    '    bump_version <prerelease> [nobuild]',
    '    -> updates to next major version and clears prerelease string.',
    '    bump_version nobuild',
    '    -> clears build number.',
    '    bump_version build',
    '    -> updates build number only.',
    'For commands other than `build`, if `nobuild` is specified,',
    'the build number will be cleared; otherwise, it is updated.',
    'Please see https://semver.org for more information.'
]


if __name__ == '__main__':
    try:
        progname, method, *nobuild = sys.argv
        if method == 'build':
            if nobuild:
                raise ValueError
            method, update_build = None, True
        elif method == 'nobuild':
            if nobuild:
                raise ValueError
            method, update_build = None, False
        elif nobuild == []:
            update_build = True
        elif nobuild == ['nobuild']:
            update_build = False
        else:
            raise ValueError
    except:
        print(*usage, sep='\n')
    else:
        update_version(method, update_build)
