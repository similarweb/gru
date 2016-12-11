import os


def relative_to(file_name, location):
    abs_file = os.path.abspath(file_name)
    abs_dir = os.path.dirname(abs_file)
    abs_dir = os.path.expanduser(abs_dir)
    return os.path.abspath(os.path.join(abs_dir, location))
