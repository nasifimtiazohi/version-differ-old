#!/usr/bin/env python

"""Tests for `version_differ` package."""

from requests import NullHandler
from requests.api import get
import pytest
import tempfile
from git import Repo


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

def test_head_commit_for_tag():
    temp_dir = tempfile.TemporaryDirectory()
    url = "https://github.com/nasifimtiazohi/test-version-tag"
    package = "test"
    clone_repository(url, temp_dir.name)
    
    repo = Repo(temp_dir.name)
    tags = repo.tags

    assert get_commit_of_release(tags, package, "0.0.8") is None
    assert get_commit_of_release(tags, package, "10.0.8").hexsha == '51efd612af12183a682bb3242d41369d2879ad60'
    assert get_commit_of_release(tags, package, "10.0.8-") is None
    assert get_commit_of_release(tags, "hakari", "0.3.0").hexsha == '946ddf053582067b843c19f1270fe92eaa0a7cb3' 


# def test_temp():
#     temp_dir = tempfile.TemporaryDirectory()
#     url = "https://github.com/hashicorp/vault"
#     package = "github.com/hashicorp/vault/vault"
#     clone_repository(url, temp_dir.name)

#     repo = Repo(temp_dir.name)
#     tags = repo.tags

#     print(get_commit_of_release(tags, package, "1.4.3"))


def test_go_module_path():
    assert get_go_module_path("github.com/keybase/client/go/chat/attachments") == "go/chat/attachments"
    assert get_go_module_path("github.com/lightningnetwork/lnd") is None
    assert get_go_module_path("github.com/istio/istio/pilot/pkg/proxy/envoy/v2") == "pilot/pkg/proxy/envoy/v2"


def test_go():
    assert get_files_loc_stat(
        go_get_version_diff_stats("github.com/labstack/echo/middleware",
    "https://github.com/labstack/echo", "4.2.0", "4.1.17")) == (27, 2695)

    assert  get_files_loc_stat(
        go_get_version_diff_stats("github.com/crewjam/saml","https://github.com/crewjam/saml",
        "0.4.2", "0.4.3")) == (10, 192)
    
def get_files_loc_stat(files):
    f = len(files)
    loc = 0
    for k in files.keys():
        loc += (files[k]['loc_added'] + files[k]['loc_removed'])
    return f, loc

def test_composer():
    assert get_files_loc_stat(
            get_version_diff_stats(
            COMPOSER, "psr/log", "https://github.com/php-fig/log",  "1.1.4",  "2.0.0"
            )
        ) == (10, 486)
    
    assert get_files_loc_stat(
            get_version_diff_stats(
            COMPOSER, "illuminate/auth", "https://github.com/illuminate/auth", "4.1.26", "4.1.25"
            )
        ) == (6, 199)



def test_maven():
    assert get_files_loc_stat(
            get_version_diff_stats(
            MAVEN, "com.github.junrar:junrar", "https://github.com/junrar/junrar.git", "1.0.1", "1.0.0"
            )
        ) == (8, 165)
    
    assert get_files_loc_stat(
            get_version_diff_stats(
            MAVEN, "org.togglz:togglz-console", "https://github.com/togglz/togglz", "2.9.4", "2.9.3"
            )
        ) == (8, 90)
    
def test_npm():
    assert get_files_loc_stat(
        get_version_diff_stats(NPM, "lodash", "https://github.com/lodash/lodash", "4.11.1", "4.11.0")) == (12,98)
    
    
    assert get_files_loc_stat(
        get_version_diff_stats(NPM, "set-value", "https://github.com/jonschlinkert/set-value", "3.0.0", "3.0.1")) == (4,48)
    
    # print(get_version_diff_stats(NPM, "property-expr","https://github.com/jquense/expr", "2.0.2", "2.0.3"))

def test_nuget():
    assert get_files_loc_stat(
        get_version_diff_stats(NUGET, "messagepack.immutablecollection", "https://github.com/neuecc/MessagePack-CSharp",  "2.1.80","2.0.335")
    ) == (1, 20)

    assert get_files_loc_stat(
        get_version_diff_stats(NUGET, "microsoft.aspnetcore.server.kestrel.core", "https://github.com/aspnet/KestrelHttpServer", "2.0.2", "2.0.3")) == (7, 113)

    




def test_pip():
    assert get_files_loc_stat(
        get_version_diff_stats(PIP, "meinheld", "asdasd", "1.0.2", "1.0.1")) == (43, 12469)

def test_rubygems():
    assert get_files_loc_stat(
        get_version_diff_stats(
            RUBYGEMS, "yard", "https://github.com/lsegal/yard", "0.9.20", "0.9.19"
        )) == (10, 3402)
    
def test_cargo():
    assert get_files_loc_stat(get_version_diff_stats(CARGO, "guppy", "adsd", "0.8.0", "0.9.0")) == (9, 393)


