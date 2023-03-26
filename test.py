import unittest
from backup import serialize_local_fs


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.root = "test_file_sys"

    def test_path_dne(self):
        self.assertEqual({}, serialize_local_fs("DNE"))

    def test_read_level_1_files_and_dirs(self):
        expected_output = {
            "files": ["file5.txt"],
            "directories": {
                "Desktop": {
                    "files": {"1.txt", "file"},
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
        self.assertEqual(expected_output, serialize_local_fs(self.root))


if __name__ == '__main__':
    unittest.main()
