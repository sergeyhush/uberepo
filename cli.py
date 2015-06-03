#!/usr/bin/env python
"""
Uber repo

Usage: cli.py [-f FILE]

Options:
    -h --help   Show help.
    --version   Show version.
    -f FILE   Output file.
"""
from docopt import docopt

import repos

if __name__ == '__main__':
    args = docopt(__doc__, version=repos.__version__)
    scratchd = repos.Repo.prep_scratchpad()
    repos.Repo.download_parts(scratchd)
    debfile = args.get('-f')
    print "Generated file: {}".format(repos.Repo.build(scratchd, debfile))
    # FIXME clenup scratchpad
