import datetime
import logging

import fire
from jinja2 import Template

from repository import load_config, get_repository


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def _get_template(template_path) -> Template:
    """Load template from specified location and return the object to be rendered."""
    with open(template_path, mode='r') as file:
        template_str = file.read()

    return Template(template_str)

def _get_mail_config(repo):
    """Get the parameters related to email sending if they are in the config"""
    report_cfg = repo.get_config()['pr_report']

    cfg = {}

    if report_cfg:    
        if report_cfg.get('mail_to') and report_cfg.get('mail_from') \
            and report_cfg.get('mail_subject') and report_cfg.get('mail_body_template'):
            cfg['to'] = report_cfg.get('mail_to')
            cfg['from'] = report_cfg.get('mail_from')
            cfg['subject'] = report_cfg.get('mail_subject')
            cfg['template_uri'] = report_cfg.get('mail_body_template')

    return cfg

def sent_mail_report(repo, days_to_report, pr_data):
    """Send mail for extracted data"""
    mail_cfg = _get_mail_config(repo)
    repo_cfg = repo.get_config()
    jinja_template = None

    if mail_cfg:
        logger.info(mail_cfg)
        jinja_template = _get_template(mail_cfg['template_uri'])
        email_content = jinja_template.render(pr_data)
        #logger.info(email_content)
        # save to a file to local visualization
        email_local_file = (f"/tmp/{repo_cfg['repository_name']}"
                            f"-{repo_cfg['repoType']}"
                            f"-{datetime.datetime.now()}.html")
        with open(email_local_file, mode="w") as file:
            file.write(email_content)
            logger.info(f"Templated genetared: {email_local_file}")
        # TODO implememt smtp for real sending
    else:
        logger.warning("Mail configuration not found or incomplete.")
    
    return jinja_template

def analize_repository_data(period_days=7, config_file_path='config/config.yml'):
    """
    Sends a mail report using the parameters from config.yml
    by default takes lastest 7 days, default config file is 'config/config.yml'
    """
    repo = get_repository(load_config(config_file_path))

    prs_data = repo.extract_pr_data(period_days)

    sent_mail_report(repo, period_days, prs_data)


if __name__ == "__main__":
    fire.Fire(analize_repository_data)

    # python3 app/reporter.py --period-days=7 --config_file_path='config/config_pytest.yml'

    #analize_repository_data(period_days=7)