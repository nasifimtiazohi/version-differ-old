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


CARGO = "Cargo"
COMPOSER = "Composer"
GO = "Go"
MAVEN = "Maven"
NPM = "npm"
NUGET = "NuGet"
PIP = "pip"
RUBYGEMS = "RubyGems"

ecosystems = [CARGO, COMPOSER, GO, MAVEN, NPM, NUGET, PIP, RUBYGEMS]


def get_stats(ecosystem, pacakge, old, new):
    print(ecosystem, pacakge, old, new)


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
                print(file)
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
    if ecosystem == COMPOSER or ecosystem == NUGET or ecosystem == MAVEN:
        download_zipped(url, dir_path)
    elif ecosystem == NPM or ecosystem == PIP or ecosystem == RUBYGEMS:
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
            if key == version:
                return data[key]["dist"]["url"]
        return None
    elif ecosystem == NPM:
        url = "https://registry.npmjs.org/{}".format(package)
        page = requests.get(url)
        data = json.loads(page.content)
        data = data["versions"]
        for key in data.keys():
            if key == version:
                return data[key]["dist"]["tarball"]
        return None
    elif ecosystem == PIP:
        url = "https://pypi.org/pypi/{}/json".format(package)
        page = requests.get(url)
        data = json.loads(page.content)
        data = data["releases"]
        for key in data.keys():
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
    index.write() # is this line necessary?
    tree = index.write_tree()
    sig1 = Signature('user', 'email@domain.com', int(time()), 0)
    oid = repo.create_commit('refs/heads/master', sig1, sig1, 'Initial commit', tree, [])
    return repo, oid

def setup_remote(repo, url):
    remote_name = "remote"
    repo.create_remote(remote_name, url)
    remote = repo.remotes[remote_name]
    remote.connect()
    remote.fetch()


    


