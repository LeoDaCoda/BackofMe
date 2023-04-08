import os
from git import Repo, NoSuchPathError
import sys



class GitRapper:
    def __init__(self, root='test_file_sys'):
        self.root = root
        if not os.path.exists(self.root):
            raise FileNotFoundError
        self.repo = Repo(self.root)  # will raise git.NoSuchPathError if given invalid path
        # self.remote = self.repo.re
        # if self.repo.remotes:
        #     self.remote = None
        # else:
        #     self.remote = self.repo.

    def serialize_local_fs(self):
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
        return serialize_recursive(file_system, [], self.root)

    def serialize_git_tree(self) -> dict:
        tree = self.repo.tree()

        def serialize_recursive(sub_fs: dict, tree):
            sub_fs["files"] = [f.name for f in tree if f.type == 'blob']
            sub_fs["directories"] = {d.name: serialize_recursive({}, d) for d in tree if d.type == 'tree'}
            return sub_fs

        return serialize_recursive({}, tree)

    def get_file_versions(self, path: str) -> tuple:
        commits = self.repo.iter_commits('--all', max_count=100, paths=path)
        return tuple(str(c) for c in commits)

    def cat_file_version(self, path: str, commit_id: str) -> str:
        target = self.repo.commit(commit_id).tree[path]
        return target.data_stream.read().decode()

    def add_changes_to_commit(self, paths: list) -> bool:
        if not isinstance(paths, list):
            raise TypeError("Expected a list")
        try:
            self.repo.index.add(paths)
        except FileNotFoundError:
            return False
        return True

    def save_state(self, commit_message):
        self.repo.index.commit(commit_message)





