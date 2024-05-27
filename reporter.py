from yaml import safe_load

from repository import get_repository

def send_report():
    """Sends a mail report using the parameters from config.yml"""

    with open("config/config.yml", mode="rt", encoding="utf-8") as file:
        config = safe_load(file)

    repo = get_repository(config)

    print(repo)
    repo.get_pr_data()

    """
    {'repository_name': 'click', 'enable': True, 'repoType': 'Github', 
    'url': 'https://github.com/pallets/click', 
    'url_pr': 'https://api.github.com/repos/pallets/click/pulls',
      'pr_report': {'state': ['open', 'closed', 'inprogress'], 
      'mail_to': None, 'mail_from': None, 'mail_subject': None, 
      'mail_body_template': None}}


    """


if __name__ == "__main__":
    send_report()