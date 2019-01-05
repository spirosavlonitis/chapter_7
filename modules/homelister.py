import os
import getpass

def run(**args):
    """List home dir"""
    print("[*] In homelister module.")
    if "nt" in os.name:
        return str(os.listdir("C:\\"))
    return str(os.listdir(f"/home/{getpass.getuser()}"))