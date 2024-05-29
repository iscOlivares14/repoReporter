import logging
import re
from urllib.parse import urlparse, parse_qs

import requests
from yaml import safe_load


logging.basicConfig(level=logging.DEBUG)

class AbstractRepositoryExtractor:
    """Base repository class."""

    def __init__(self, name) -> None:
        self._name = name

    def extract_pr_data(self):
        raise NotImplementedError()
    
    def __str__(self) -> str:
        return self._name

class GithubRepoExtractor(AbstractRepositoryExtractor):
    """Github implementation"""

    def __init__(self, config) -> None:
        super().__init__(config['repository_name'])
        self._config = config

    def _get_next_page(self, resp_headers):
        """Review link references to next"""
        
        link = resp_headers.get('Link', None)
        next_link_item = None
        url_qs = None
        next_page = None

        if link:
            next_link_item = [l for l in link.split(",") if "next" in l]
            # <https://api.github.com/repositories/19103692/pulls?state=closed&direction=desc&per_page=1&page=2>; rel="next"
            if next_link_item:
                re_url_item = re.compile('^<.*>')
                results = re_url_item.search(next_link_item[0])
                url_str = results.group()
                url_str = url_str.replace('<', '').replace('>', '')
                url_obj = urlparse(url_str)
                url_qs = parse_qs(url_obj.query)

        if url_qs and 'page' in url_qs:
            next_page = url_qs.get('page')[0]

        return next_page

    def _get_pr_url(self):
        return self._config['url_pr']
    
    def _get_payload(self, next_page=None):
        payload = {
            "state": "all",
            "direction": "desc",
            "per_page": 1
        }
        if next_page:
            payload.update({'page': next_page})

        return payload
    
    def _pr_in_time():
        pass

    def _pr_is_closed(self, pr):
        return pr['state'] == 'closed'

    def classify_prs(self, prs_list):
        """Classify PRs in open, closed or merged and return a tuple of 3 lists"""
        pr_open = []
        pr_closed = []
        pr_merged = []
        out_of_period = False

        for pr in prs_list:
            # validate time
            # validate open
            # validate closed
            if self._pr_is_closed(pr):
                pr_closed.append(pr)

        return (out_of_period, pr_open, pr_closed, pr_merged)


    def extract_pr_data(self, period_days=7):
        """retrieve data using Github REST API"""
        # PRs open, closed, merged in the specified period time
        prs_to_report = {
            "open": [],
            "merged": [],
            "closed": []
        }

        # as the PRs are sorted will stop once it's out of timeframe
        out_of_period = False
        next_page = None

        ## temporal counter 5
        counter = 0

        while not out_of_period:
            payload = self._get_payload(next_page)
            print(f"Making API call {payload}")
            r = requests.get(self._get_pr_url(), params=payload)
            if not r:
                break # empty response
            # validate PRs are in range and add to final list
            out_of_period, pr_open, pr_closed, pr_merged = self.classify_prs(r.json())
            print(f'# Cycle - open: {len(pr_open)} / closed: {len(pr_closed)} / merged: {len(pr_merged)}')
            # add to final results
            prs_to_report['open'].append(pr_open)
            prs_to_report['closed'].append(pr_closed)
            prs_to_report['merged'].append(pr_merged)
            # looks for next link to call, must be different
            if next_page != self._get_next_page(r.headers):
                next_page = self._get_next_page(r.headers)
            else:
                next_page = None
            print(f'Next page? {next_page}')
            # no next page break the cycle
            if not next_page:
                break
            if counter >= 5:
                break
            counter += 1
        
        return prs_to_report

    def __str__(self) -> str:
        return super().__str__() + ' hosted on GitHub'


def load_config(config_file_path):
    with open(config_file_path, mode="rt", encoding="utf-8") as file:
        config = safe_load(file)
    
    return config


def get_repository(config):
    """Return an instance of the right repo type"""
    
    if not config or not config['enabled']:
        return None
    
    if config['repoType'] == "Github":
        return GithubRepoExtractor(config)
    else:
        raise ValueError('Repository Type not supported.')