import unittest
from backup import serialize_local_fs


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.root = "test_file_sys"

    def assert_nested_file_sys_equal(self, d1: dict, d2: dict):
        d1_keys = list(d1.keys())
        d2_keys = list(d2.keys())

        self.assertCountEqual(d1_keys, d2_keys)
        for k in d1_keys:
            if isinstance(d1[k], list):
                self.assertCountEqual(d1[k], d2[k])
            else: # if not a list then a nested dictionary
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

    def test_path_dne(self):
        self.assertEqual({}, serialize_local_fs("DNE"))

    def test_serialized_file_system(self):
        expected_output = {
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

        # expected_output = (["file5.txt"], ["Desktop", "Downloads"])
        self.assert_nested_file_sys_equal(expected_output, serialize_local_fs(self.root))


if __name__ == '__main__':
    unittest.main()
