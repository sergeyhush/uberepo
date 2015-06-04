import repos


class Wheezy(repos.Repo):
    lists = [
        "deb http://httpredir.debian.org/debian wheezy main",
        "deb-src http://httpredir.debian.org/debian wheezy main",
    ]
