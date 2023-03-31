import os
from git import Repo, NoSuchPathError


class GitRapper:
    def __init__(self):
        self.root = 'test_file_sys'
        self.repo = Repo(self.root)


def serialize_local_fs(root_path: str):
    # If path is not valid return an empty dictionary
    try:
        paths = os.listdir(root_path)
    except FileNotFoundError:
        return {}

    def serialize_recursive(sub_fs: dict, parent: list, curr_dirr: str):
        # No need for base case b/c recursion will not be called if len(dirs) = 0

        pwd = f'{"/".join(parent)}/{curr_dirr}' if len(parent) > 0 else curr_dirr
        paths = os.listdir(pwd)
        paths = [p for p in paths if p != ".git"]  # removes hidden folders
        files = [f for f in paths if os.path.isfile(f"{pwd}/{f}")]
        dirs = [d for d in paths if os.path.isdir(f"{pwd}/{d}")]

        parent.append(curr_dirr)
        sub_fs["files"] = files
        sub_fs["directories"] = {d: serialize_recursive({}, list(parent), d) for d in dirs}  # no base case

        return sub_fs

    file_system = {}
    return serialize_recursive(file_system, [], root_path)


def serialize_git_tree(root="test_file_sys"):
    # to set up for test until class is implemented
    try:
        mrrepo = Repo(root)
    except NoSuchPathError:
        return {}

    tree = mrrepo.tree()
    def serialize_recursive(sub_fs: dict , tree):
        sub_fs["files"] = [f.name for f in tree if f.type == 'blob']
        sub_fs["directories"] = {d.name: serialize_recursive({}, d) for d in tree if d.type == 'tree'}
        return sub_fs
    return serialize_recursive({}, tree)
