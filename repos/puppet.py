import repos


class Puppet(repos.Repo):
    key = "https://apt.puppetlabs.com/keyring.gpg"
    lists = [
        # Puppetlabs products
        "deb http://apt.puppetlabs.com wheezy main",
        "deb-src http://apt.puppetlabs.com wheezy main",
        # Puppetlabs dependencies
        "deb http://apt.puppetlabs.com wheezy dependencies",
        "deb-src http://apt.puppetlabs.com wheezy dependencies",
    ]
