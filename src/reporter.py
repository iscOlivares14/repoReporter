from .repository import load_config, get_repository


def analize_repository_data(period_days=7, config_file_path='config/config.yml'):
    """
    Sends a mail report using the parameters from config.yml
    by default takes lastest 7 days, default config file 
    """
    repo = get_repository(load_config(config_file_path))

    print(repo)
    repo.extract_pr_data(period_days)

    """
    {'repository_name': 'click', 'enable': True, 'repoType': 'Github', 
    'url': 'https://github.com/pallets/click', 
    'url_pr': 'https://api.github.com/repos/pallets/click/pulls',
      'pr_report': {'state': ['open', 'closed', 'inprogress'], 
      'mail_to': None, 'mail_from': None, 'mail_subject': None, 
      'mail_body_template': None}}


    headers

    {'Server': 'GitHub.com', 'Date': 'Mon, 27 May 2024 22:19:08 GMT', 
    'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'public, max-age=60,
      s-maxage=60', 'Vary': 'Accept, Accept-Encoding, Accept, X-Requested-With',
        'ETag': 'W/"f280d7dc09eddc72f6d86387971339337c14ff043d0b46eb24c1a50c78a4fc3a"', 
        'X-GitHub-Media-Type': 'github.v3; format=json',
          'Link': '<https://api.github.com/repositories/19103692/pulls?state=closed&direction=desc&per_page=1&page=2>; rel="next", <https://api.github.com/repositories/19103692/pulls?state=closed&direction=desc&per_page=1&page=1082>; rel="last"', 
          'x-github-api-version-selected': '2022-11-28', 
          'Access-Control-Expose-Headers': 'ETag, Link, Location, Retry-After, X-GitHub-OTP, X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Used, X-RateLimit-Resource, X-RateLimit-Reset, X-OAuth-Scopes, X-Accepted-OAuth-Scopes, X-Poll-Interval, X-GitHub-Media-Type, X-GitHub-SSO, X-GitHub-Request-Id, Deprecation, Sunset', 
          'Access-Control-Allow-Origin': '*', 'Strict-Transport-Security': 'max-age=31536000; includeSubdomains; preload', 'X-Frame-Options': 'deny', 'X-Content-Type-Options': 'nosniff', 'X-XSS-Protection': '0', 'Referrer-Policy': 'origin-when-cross-origin, strict-origin-when-cross-origin', 'Content-Security-Policy': "default-src 'none'", 'Content-Encoding': 'gzip', 'X-RateLimit-Limit': '60', 'X-RateLimit-Remaining': '59', 'X-RateLimit-Reset': '1716851948', 'X-RateLimit-Resource': 'core', 'X-RateLimit-Used': '1', 'Accept-Ranges': 'bytes', 'Transfer-Encoding': 'chunked', 'X-GitHub-Request-Id': 'BDEA:2B5A20:59C842B:982DEDD:665506DC'}

    """


if __name__ == "__main__":
    analize_repository_data(period_days=1)