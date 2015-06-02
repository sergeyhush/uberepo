#!/usr/bin/env python
"""
Uber repo

Usage:
    cli.py
    cli.py (-h | --help)
    cli.py --version
"""
from docopt import docopt

import repos

if __name__ == '__main__':
    args = docopt(__doc__, version=repos.__version__)
    scratchd = repos.Repo.prep_scratchpad()
    repos.Repo.download_parts(scratchd)
    print "Generated file: {}".format(repos.Repo.build(scratchd))
    # FIXME clenup scratchpad
