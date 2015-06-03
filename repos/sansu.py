import repos


class Sansu(repos.Repo):
    keyring = "http://repos.sensuapp.org/apt/keyring.gpg"
    lists = [
        "deb http://repos.sensuapp.org/apt sensu main"
    ]

