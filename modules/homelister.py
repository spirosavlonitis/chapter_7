import os
import getpass

def run(**args):
    """List home dir"""
    print("[*] In homelister module.")
    return str(os.listdir(f"/home/{getpass.getuser()}"))