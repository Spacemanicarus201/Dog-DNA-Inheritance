# utils/debug.py
enable_debug = True

def debug(*msg):
    if enable_debug:
        print("[DEBUG]", *msg)
