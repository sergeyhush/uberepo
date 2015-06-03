__author__ = 'Sergey Sudakovich'
__version__ = '0.1'
__pkg__ = 'uberepo'
__deb__ = __pkg__ + '_' + __version__ + '.deb'

import os
import tempfile
import subprocess
import logging

import requests

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

registry = set()

CONTROL_FILE = """Package: {package}
Architecture: all
Maintainer: {author}
Version: {version}
Description: Uber Repo
""".format(
    package=__pkg__,
    author=__author__,
    version=__version__
)
POSTINST = """#!/bin/sh

{body}
"""


def _aptdir(d):
    return os.path.join(d, 'etc', 'apt')


def _makedirs(o):
    for d in o:
        os.makedirs(d)


def _file_with_string(path, s):
    with open(path, 'w') as f:
        f.write(s)
        f.flush()


def _download_to(url, path):
    r = requests.get(url, stream=True)
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
    return path


def __import_repos_():
    def filename(o):
        return os.path.basename(os.path.splitext(o)[0])

    modules = set(map(filename, os.listdir(os.path.dirname(__file__))))
    modules.remove('__init__')
    for module in modules:
        __import__('repos.' + module, locals(), globals())


class MetaRepo(type):
    registry = set()

    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        # if not isinstance(new_cls, repos.Repo)
        if name != 'Repo':
            MetaRepo._validate_class(name, attrs)
            cls.registry.add((name, new_cls))
        return new_cls

    @staticmethod
    def _validate_class(name, attrs):
        if ('key' not in attrs) and ('keyring' not in attrs):
            raise AttributeError('Class {} must define "key" or "keyring"'.format(name))

    def __iter__(self):
        return iter(MetaRepo.registry)


class Repo(object):
    __metaclass__ = MetaRepo

    @staticmethod
    def apt_dir(d):
        return _aptdir(d)

    @staticmethod
    def prep_scratchpad(d=None):
        if not d:
            d = tempfile.mkdtemp(dir=os.getcwd())
        if not os.path.isdir(d):
            raise AttributeError("{0} must exist.".format(d))
        pkgdir = os.path.join(d, __pkg__)
        os.makedirs(pkgdir)
        aptdir = _aptdir(pkgdir)
        _makedirs(os.path.join(aptdir, _d) for _d in ['sources.list.d', 'trusted.gpg.d'])
        # Create standard Debian package dir structure
        debdir = os.path.join(pkgdir, 'DEBIAN')
        os.makedirs(debdir)
        _file_with_string(os.path.join(debdir, 'control'), CONTROL_FILE)

        return pkgdir

    @staticmethod
    def download_parts(pkgdir):
        aptd = Repo.apt_dir(pkgdir)
        debdir = os.path.join(pkgdir, 'DEBIAN')
        keys = []
        for name, repo in Repo:
            src = None
            dest = None
            if hasattr(repo, 'key'):
                # src = repo.key
                keys.append(repo.key)
                # dest = os.path.join(aptd, 'keys.tmp', '{}.key'.format(name.lower()))
                log.debug('Adding key {key} for {repo}'.format(key=repo.key, repo=name))
            elif hasattr(repo, 'keyring'):
                src = repo.keyring
                dest = os.path.join(aptd, 'trusted.gpg.d', '{}.gpg'.format(name.lower()))
                log.debug(
                    'Downloading keyring {key} for {repo} to {dest}'.format(key=repo.keyring, repo=name, dest=dest))
                _download_to(src, dest)
            with open(os.path.join(aptd, 'sources.list.d', '{}.list'.format(name.lower())), 'w') as f:
                f.write('\n'.join(repo.lists))
        if keys:
            postinst_body = '\n'.join(
                ['wget -q -O- "{}" | apt-key add -'.format(k) for k in keys]
            )
            _file_with_string(os.path.join(debdir, 'postinst'), POSTINST.format(body=postinst_body))
            os.chmod(os.path.join(debdir, 'postinst'), 0555)

    @staticmethod
    def build(pkgdir, debfile=None):
        if not debfile:
            debfile = os.path.join(os.getcwd(), __deb__)
        cmd = ['fakeroot', 'dpkg-deb', '--build', pkgdir, debfile]
        devnull = open(os.devnull, 'w')
        retcode = subprocess.call(cmd, stdout=devnull, stderr=subprocess.STDOUT)
        return (debfile, retcode)


__import_repos_()
