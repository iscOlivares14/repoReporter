import datetime
import json
import logging
import re
from urllib.parse import urlparse, parse_qs

import requests
from yaml import safe_load

logger = logging.getLogger(__name__)

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
                logger.debug(next_link_item)
                re_url_item = re.compile('^<.*>')
                results = re_url_item.search(next_link_item[0].strip())
                url_str = results.group()
                url_str = url_str.replace('<', '').replace('>', '')
                url_obj = urlparse(url_str)
                url_qs = parse_qs(url_obj.query)

        if url_qs and 'page' in url_qs:
            next_page = url_qs.get('page')[0]

        return next_page

    def _get_pr_url(self):
        """"url to get repository PRs"""
        return self._config['url_pr']
    
    def _get_payload(self, next_page=None):
        """default 10 PRs per page"""
        payload = {
            "state": "all",
            "direction": "desc",
            "per_page": 15
        }
        if next_page:
            payload.update({'page': next_page})

        return payload
    
    # TODO: MOve all this to a PR Class for better semanthic
    def _is_pr_time_valid(self, str_pr_time, valid_time):
        """Check time from PR is valid, depends on the case 
        it could be created_at, closed_at, merged_at"""
        pr_time = datetime.datetime.strptime(str_pr_time, '%Y-%m-%dT%H:%M:%SZ')
        logger.debug(f"{pr_time} >= {valid_time} = {pr_time >= valid_time}")
        return pr_time >= valid_time

    def _is_pr_open(self, pr, valid_time):
        """
        pr_open - Applies when:
        - "state": "open" <==
        - "created_at": "2024-05-21T20:49:52Z", (Valid time) <==
        - "updated_at": "2024-05-23T22:19:45Z",
        - "closed_at": null
        - "merged_at": null
        """
        logger.debug("is Open??")
        is_open = False
        if pr['state'] == 'open':
            if self._is_pr_time_valid(pr['created_at'], valid_time):
                is_open = True
        return is_open
    
    def _is_pr_merged(self, pr, valid_time):
        """
        pr_merged - Applies when:
        - "state": "closed" <==
        - "created_at": "2024-05-20T23:23:43Z",
        - "updated_at": "2024-05-22T21:14:03Z",
        - "closed_at": "2024-05-21T14:46:21Z",
        - "merged_at": "2024-05-21T14:46:21Z", <==
        """
        logger.debug("is Merged??")
        is_merged = False
        if pr['state'] == 'closed':
            if pr['merged_at'] and \
                self._is_pr_time_valid(pr['merged_at'], valid_time):
                is_merged = True
        return is_merged

    def _is_pr_closed(self, pr, valid_time):
        """
        pr_closed - Applies when:
        - "state": "closed" <==
        - "created_at": "2024-05-20T23:23:43Z",
        - "updated_at": "2024-05-22T21:14:03Z",
        - "closed_at": "2024-05-21T14:46:21Z", <==
        - "merged_at": null, <==
        """

        is_closed = False
        if pr['state'] == 'closed':
            if pr['closed_at'] and \
                not pr['merged_at'] and \
                self._is_pr_time_valid(pr['closed_at'], valid_time):
                is_closed = True
        logger.debug(f"is Closed?? {is_closed}")
        return is_closed

    def _get_minimum_valid_datetime(self, period_days):
        """Get the datetime which works as low limit for PRs to report."""
        today = datetime.datetime.today()
        return today - datetime.timedelta(days=period_days)
    
    def get_config(self):
        return self._config

    def classify_prs(self, prs_list, valid_datetime):
        """
        Classify PRs in open, closed or merged and return a tuple of 3 lists

        out_of_period - Flagged when the first out of time window PR appears
        """
        pr_open = []
        pr_closed = []
        pr_merged = []
        out_of_period = False

        for pr in prs_list:
            # TODO: Make optional/configurable to save PR data
            # logger.debug(f"Saving data for PR id: {pr['id']}")
            # with open(f"tmp/{pr['id']}.json", mode="w") as file:
            #     file.write(json.dumps(pr))

            if self._is_pr_open(pr, valid_datetime):
                pr_open.append(pr)
            elif self._is_pr_merged(pr, valid_datetime):
                pr_merged.append(pr)
            elif self._is_pr_closed(pr, valid_datetime):
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
        valid_datetime = self._get_minimum_valid_datetime(period_days)
        logger.info(f"Valid datetime {valid_datetime}")
        out_of_period = False
        next_page = None

        ## temporal counter 5
        counter = 0

        while not out_of_period:
            payload = self._get_payload(next_page)
            r = requests.get(self._get_pr_url(), params=payload)
            if not r:
                break # empty response
            # validate PRs are in range and add to final list
            out_of_period, pr_open, pr_closed, pr_merged = self.classify_prs(r.json(), valid_datetime)
            logger.info(f'# Cycle - O: {len(pr_open)} / C: {len(pr_closed)} / M: {len(pr_merged)}')
            # no valid entries in the last cycle, stop
            if not pr_open and not pr_merged and not pr_closed:
                logger.info("Stop extraction as no new valid events appeared")
                break
            # add to final results
            prs_to_report['open'].extend(pr_open)
            prs_to_report['closed'].extend(pr_closed)
            prs_to_report['merged'].extend(pr_merged)
            
            # looks for next link to call, must be different
            if next_page != self._get_next_page(r.headers):
                next_page = self._get_next_page(r.headers)
            else:
                next_page = None
            logger.debug(f'Next page? {next_page}')
            # print(prs_to_report)
            # no next page break the cycle
            if not next_page:
                break
            if counter >= 5:
                break
            counter += 1

        total_open = len(prs_to_report['open'])
        total_merged = len(prs_to_report['merged'])
        total_closed = len(prs_to_report['closed'])
        prs_to_report['qty_open'] = total_open
        prs_to_report['qty_closed'] = total_closed
        prs_to_report['qty_merged'] = total_merged
        prs_to_report['total_prs'] = total_open + total_closed + total_merged
        prs_to_report['days_to_report'] = period_days
        logger.info(
            f"Total <Open: {total_open}>"
            f" <Closed: {total_closed}>"
            f" <Merged: {total_merged}>"
        )
        
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