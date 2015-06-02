__author__ = 'Sergey Sudakovich'
__version__ = '0.1'
__pkg__ = 'uberepo'

import os
import tempfile
import subprocess

import requests

registry = set()

CONTROL_FILE = """
Package: {package}
Architecture: all
Maintainer: {author}
Version: {version}
Description: Uber Repo
""".format(
    package=__pkg__,
    author=__author__,
    version=__version__
)


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
            cls.registry.add((name, new_cls))
        return new_cls

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
            d = tempfile.mkdtemp()
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
        for name, repo in Repo:
            _download_to(repo.key, os.path.join(aptd, 'trusted.gpg.d', '{}.gpg'.format(name.lower())))
            with open(os.path.join(aptd, 'sources.list.d', '{}.list'.format(name.lower())), 'w') as f:
                f.write('\n'.join(repo.lists))

    @staticmethod
    def build(pkgdir):
        debfile = os.path.join(os.path.dirname(pkgdir), __pkg__ + '.deb')
        cmd = ['fakeroot', 'dpkg-deb', '--build', pkgdir, debfile]
        devnull = open(os.devnull, 'w')
        subprocess.call(cmd, stdout=devnull, stderr=subprocess.STDOUT)
        return debfile


__import_repos_()
