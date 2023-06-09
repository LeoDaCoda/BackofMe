import unittest
import git
from backup import Backup
import os
import shutil

class FileIOHelper:
    def __init__(self, string_to_add):
        self.string_to_add = string_to_add

    def add_string_to_file(self, file_path):
        # Check if the file exists
        if not os.path.exists(file_path):
            # Create the file if it does not exist
            open(file_path, 'w').close()

        # Open the file in append mode and add the string to the end
        with open(file_path, 'a') as file:
            file.write('\n' + self.string_to_add)

    def delete_last_line(self, file_path):
        # Open the original file and read all its lines
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Ensure the last line is the string added by add_string_to_file
        assert lines[-1].strip() == self.string_to_add, "The last line is not the string added by add_string_to_file."

        # Remove the last line and the newline character added by add_string_to_file
        lines = lines[:-1]
        if lines[-1].endswith('\n'):
            lines[-1] = lines[-1][:-1]

        # Write all the lines except for the last line to the file
        with open(file_path, 'w') as file:
            for line in lines:
                file.write(line)


def delete_last_line(file_path):
    # Open the original file and read all its lines
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Remove the last line if it was added by the add_string_to_file function
    if lines[-1].strip() == 'Hello, world!':
        lines = lines[:-1]

    # Write all the lines except for the last line to the file
    with open(file_path, 'w') as file:
        for line in lines:
            file.write(line)

class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.debug=False
        self.root = "test_file_sys"
        self.test_file_sys = "TEST_FILE_SYS"
        self.remote_path = '.remote'
        try:
            os.mkdir(self.remote_path)
        except FileExistsError:
            shutil.rmtree(self.remote_path)
            print(f"Deleted temporary directory {self.remote_path}")
        # Create a temporary directory to use for testing
        try:
            shutil.copytree(self.root, self.test_file_sys)
        except FileExistsError:
            shutil.rmtree(self.test_file_sys)
            shutil.copytree(self.root, self.test_file_sys)
            print(f"Please delete temporary directory {self.test_file_sys}")
        # self.repo_rapper = GitRapper(self.root)
        self.repo_rapper = Backup(self.test_file_sys, init_git_if_none=True)
        self.test_file = "Downloads/dir1/file2.txt"
        self.test_file_commits = {
            '480ddf7f381374b11d3e245690023b6f76f4d987': 'random thoughts this should be my diary\n\nmonday - got a '
                                                        'free chinese meal',
            'a8ed8bb567dff4de249781ed26cf7e6a34c74b04': 'random thoughts this should be my diary\n',
            'f886763b622828dd57b01f815b10464cddcf8be6': 'pa$$ord'
        }
        self.expected_tree = {
            "files": ["file5.txt"],
            "directories": {
                "Desktop": {
                    "files": ["1.txt", "file"],
                    "directories": {}
                },
                "Downloads": {
                    "files": ["file4.txt"],
                    "directories": {
                        "dir1": {
                            "files": ["file2.txt", "file3.txt"],
                            "directories": {}
                        }
                    }
                }
            }
        }
        self.fileIOtestfile = ".test"
        self.gotf = True

    def tearDown(self) -> None:
        print("Don!!!!!!")
        shutil.rmtree(self.test_file_sys)
        shutil.rmtree(self.remote_path)

    def test_add_string_to_existing_file(self):
        # Create the test file with initial contents
        first = "Initial contents\n"
        with open(self.fileIOtestfile, "w") as file:
            file.write(first)

        # Call the add_string_to_file method to add a string to the file
        ch = "A"*10
        helper = FileIOHelper(ch)
        helper.add_string_to_file(self.fileIOtestfile)

        # Verify that the file now has the expected contents
        with open(self.fileIOtestfile, "r") as file:
            contents = file.read()
            expected_contents = first + '\n' + ch
            self.assertEqual(contents, expected_contents)

        os.remove(self.fileIOtestfile)

    def test_delete_last_line(self):
        string_to_add = "This is a test string."
        helper = FileIOHelper(string_to_add)

        # First add a string to the file
        helper.add_string_to_file(self.fileIOtestfile)

        # Check that the file now contains the string
        with open(self.fileIOtestfile, 'r') as file:
            contents = file.read()
        self.assertIn(string_to_add, contents)

        # Now delete the last line
        helper.delete_last_line(self.fileIOtestfile)

        # Check that the file no longer contains the string
        with open(self.fileIOtestfile, 'r') as file:
            contents = file.read()
        self.assertNotIn(string_to_add, contents)

        # Clean up the test file
        os.remove(self.fileIOtestfile)

    def test_invalid_root_path(self):
        self.assertRaises(FileNotFoundError, Backup, "Path DNE")  # Test the Backup class constructor on assertRaises

    def test_no_remote(self):
        if self.debug: # if debug is True no remote is configured
            self.assertIsNone(self.repo_rapper.remote)

    def test_error_raised_invalid_repo_path(self):
        # self.assertRaises(git.InvalidGitRepositoryError, GitRapper, self.root + "/Desktop")
        invalid_repo = Backup(self.test_file_sys + "/Desktop")
        self.assertEqual(None, invalid_repo.repo)

    def assert_nested_file_sys_equal(self, d1: dict, d2: dict):
        d1_keys = list(d1.keys())
        d2_keys = list(d2.keys())

        self.assertCountEqual(d1_keys, d2_keys)
        for k in d1_keys:
            if isinstance(d1[k], list):
                self.assertCountEqual(d1[k], d2[k])
            else:  # if not a list then a nested dictionary
                self.assert_nested_file_sys_equal(d1[k], d2[k])

    def test_assert_nested_dict_equal_pass(self):
        x, y = ({"a": [1, 2, 3], "b": {"c": [4, 5, 6]}}, {"b": {"c": [6, 4, 5]}, "a": [3, 2, 1]})
        self.assert_nested_file_sys_equal(x, y)

    def test_assert_nested_dict_equal_fail(self):
        x, y = ({"a": [1, 2, 3], "b": {"c": [13, 12]}}, {"b": {"c": [6, 4, 5]}, "a": [3, 2, 1]})
        try:
            self.assert_nested_file_sys_equal(x, y)  # Test passes if this assertion fails
        except AssertionError:
            return

        self.assertTrue(False)  # if previous assertion passes this test FAILS

    def test_serialized_file_system(self):
        # expected_output = (["file5.txt"], ["Desktop", "Downloads"])
        self.assert_nested_file_sys_equal(self.expected_tree, self.repo_rapper.get_serialized_local())

    def test_serialized_git_tree(self):
        self.assert_nested_file_sys_equal(self.expected_tree, self.repo_rapper.serialize_git_tree())

    def test_get_file_version_invalid(self):
        self.assertCountEqual((), self.repo_rapper.get_file_versions("DNE"))

    def test_get_file_version(self):
        self.assertCountEqual(tuple(self.test_file_commits), self.repo_rapper.get_file_versions(self.test_file))

    def test_cat_file_version(self):
        for commit_id, text in self.test_file_commits.items():
            with self.subTest():
                self.assertEqual(text, self.repo_rapper.cat_file_version(self.test_file, commit_id))

    def test_unstanged_changes_no_changes(self):
        self.assertCountEqual([], self.repo_rapper.get_unstaged_changes())

    def test_unstanged_changes_1_changes(self):
        helper = FileIOHelper("A"*4)
        helper.add_string_to_file(f'{self.test_file_sys}/{self.test_file}')
        self.assertCountEqual([self.test_file], self.repo_rapper.get_unstaged_changes())
        helper.delete_last_line(f'{self.test_file_sys}/{self.test_file}')
        self.assertCountEqual([], self.repo_rapper.get_unstaged_changes())

    def test_get_untracked_files_no_new_file(self):
        self.assertCountEqual([], self.repo_rapper.get_untracked_files())

    def test_get_untracked_files_new_file(self):
        with open(f'{self.test_file_sys}/{self.fileIOtestfile}', 'w') as f:
            pass
        self.assertCountEqual([f'{self.fileIOtestfile}'], self.repo_rapper.get_untracked_files())
        os.remove(f'{self.test_file_sys}/{self.fileIOtestfile}')
        self.assertCountEqual([], self.repo_rapper.get_untracked_files())

    def test_rebuild_local_git(self):
        if self.gotf:
            # self.repo_rapper = Backup(self.test_file_sys, remote_path=self.remote_path)
            self.repo_rapper.add_remote(os.path.abspath(self.remote_path), init_if_not=True)
            self.repo_rapper.commit("Test commit for GOTF")
            self.repo_rapper.push_to_remote()
            old_tree = self.repo_rapper.get_serialized_local()
            unstaged_files = self.repo_rapper.get_unstaged_changes()
            untracked_files = self.repo_rapper.get_untracked_files()
            if not self.repo_rapper.delete_local_git():
                self.assertTrue(False, "Test did not run. No .git/")

            self.repo_rapper.rebuild_local_git()

            self.assertCountEqual(old_tree, self.repo_rapper.get_serialized_local())
            self.assertCountEqual(unstaged_files, self.repo_rapper.get_unstaged_changes())
            self.assertCountEqual(untracked_files, self.repo_rapper.get_untracked_files())
        else:
            self.assertTrue(False, "No test GOTF is equal to false")

    def test_rebuild_local_git_unstaged(self):
        helper = FileIOHelper("A" * 4)
        helper.add_string_to_file(f'{self.test_file_sys}/{self.test_file}')
        with self.subTest():
            self.test_rebuild_local_git()

    def test_rebuild_git_untracked(self):
        test_file = f"{self.test_file_sys}/test_rebuild_git_untracked.txt"
        with open(test_file, 'w') as f:
            f.close()
        with self.subTest():
            self.test_rebuild_local_git()


    # def test_mount_file_sys(self):
    #     if self.debug:
    #         return
    #     self.assertEqual("hello ord", self.repo_rapper.mount_remote(1, 1))

    def test_delete_git(self):
        if not os.path.exists(f"{self.test_file_sys}/.git"):
            self.assertTrue(False, f"Test not ran. {self.test_file_sys}/.git not found!")
        result = self.repo_rapper.delete_local_git()
        if os.path.exists(f"{self.test_file_sys}/.git"):
            self.assertTrue(not result, "wrong return value")
            self.assertTrue(False, f"{self.test_file_sys}/.git not deleted!")
        else:
            self.assertTrue(result, "wrong return value")
            self.assertEqual(None, self.repo_rapper.repo)

    def test_delete_git_already_deleted(self):
        try:
            shutil.rmtree(f'{self.test_file_sys}/.git')
        except FileNotFoundError:
            self.assertTrue(False, f"Test not run. {self.test_file_sys}/.git not found!")
        self.assertRaises(AssertionError, self.test_delete_git)

if __name__ == '__main__':
    unittest.main()

