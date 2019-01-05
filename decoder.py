import base64
from github3 import login


class Decoder():
    def __init__(self):
        pass
    
    def connet_to_github(self):
        """Connect to github api"""

        gh = login(username="yourusername", password="yourpassword")
        repo = gh.repository("yourusername", "yourrepository")
        branch = repo.branch("master")

        return gh, repo, branch

    def get_file_contents(self, filepath):
        """Get the contents of a given file"""

        gh, repo, branch = self.connet_to_github()
        tree = branch.commit.commit.tree.to_tree().recurse()

        for filename in tree.tree:
            if filepath in filename.path:
                print("[*] Found file %s" % filepath)
                blob = repo.blob(filename._json_data['sha'])
                return base64.b64decode((base64.b64decode(blob.content)))  # decode twice
        return None

    def list_dir(self):
        """List entries in dir"""
        entries = self.get_file_contents("homelister_1546662730.data").decode()
        entries = entries.replace('[', '').replace(']', '')
        
        for entry in entries.split(','):
            entry = entry.replace("'", '').strip()
            print(entry)

decdr = Decoder()
decdr.list_dir()