import argparse
import json
from backup import Backup
from termcolor import colored

def pretty_json(d):
    """
    Print the input dictionary as a pretty-formatted JSON string.

    :param d: The input dictionary.
    :type d: dict
    """
    print(json.dumps(d, indent=2))


def format_commit_metadata(commit):
    """
    Format the commit metadata for display.

    :param commit: A git commit object.
    :type commit: git.Commit
    :return: A list containing formatted commit metadata.
    :rtype: list
    """
    metadata = [
        colored('Author:', attrs=['bold']) + ' ' + colored(f'{commit.author.name} ({commit.author.email})', 'green'),
        colored('Date:', attrs=['bold']) + ' ' + colored(commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S %z'), 'blue'),
        colored('Message:', attrs=['bold']) + ' ' + commit.message,
        colored('Commit ID:', attrs=['bold']) + ' ' + colored(commit.hexsha, 'red')
    ]
    return metadata



def format_git_filesystem(file_system):
    """
    Format the git file system for display.

    :param file_system: A dictionary representing the serialized git file system.
    :type file_system: dict or str
    """
    if isinstance(file_system, str):
        print(file_system)
    else:
        def format_recursive(sub_fs, indent_lvl=0):
            for key, val in sub_fs.items():
                if isinstance(val, dict):
                    # print header for top-level directories
                    if indent_lvl == 0:
                        print(colored(key, 'green', attrs=['bold']))
                    else:
                        # print directory with color and indent
                        print("  " * indent_lvl + colored(key, 'blue', attrs=['bold']))
                    format_recursive(val, indent_lvl + 1)
                else:
                    # print file with color and indent
                    print("  " * indent_lvl + colored(key, 'white'))

        format_recursive(file_system)

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description="Git on the Fly - A simple local version control system.")
subparsers = parser.add_subparsers(dest='command', help='Sub-commands available.')

new_parser = subparsers.add_parser('new', help='Create a new local git repository.')
new_parser.add_argument('path', nargs='?', default=None, help='Path to initialize a new git repository. Default is the working directory.')

view_local_parser = subparsers.add_parser('view_local', help='Display the local file system.')
view_local_parser.add_argument('path', nargs='?', default=None, help='Path to display the local file system. Default is the working directory.')

view_git_parser = subparsers.add_parser('view_git', help='Display the file system in the .git folder.')
view_git_parser.add_argument('path', nargs='?', default=None, help='Path to display the file system in the .git folder. Default is the working directory.')

view_commits_parser = subparsers.add_parser('view_commits', help='Display commit history and metadata for a given file or directory.')
view_commits_parser.add_argument('path', help='Path to the file or directory for which to view commit history and metadata.')

restore_parser = subparsers.add_parser('restore', help='Restore a commit by ID.')
restore_parser.add_argument('commit_id', help='ID of the commit to be restored.')

push_parser = subparsers.add_parser('push', help='Push a file or directory to a remote destination.')
push_parser.add_argument('source', help='Path to the file or directory to be pushed.')
push_parser.add_argument('destination', help='Path to the destination to which the file or directory should be pushed.')

# Parse command-line arguments
args = parser.parse_args()

# Initialize a Backup object with the specified path, or the working directory if no path is specified.
if args.path:
    backup = Backup(args.path)
else:
    backup = Backup()

# Execute the command specified by the command-line arguments
if args.command == 'new':
    result = backup.init_git_repo()
    print(result)

elif args.command == 'view_local':
    file_system = backup.get_serialized_local()
    pretty_json(file_system)

elif args.command == 'view_git':
    file_system = backup.get_serialized_git()
    format_git_filesystem(file_system)

elif args.command == 'view_commits':
    try:
        commits = backup.get_commit_history(args.path)
        delimiter = '-' * 60
        for commit in commits:
            metadata = format_commit_metadata(commit)
            print('\n'.join(metadata))
            print(delimiter)
    except ValueError as e:
        print(f"Error: {str(e)}")


elif args.command == 'restore':
    result = backup.restore_commit(args.commit_id)
    print(result)