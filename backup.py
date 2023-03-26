import os


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
        files = [f for f in paths if os.path.isfile(f"{pwd}/{f}")]
        dirs = [d for d in paths if os.path.isdir(f"{pwd}/{d}")]

        parent.append(curr_dirr)
        sub_fs["files"] = files
        sub_fs["directories"] = {d: serialize_recursive({}, list(parent), d) for d in dirs}  # no base case

        return sub_fs

    file_system = {}
    return serialize_recursive(file_system, [], root_path)
