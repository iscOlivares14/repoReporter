from repository import load_config, get_repository


def analize_repository_data(period_days=7, config_file_path='config/config.yml'):
    """
    Sends a mail report using the parameters from config.yml
    by default takes lastest 7 days, default config file 
    """
    repo = get_repository(load_config(config_file_path))

    prs_data = repo.extract_pr_data(period_days)


if __name__ == "__main__":
    analize_repository_data(period_days=15)