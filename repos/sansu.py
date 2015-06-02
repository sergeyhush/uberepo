import repos


class Sansu(repos.Repo):
    key = "http://repos.sensuapp.org/apt/keyring.gpg"
    lists = [
        "deb http://repos.sensuapp.org/apt sensu main"
    ]
