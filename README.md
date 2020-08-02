These are a couple of utilities I find useful for starting new Python projects
with Poetry and git. No installation is expected or required; just put this folder in a place where you keep other project folders.

# Dependencies

Git and Poetry need to be available, and `bump_version.py` uses the `toml` package to parse `pyproject.toml` (you should be quite familiar with this already if you are using Poetry). Otherwise only the standard library is used.

# `new_project.py`

To start a new project, run `zutils/new_project.py`.

You can optionally specify the new project name on the command line, or else
you will be prompted for it interactively. The script will:

* Use `poetry new <project name>` to create a new project folder.
* Set up a git repository in that folder (via `git init`).
* Set up an initial project-wide `.gitignore`, as well as a `local/` subdirectory with its own `.gitignore` that ignores everything. The idea is that you can keep private, project-related data in this folder (e.g., source code from another project used for reference, or temporary data for informal acceptance testing) without a record of its existence in the project .gitignore.
* Copy `bump_version.py` to the `local/` folder (making it easier to use).
* Make an initial `git commit` with this content.


# `bump_version.py`

The `bump_version.py` script is a wrapper for `poetry version`. It accepts all the arguments that `poetry version` does, as well as `build` and `nobuild` flags (which can also be specified by themselves`. This lets you add or remove a build identifier from the version number (by default, the old build string is kept if there was one, or left off if there wasn't). When a build identifier is added, it is determined as the total number of commits in the git repository (as computed by `git rev-list head --count`).

When the script is run, in addition to updating `pyproject.toml`, it will recursively search for lines starting with `__version__` in your `.py` source files, and replace them with `__version__ == <version number>`. This happens regardless of the arguments provided; you can run the script with no arguments to apply this fix without changing the version number.

Because the script wraps `poetry version`, it needs to be run from your project's root directory. Keeping it in the private `local/` directory created by `new_project.py` makes it easy to do this even without any installer for the scripts; just run e.g. `python -m local/bump_version.py`.
