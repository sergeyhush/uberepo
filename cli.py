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
    deb, code = repos.Repo.build(scratchd, debfile)
    print "Generated file: {0} ... {1}".format(deb, "Success" if code == 0 else "Failure")
    # FIXME clenup scratchpad
