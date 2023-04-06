import os
import shutil
from git import InvalidGitRepositoryError, Repo, NoSuchPathError, GitCommandError


class Backup:
    def __init__(self, root=None):
        """
        Initialize a Backup object, setting the root directory and creating a Repo object if it's a valid git repository.

        :param root: The root directory for the backup operations. Defaults to the current working directory.
        :type root: str, optional
        :raises FileNotFoundError: If the specified root directory doesn't exist.
        """
        if not root:
            self.root = os.getcwd()
        else:
            self.root = root
        if not os.path.exists(self.root):
            raise FileNotFoundError
        try:
            self.repo = Repo(self.root)  # will raise git.NoSuchPathError if given invalid path
        except InvalidGitRepositoryError:
            self.repo = None

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

    def get_serialized_local(self):
        """
        Serialize the local file system, excluding hidden folders.

        :return: A dictionary representing the serialized file system.
        :rtype: dict
        """
        def serialize_recursive(sub_fs: dict, parent: list, curr_dir: str):
            pwd = f'{"/".join(parent)}/{curr_dir}' if len(parent) > 0 else curr_dir
            paths = os.listdir(pwd)
            paths = [p for p in paths if p != ".git"]  # removes hidden folders
            files = [f for f in paths if os.path.isfile(f"{pwd}/{f}")]
            dirs = [d for d in paths if os.path.isdir(f"{pwd}/{d}")]

            parent.append(curr_dir)
            sub_fs["files"] = files
            sub_fs["directories"] = {d: serialize_recursive({}, list(parent), d) for d in dirs}

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

