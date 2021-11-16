#!/usr/bin/env python

"""Tests for `version_differ` package."""

from requests import NullHandler
from requests.api import get
import pytest
import tempfile
from git import Repo
from pygit2 import clone_repository


from version_differ.version_differ import *


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


def test_init_git_repo():
    dir_a = tempfile.TemporaryDirectory().name
    dir_b = tempfile.TemporaryDirectory().name
    repo_a, oid_a = init_git_repo(dir_a)
    repo_b, oid_b = init_git_repo(dir_b)
    setup_remote(repo_a, dir_b)

    diff = get_diff_stats(dir_a, oid_a, oid_b)
    print(diff)


def test_get_commit_of_release():
    temp_dir = tempfile.TemporaryDirectory()
    url = "https://github.com/nasifimtiazohi/test-version-tag"
    package = "test"
    clone_repository(url, temp_dir.name)

    repo = Repo(temp_dir.name)
    tags = repo.tags

    assert get_commit_of_release(tags, package, "0.0.8") is None
    assert (
        get_commit_of_release(tags, package, "10.0.8").hexsha
        == "51efd612af12183a682bb3242d41369d2879ad60"
    )
    assert get_commit_of_release(tags, package, "10.0.8-") is None
    assert (
        get_commit_of_release(tags, "hakari", "0.3.0").hexsha
        == "946ddf053582067b843c19f1270fe92eaa0a7cb3"
    )


def test_get_go_module_path():
    assert (
        get_go_module_path("github.com/keybase/client/go/chat/attachments")
        == "go/chat/attachments"
    )
    assert not get_go_module_path("github.com/lightningnetwork/lnd")
    assert (
        get_go_module_path("github.com/istio/istio/pilot/pkg/proxy/envoy/v2")
        == "pilot/pkg/proxy/envoy/v2"
    )


def test_go():
    assert (
        get_files_loc_stat(
            go_get_version_diff_stats(
                "github.com/labstack/echo/middleware",
                "https://github.com/labstack/echo",
                "4.1.17",
                "4.2.0",
            )
        )
        == (27, 2461, 234)
    )

    assert (
        get_files_loc_stat(
            go_get_version_diff_stats(
                "github.com/crewjam/saml",
                "https://github.com/crewjam/saml",
                "0.4.2",
                "0.4.3",
            )
        )
        == (10, 179, 13)
    )


def get_files_loc_stat(files):
    # for k in files.keys():
    #     print(k, "\n::::::::::::::::::::::::::::::::::::::::\n", files[k])

    # for files only renamed,
    # need to filter out files with zero loc change

    changed_files = len(files)
    lines_added = lines_deleted = 0
    for k in files.keys():
        lines_added += files[k]["loc_added"]
        lines_deleted += files[k]["loc_removed"]
    return changed_files, lines_added, lines_deleted


def test_composer():
    assert get_files_loc_stat(
        get_version_diff_stats(
            COMPOSER, "psr/log", "https://github.com/php-fig/log", "1.1.4", "2.0.0"
        )
    ) == (10, 56, 430)

    assert (
        get_files_loc_stat(
            get_version_diff_stats(
                COMPOSER,
                "illuminate/auth",
                "https://github.com/illuminate/auth",
                "4.1.25",
                "4.1.26",
            )
        )
        == (6, 186, 13)
    )


def test_maven():
    assert (
        get_files_loc_stat(
            get_version_diff_stats(
                MAVEN,
                "com.github.junrar:junrar",
                "https://github.com/junrar/junrar.git",
                "1.0.0",
                "1.0.1",
            )
        )
        == (8, 40, 125)
    )

    assert (
        get_files_loc_stat(
            get_version_diff_stats(
                MAVEN,
                "org.togglz:togglz-console",
                "https://github.com/togglz/togglz",
                "2.9.3",
                "2.9.4",
            )
        )
        == (8, 88, 2)
    )


def test_npm():
    assert get_files_loc_stat(
        get_version_diff_stats(
            NPM, "lodash", "https://github.com/lodash/lodash", "4.11.0", "4.11.1"
        )
    ) == (12, 54, 44)

    assert (
        get_files_loc_stat(
            get_version_diff_stats(
                NPM,
                "set-value",
                "https://github.com/jonschlinkert/set-value",
                "3.0.0",
                "3.0.1",
            )
        )
        == (4, 23, 25)
    )


def test_nuget():
    assert (
        get_files_loc_stat(
            get_version_diff_stats(
                NUGET,
                "messagepack.immutablecollection",
                "https://github.com/neuecc/MessagePack-CSharp",
                "2.0.335",
                "2.1.80",
            )
        )
        == (1, 14, 6)
    )

    assert (
        get_files_loc_stat(
            get_version_diff_stats(
                NUGET,
                "microsoft.aspnetcore.server.kestrel.core",
                "https://github.com/aspnet/KestrelHttpServer",
                "2.0.2",
                "2.0.3",
            )
        )
        == (7, 89, 24)
    )


def test_pip():
    assert get_files_loc_stat(
        get_version_diff_stats(
            PIP, "meinheld", "https://github.com/mopemope/meinheld", "1.0.1", "1.0.2"
        )
    ) == (43, 6091, 6380)


def test_rubygems():
    # in below example, auto-generated file spec/example.txt causes a large diff
    assert get_files_loc_stat(
        get_version_diff_stats(
            RUBYGEMS, "yard", "https://github.com/lsegal/yard", "0.9.19", "0.9.20"
        )
    ) == (10, 1706, 1696)


def test_cargo():
    assert (
        get_files_loc_stat(
            get_version_diff_stats(
                CARGO,
                "guppy",
                "https://github.com/facebookincubator/cargo-guppy",
                "0.8.0",
                "0.9.0",
            )
        )
        == (9, 222, 171)
    )


def test_sanitize_repo_url():
    assert (
        sanitize_repo_url("https://github.com/nasifimtiazohi/version-differ/issues/1")
        == "https://github.com/nasifimtiazohi/version-differ"
    )
    assert (
        sanitize_repo_url(
            "https://gitlab.com/gitlab-org/charts/gitlab/-/tree/master/doc/architecture"
        )
        == "https://gitlab.com/gitlab-org/charts"
    )
