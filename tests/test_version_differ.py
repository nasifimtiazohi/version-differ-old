#!/usr/bin/env python

"""Tests for `version_differ` package."""

from requests import NullHandler
import pytest


from version_differ.version_differ import *


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_src_download_url():
    assert (
        get_package_version_source_url(CARGO, "depdive", "0.1.0")
        == "https://crates.io/api/v1/crates/depdive/0.1.0/download"
    )
    assert (
        get_package_version_source_url(COMPOSER, "psr/log", "2.0.0")
        == "https://api.github.com/repos/php-fig/log/zipball/ef29f6d262798707a9edd554e2b82517ef3a9376"
    )
    assert (
        get_package_version_source_url(NPM, "lodash", "4.11.1")
        == "https://registry.npmjs.org/lodash/-/lodash-4.11.1.tgz"
    )
    assert (
        get_package_version_source_url(PIP, "Django", "3.2.7")
        == "https://files.pythonhosted.org/packages/59/45/c6fbb3a206df0b7dc3e6e8fae738e042c63d4ddf828c6e1ba10d7417a1d9/Django-3.2.7.tar.gz"
    )
    assert (
        get_package_version_source_url(NUGET, "Serilog", "2.10.0")
        == "https://www.nuget.org/api/v2/package/Serilog/2.10.0"
    )
    assert (
        get_package_version_source_url(RUBYGEMS, "bundler", "2.2.27")
        == "https://rubygems.org/downloads/bundler-2.2.27.gem"
    )
    assert (
        get_package_version_source_url(MAVEN, "io.spray:spray-httpx", "1.2.3")
        == "https://repo1.maven.org/maven2/io/spray/spray-httpx/1.2.3/spray-httpx-1.2.3-sources.jar"
    )


@pytest.mark.skip(reason="needs TODO")
def test_download():
    dir = "/Users/nasifimtiaz/repos/version_differ/tests/resources/temp"
    download_package_source(COMPOSER, "psr/log", "2.0.0", dir)
    download_package_source(NUGET, "Serilog", "2.10.0", dir)
    download_package_source(MAVEN, "com.github.junrar:junrar", "1.0.1", dir)
    download_package_source(RUBYGEMS, "bundler", "2.2.27", dir)
    download_package_source(PIP, "Django", "3.2.7", dir)
    download_package_source(NPM, "lodash", "4.11.1", dir)
    # TODO 1. make tempdir, assert file count

@pytest.mark.skip(reason="needs TODO")
def test_init_git_repo():
    # TODO: do it in temp file
    dir_a = "/Users/nasifimtiaz/repos/version_differ/tests/resources/repo_a"
    dir_b = "/Users/nasifimtiaz/repos/version_differ/tests/resources/repo_b"
    repo_a, oid_a = init_git_repo(dir_a)
    repo_b, oid_b = init_git_repo(dir_b)
    setup_remote(repo_a, dir_b)

    diff = get_diff_stats(dir_a, oid_a, oid_b)
    print(diff)

def test_version_diff_stats():
    assert len(get_version_diff_stats(NPM, "lodash", "4.11.1", "4.11.0")) == 943
    assert len(get_version_diff_stats(RUBYGEMS, "bundler", "2.2.27", "2.2.26")) == 299
    assert len(get_version_diff_stats(MAVEN, "com.github.junrar:junrar", "1.0.1", "1.0.0")) == 89
    assert len(get_version_diff_stats(NUGET, "Serilog", "2.10.0","2.9.0")) == 19
    assert len(get_version_diff_stats(COMPOSER, "psr/log", "2.0.0", "1.1.4")) == 25
    assert len(get_version_diff_stats(PIP, "meinheld", "1.0.2", "1.0.1")) == 112


