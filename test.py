import unittest

import git
from backup import GitRapper


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.root = "test_file_sys"
        self.repo_rapper = GitRapper(self.root)
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

    def test_invalid_root_path(self):
        self.assertRaises(FileNotFoundError, GitRapper, "Path DNE")

    def test_error_raised_invalid_repo_path(self):
        self.assertRaises(git.InvalidGitRepositoryError, GitRapper, self.root + "/Desktop")

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
        self.assert_nested_file_sys_equal(self.expected_tree, self.repo_rapper.serialize_local_fs())

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


if __name__ == '__main__':
    unittest.main()
