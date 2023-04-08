import os
import shutil
from git import InvalidGitRepositoryError, Repo, NoSuchPathError, GitCommandError


class Backup:
    def __init__(self, root='test_file_sys', remote_path=None):
        """
        Initialize a Backup object, setting the root directory and creating a Repo object if it's a valid git repository.
        :param root: The root directory for the backup operations. Defaults to the current working directory.
        :type root: str, optional
        :raises FileNotFoundError: If the specified root directory doesn't exist.
        """
        self.remote_path = remote_path
        if not root:
            self.root = os.getcwd()
        else:
            self.root = root
        if not os.path.exists(self.root):
            raise FileNotFoundError
        try:
            self.repo = Repo(self.root)  # will raise git.NoSuchPathError if given invalid path
            self.remote = self.repo.remote('usb')
        except InvalidGitRepositoryError:
            self.repo = None
        except ValueError:
            self.remote = None

    def init_git_repo(self):
        """
        Initialize a new git repository in the root directory if it's not already a git repository.
        :return: A message indicating the result of the operation.
        :rtype: str
        """
        if self.repo:
            return "This directory is already a git repository."
        else:
            try:
                new_repo = Repo.init(self.root)
                self.repo = new_repo  # Update self.repo with the newly created repository
                return f"A new git repository has been initialized at {self.root}."
            except GitCommandError:
                return "An error occurred while initializing the git repository."

    def add_remote(self):
        pass

    def get_serialized_local(self):
        """
        Serialize the local file system, excluding hidden folders.
        :return: A dictionary representing the serialized file system.
        :rtype: dict
        """

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

    def get_serialized_git(self):
        """
        Serialize the git repository file system.
        :return: A dictionary representing the serialized git repository, or an error message if the directory is not a git repository.
        :rtype: dict or str
        """
        if not self.repo:
            return "This directory is not a git repository."

        try:
            current_branch = self.repo.active_branch
            commit = current_branch.commit
        except ValueError:
            return "This git repository has no commits yet."

        def serialize_recursive(sub_fs: dict, tree, parent_commit: str):
            for f in tree:
                if f.type == 'blob':
                    sub_fs[f"{f.name} ({parent_commit})"] = ''
                elif f.type == 'tree':
                    sub_fs[f"{f.name} ({parent_commit})"] = {}
                    serialize_recursive(sub_fs[f"{f.name} ({parent_commit})"], f, parent_commit)

        tree = commit.tree

        serialized_git = {}
        serialized_git[f"{commit.hexsha} ({commit.author.name} - {commit.author.email})"] = {}
        serialize_recursive(serialized_git[f"{commit.hexsha} ({commit.author.name} - {commit.author.email})"], tree, commit.hexsha)

        return serialized_git

    def get_commit_history(self, path):
        """
        Get the commit history for the specified file or directory.
        :param path: The path to the file or directory.
        :type path: str
        :return: A list of commits, or an error message if the directory is not a git repository or if an error occurs while retrieving commit history.
        :rtype: list or str
        """
        if not self.repo:
            return "This directory is not a git repository."

        try:
            commits = list(self.repo.iter_commits(paths=path))
            if not commits:
                return "No commits found for this file or directory."
            return commits
        except GitCommandError:
            return "An error occurred while retrieving commit history."

    def restore_commit(self, commit_id):
        """
        Restore the file system to the specified commit.
        :param commit_id: The commit ID to restore.
        :type commit_id: str
        :return: A message indicating the result of the operation.
        :rtype: str
        """
        if not self.repo:
            return "This directory is not a git repository."

        try:
            commit = self.repo.commit(commit_id)
            self.repo.git.checkout(commit_id)
            return f"Commit {commit_id} has been restored."
        except GitCommandError:
            return f"Error: Unable to restore commit {commit_id}."

    '''Implement in CLI to resolve issue BM-18'''
    def serialize_git_tree(self) -> dict:
        tree = self.repo.tree()

        def serialize_recursive(sub_fs: dict, tree):
            sub_fs["files"] = [f.name for f in tree if f.type == 'blob']
            sub_fs["directories"] = {d.name: serialize_recursive({}, d) for d in tree if d.type == 'tree'}
            return sub_fs

        return serialize_recursive({}, tree)

    '''Implement in CLI to resolve issue BM-18'''
    def cat_file_version(self, path: str, commit_id: str) -> str:
        target = self.repo.commit(commit_id).tree[path]
        return target.data_stream.read().decode()

    '''Implement in CLI to resolve issue BM-18'''
    def add_changes_to_commit(self, paths: list) -> bool:
        if not isinstance(paths, list):
            raise TypeError("Expected a list")
        try:
            self.repo.index.add(paths)
        except FileNotFoundError:
            return False
        return True

    '''Implement in CLI to resolve issue BM-18'''
    def commit(self, commit_message):
        self.repo.index.commit(commit_message)

    '''Implement in CLI to resolve issue BM-18'''
    def get_file_versions(self, path: str) -> tuple:
        commits = self.repo.iter_commits('--all', max_count=100, paths=path)
        return tuple(str(c) for c in commits)

    def push_to_remote(self):
        assert self.remote is not None
        self.remote.push()

    # def pull_to_remote(self):
    #     assert self.remote is not None
    #     self.remote.pull()
    #

    def get_unstaged_changes(self) -> list:
        """Returns a list of file paths of blobs that changes since last commit"""
        return [f.a_path for f in self.repo.index.diff(None)]

    def get_untracked_files(self) -> list:
        """Returns a list of untracked files"""
        return self.repo.untracked_files

    def rebuild_local_git(self):
        """
        This is a Git on the Fly operation. If user choose to delete their local .git after backup
        this is how they get it back. All changes and uncommitted files are stashed.
        See https://stackoverflow.com/questions/6246907/can-deleted-git-be-restored
        """
        assert self.remote_path is not None
        assert self.repo is None

        self.init_git_repo()
        self.remote = self.repo.create_remote('usb', self.remote_path)

        # Create and checkout a local "master" branch that tracks "origin/master"
        master = self.repo.create_head('master', 'origin/master')

        # Set the upstream tracking information for the master branch
        master.set_tracking_branch(self.remote.refs.master)

        # Reset the index and working tree to match the "master" branch
        master.git.reset('HEAD', '.')

        # Rebase the "master" branch with the "--autostash" option
        self.repo.git.rebase('--autostash')

