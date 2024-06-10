import datetime
import json
import logging

import pytest
import requests
import requests_mock

from app.repository import (
    load_config, 
    get_repository,
    GithubRepoExtractor)

@pytest.fixture
def config():
    """Default config is for Github repo"""
    return load_config('config/config.yml')

@pytest.fixture
def unsupported_config():
    """Test with non supported repository flavor"""
    return load_config('config/unsupported.yml')

@pytest.fixture
def disabled_config():
    """Test the enabled option"""
    return load_config('config/disabled.yml')

def test_load_config(config):
    """Test right config file"""

    assert config is not None
    assert config['repository_name'] == 'click'

def test_load_config_wrong_filename():
    """Test error when incorrect filename is passed"""
    with pytest.raises(FileNotFoundError):
        load_config('config/confi.yml')

@pytest.fixture
def github_extractor(config):
    return get_repository(config) 

def test_get_repository_github(github_extractor):
    """Get instance of supported repoType"""
    assert isinstance(github_extractor, GithubRepoExtractor)

def test_get_repository_disabled(disabled_config):
    """Ask for disabled repo"""
    gre = get_repository(disabled_config)

    assert gre is None

def test_get_repository_unsupported(unsupported_config):
    """Ask for unsupported repoType"""
    with pytest.raises(ValueError):
        get_repository(unsupported_config)

@pytest.fixture
def json_content_github_closed():
    with open('tests/resources/pr_sample_closed.json', mode="r") as file:
        json_response = json.loads(file.read())
    
    return json_response

@pytest.fixture
def json_content_github_open():
    with open('tests/resources/pr_sample_open.json', mode="r") as file:
        json_response = json.loads(file.read())
    
    return json_response

def test_classify_prs(github_extractor, json_content_github_closed):
    today = datetime.datetime.today()
    valid_dt = today - datetime.timedelta(days=1)
    oop, pr_o, pr_c, pr_m = github_extractor.classify_prs(
        json_content_github_closed, valid_dt
        )

    assert len(pr_c) == 0


@requests_mock.Mocker(kw='mock')
def test_extract_pr_data(config, github_extractor, json_content_github_closed, json_content_github_open, **kwargs):
    """Mock is returning a PR with closed state"""
    kwargs['mock'].get(
        config['url_pr'], 
        json=json_content_github_closed,
        headers={'Link': '<https://local.github.com/repositories/19103692/pulls?state=closed&direction=desc&per_page=1&page=2>; rel="next", <https://local.github.com/repositories/19103692/pulls?state=closed&direction=desc&per_page=1&page=1082>; rel="last"'}
        )

    data = github_extractor.extract_pr_data(period_days=1)

    assert data == {}