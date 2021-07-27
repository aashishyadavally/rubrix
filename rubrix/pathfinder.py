from pathlib import Path


def get_root():
    """Returns the absolute path of the main directory

    Returns:
    --------
        root (pathlib.Path)
    """
    cwd = str(Path.cwd())
    root = Path(cwd[:cwd.find('rubrix')]) / 'rubrix'

    return root


def get(*args):
    """Returns path of the file, relative to the path of the main directory.
    It helps avoid relative paths, and path-related conflicts.

    Arguments:
    ----------
        *args:
            Folders/files in order of directory-structure.

    Returns:
    --------
        path (pathlib.Path)
            Absolute path based on the main directory.
    """
    path = get_root()

    for arg in args:
        path = path / arg

    return path
