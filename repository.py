import requests

"""
REPO_URL = "https://api.github.com/repos/pallets/click/pulls"




"""


class AbstractRepository:
    """Base repository class."""

    def __init__(self, name) -> None:
        self._name = name

    def get_pr_data(self):
        raise NotImplementedError()
    
    def __str__(self) -> str:
        return self._name

class GithubRepository(AbstractRepository):
    """Github implementation"""

    def __init__(self, config) -> None:
        super().__init__(config['repository_name'])
        self._config = config

    def get_pr_data(self):
        """retrieve data using Github REST API"""

        headers = {
            "accept": "application/vnd.github+json"
        }
        payload = {
            "state": "closed",
            "direction": "desc",
            "per_page": 1
        }

        r = requests.get(self._config['url_pr'], params=payload)

        # print 1 item
        prs = r.text
        print(prs)

    def __str__(self) -> str:
        return super().__str__() + ' hosted on GitHub'
    
def get_repository(config):
    """Return an instance of the right repo type"""
    
    if not config or not config['enabled']:
        return None
    
    if config['repoType'] == "Github":
        return GithubRepository(config)