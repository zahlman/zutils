# zutils

These are a couple of utilities I find useful for starting new Python projects
with Poetry and git. No installation is expected or required; just put this folder in a place where you keep other project folders.

## Dependencies

Git and Poetry need to be available, and `bump_version.py` uses the `toml` package to parse `pyproject.toml` (you should be quite familiar with this already if you are using Poetry). Otherwise only the standard library is used.

## `new_project.py`

To start a new project, run `zutils/new_project.py`.

You can optionally specify the new project name on the command line, or else
you will be prompted for it interactively. The script will:

* Use `poetry new <project name>` to create a new project folder.
* Set up a git repository in that folder (via `git init`).
* Set up an initial project-wide `.gitignore`, as well as a `local/` subdirectory with its own `.gitignore` that ignores everything. The idea is that you can keep private, project-related data in this folder (e.g., source code from another project used for reference, or temporary data for informal acceptance testing) without a record of its existence in the project .gitignore.
* Set up a `.local` directory with more useful tools (see below).
* Make an initial `git commit` with this content.

## The `.local` directory

The script `new_project.py` script will set up each new project with a `.local` folder that contains its own `.gitignore` that ignores all files in the directory. This way, there is no indication of the folder in your main `.gitignore`, and you have a place to put files relevant to the project that shouldn't be checked in to version control and which also aren't of relevance to other developers - for example, personal to-do notes, data for ad-hoc acceptance testing, etc. The folder is named with a leading `.` to "hide" it by default on Linux; this also makes it easy to ignore with other tools such as `find` or `wc`.

## Recommended `.bash_aliases` on Linux

On Linux, you may want to add these aliases to your `.bash_aliases` file:
```
# Activate the local venv, which is specially named/located.
alias activate-local="source .local/.venv/bin/activate"
```
If you prefer to set up a separate virtual environment per project, you can give it the same name in each new project and set it up within the `.local` directory. Then an alias like this will work globally for whichever project you're currently `cd`'d into.
```
# Run an acceptance test in the local private folder.
alias try-it="(cd .local/ && source run-acceptance-test)"
```
The provided `run-acceptance-test` is a stub file to write any script needed for ad-hoc acceptance testing of the project. It's intended to be sourced, so that the code runs in the currently active virtual environment. This alias allows for doing so while also avoiding the need to `cd` into the `.local` directory and back.

## `bump_version.py`

The `bump_version.py` script is a wrapper for `poetry version`. It accepts all the arguments that `poetry version` does, as well as `build` and `nobuild` flags (which can also be specified by themselves). This lets you add or remove a build identifier from the version number (by default, the old build string is kept if there was one, or left off if there wasn't). When a build identifier is added, it is determined as the total number of commits in the git repository (as computed by `git rev-list head --count`).

When the script is run, in addition to updating `pyproject.toml`, it will recursively search for lines starting with `__version__` in your `.py` source files, and replace them with `__version__ == <version number>`. This happens regardless of the arguments provided; you can run the script with no arguments to apply this fix without changing the version number.

Because the script wraps `poetry version`, it needs to be run from your project's root directory. Keeping it in the private `local/` directory created by `new_project.py` makes it easy to do this even without any installer for the scripts; just run e.g. `python -m local/bump_version.py`.
