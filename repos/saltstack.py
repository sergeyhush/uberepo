import repos


class Saltstack(repos.Repo):
    key = "http://debian.saltstack.com/debian-salt-team-joehealy.gpg.key"
    lists = [
        "deb http://debian.saltstack.com/debian wheezy-saltstack main"
    ]
