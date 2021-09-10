"""Main module."""

"""
1. get file for two versions
2. setup git repo
3. add a repo as a remote branch to another 
4. get git diff
"""

import requests
import json
import os
from zipfile import ZipFile
import tarfile
from pygit2 import Repository, init_repository, Signature
from time import time
import pydriller
import tempfile


CARGO = "Cargo"
COMPOSER = "Composer"
GO = "Go"
MAVEN = "Maven"
NPM = "npm"
NUGET = "NuGet"
PIP = "pip"
RUBYGEMS = "RubyGems"

ecosystems = [CARGO, COMPOSER, GO, MAVEN, NPM, NUGET, PIP, RUBYGEMS]


def get_version_diff_stats(ecosystem, package, old, new):
    temp_dir_old = tempfile.TemporaryDirectory()
    download_package_source(ecosystem, package, old, temp_dir_old.name)

    temp_dir_new = tempfile.TemporaryDirectory()
    download_package_source(ecosystem, package, new, temp_dir_new.name)

    repo_old, oid_old = init_git_repo(temp_dir_old.name)
    repo_new, oid_new = init_git_repo(temp_dir_new.name)

    setup_remote(repo_old, temp_dir_new.name)

    stats = get_diff_stats(temp_dir_old.name, oid_old, oid_new)

    temp_dir_old.cleanup()
    temp_dir_new.cleanup()
    return stats 
    
def get_maven_pacakge_url(package):
    url = "https://repo1.maven.org/maven2/" + package.replace(".", "/").replace(
        ":", "/"
    )
    if requests.get(url).status_code == 200:
        return url

    s1, s2 = package.split(":")
    url = "https://repo1.maven.org/maven2/" + s1.replace(".", "/") + "/" + s2
    if requests.get(url).status_code == 200:
        return url
    else:
        return None


def download_zipped(url, path):
    # download content in a zipped format
    dest_file = "{}/temp_data.zip".format(path)

    r = requests.get(url, stream=True)
    with open(dest_file, "wb") as output_file:
        output_file.write(r.content)

    z = ZipFile(dest_file, "r")
    z.extractall(path)
    z.close()

    os.remove(dest_file)

    return dest_file


def download_tar(url, path):
    # download content in a zipped format
    dest_file = "{}/temp_data.tar.gz".format(path)
    r = requests.get(url)
    with open(dest_file, "wb") as output_file:
        output_file.write(r.content)

    flag = True
    while flag:
        flag = False
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith("tar.gz"):
                    filepath = "{}/{}".format(root, file)
                    flag = True
                    # extract the tar file and delete itself
                    t = tarfile.open(filepath)
                    t.extractall(path)
                    t.close()
                    os.remove(filepath)

    return dest_file


def download_package_source(ecosystem, package, version, dir_path):
    url = get_package_version_source_url(ecosystem, package, version)
    print(
        "fetching {}-{} in {} ecosystem from {}".format(
            package, version, ecosystem, url
        )
    )
    # First try based on file extension
    if (
        url.endswith(".whl")
        or url.endswith(".jar")
        or url.endswith(".nupkg")
        or url.endswith(".zip")
    ):
        download_zipped(url, dir_path)
    elif (
        url.endswith(".gz")
        or url.endswith(".crate")
        or url.endswith(".gem")
        or url.endswith(".tgz")
    ):
        download_tar(url, dir_path)
    elif ecosystem == COMPOSER or ecosystem == NUGET or ecosystem == MAVEN:
        download_zipped(url, dir_path)
    elif (
        ecosystem == NPM
        or ecosystem == PIP
        or ecosystem == RUBYGEMS
        or ecosystem == CARGO
    ):
        download_tar(url, dir_path)
    else:
        # TODO Go
        pass


def get_package_version_source_url(ecosystem, package, version):
    assert ecosystem in ecosystems

    if ecosystem == CARGO:
        return "https://crates.io/api/v1/crates/{}/{}/download".format(package, version)
    elif ecosystem == COMPOSER:
        url = "https://repo.packagist.org/packages/{}.json".format(package)
        page = requests.get(url)
        data = json.loads(page.content)
        data = data["package"]["versions"]
        for key in data.keys():
            if key.startswith('v'):
                key = key[1:]
            if key == version:
                return data[key]["dist"]["url"]
        return None
    elif ecosystem == NPM:
        url = "https://registry.npmjs.org/{}".format(package)
        page = requests.get(url)
        data = json.loads(page.content)
        data = data["versions"]
        for key in data.keys():
            if key.startswith('v'):
                key = key[1:]
            if key == version:
                return data[key]["dist"]["tarball"]
        return None
    elif ecosystem == PIP:
        url = "https://pypi.org/pypi/{}/json".format(package)
        page = requests.get(url)
        data = json.loads(page.content)
        data = data["releases"]
        for key in data.keys():
            if key.startswith('v'):
                key = key[1:]
            if key == version:
                return data[key][-1]["url"]
        return None
    elif ecosystem == NUGET:
        return "https://www.nuget.org/api/v2/package/{}/{}".format(package, version)
    elif ecosystem == RUBYGEMS:
        return "https://rubygems.org/downloads/{}-{}.gem".format(package, version)
    elif ecosystem == MAVEN:
        url = get_maven_pacakge_url(package)
        if url:
            artifact = package.split(":")[1]
            url = "{}/{}/{}-{}-sources.jar".format(url, version, artifact, version)
            if requests.get(url).status_code == 200:
                return url
        return None


def init_git_repo(path):
    repo = init_repository(path)
    index = repo.index
    index.add_all()
    index.write()  # is this line necessary?
    tree = index.write_tree()
    sig1 = Signature("user", "email@domain.com", int(time()), 0)
    oid = repo.create_commit(
        "refs/heads/master", sig1, sig1, "Initial commit", tree, []
    )
    return repo, oid


def setup_remote(repo, url):
    remote_name = "remote"
    repo.create_remote(remote_name, url)
    remote = repo.remotes[remote_name]
    remote.connect()
    remote.fetch()


def get_diff_stats(repo_path, commit_a, commit_b):
    files = {}

    for commit in pydriller.Repository(
        repo_path, from_commit=commit_a, to_commit=commit_b, only_no_merge=True
    ).traverse_commits():

        for m in commit.modified_files:
            file = m.new_path
            if not file:
                file = m.old_path
            assert file

            if file not in files:
                files[file] = {"loc_added": 0, "loc_removed": 0}

            files[file]["loc_added"] += m.added_lines
            files[file]["loc_removed"] += m.deleted_lines

    return files
