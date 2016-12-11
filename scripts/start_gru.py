#!/usr/bin/env python
import os
import sys
import fnmatch

from subprocess import Popen

import pip
from gru.config import settings


def find_recursive(path, pattern):
    matches = []
    for root, _, file_names in os.walk(path):
        for file_name in fnmatch.filter(file_names, pattern):
            matches.append(os.path.join(root, file_name))
    return matches


def install_plugin_reqs(requirements_file):
    print('pip install -r {}'.format(requirements_file))
    pip.main(['install', '-r', requirements_file])


def run_gunicorn(gunicorn_args):
    print('gunicorn {}'.format(' '.join(gunicorn_args)))
    args = ['gunicorn'] + gunicorn_args
    gunicorn_proc = Popen(args, stdout=sys.stdout, stderr=sys.stderr, env=os.environ)
    gunicorn_proc.wait()
    return gunicorn_proc.returncode


def main(args):
    plugin_directories = settings.get('plugins.directories')
    requirement_files = []
    for plugin_directory in plugin_directories:
        requirement_files += find_recursive(plugin_directory, 'requirements.txt')
        requirement_files += find_recursive(plugin_directory, 'reqs.txt')

    for req_file in requirement_files:
        install_plugin_reqs(req_file)

    return_code = run_gunicorn(args)
    sys.exit(return_code)


if __name__ == '__main__':
    main(sys.argv[1:])
