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
from pygit2 import Repository, clone_repository, init_repository, Signature
from time import time
import pydriller
import tempfile
from git import Repo
import re


CARGO = "Cargo"
COMPOSER = "Composer"
GO = "Go"
MAVEN = "Maven"
NPM = "npm"
NUGET = "NuGet"
PIP = "pip"
RUBYGEMS = "RubyGems"

ecosystems = [CARGO, COMPOSER, GO, MAVEN, NPM, NUGET, PIP, RUBYGEMS]

def sanitize_repo_url(repo_url):
    http = 'https://'
    assert repo_url.startswith(http)
    
    # gitbox urls
    s='https://gitbox.apache.org/repos/asf?p='
    url = repo_url
    if url.startswith(s):
        url = url[len(s):]
        assert url.count('.git') == 1
        url = url[:url.find('.git')]
        return 'https://gitbox.apache.org/repos/asf/'+url

    
    s = repo_url[len(http):]

    #custom
    if s.startswith('svn.opensymphony.com'):
        return repo_url

    #below rule covers github, gitlab, bitbucket, foocode, eday, qt
    sources = ['github', 'gitlab', 'bitbucket', 'foocode', 'eday', 'q', 'opendev']
    flag = False
    for source in sources:
        if source in s:
            flag = True
    assert flag

    if s.endswith('.git'):
        s=s[:-len('.git')]
    s = http + '/'.join(s.split('/')[:3])

    return s

def get_commit_of_release(tags, package, version):
    '''tags is a gitpython object, while release is a string taken from ecosystem data'''
    version = version.strip()
    output_tag = None
    candidate_tags = tags

    # Now we check through a series of heuristics if tag matches a version
    version_formatted_for_regex = version.replace(".", "\\.")
    patterns = [
        # 1. Ensure the version part does not follow any digit between 1-9,
        # e.g., to distinguish betn 0.1.8 vs 10.1.8
        r"^(?:.*[^1-9])?{}$".format(version_formatted_for_regex),

        # 2. If still more than one candidate,
        # check the extistence of crate name
        r"^.*{}(?:.*[^1-9])?{}$".format(package, version_formatted_for_regex),

        # 3. check if  and only if crate name and version string is present
        # besides non-alphanumeric, e.g., to distinguish guppy vs guppy-summaries
        r"^.*{}\W*{}$".format(package, version_formatted_for_regex)
    ]

    for pattern in patterns:
        if output_tag:
            break

        pattern = re.compile(pattern)
        temp = []
        for tag in candidate_tags:
            if pattern.match(tag.name.strip()):
                temp.append(tag)
        candidate_tags = temp
        if len(candidate_tags) == 1:
            output_tag = candidate_tags[0]
    
    if output_tag:
        return output_tag.commit
    return None


def go_get_version_diff_stats(package, repo_url, old, new):
    if "github.com" not in repo_url:
        raise Exception("repository not github url")
    url = sanitize_repo_url(repo_url)

    temp_dir = tempfile.TemporaryDirectory()
    clone_repository(url, temp_dir)

    repo = Repo(temp_dir)
    assert not repo.bare 
    tags = repo.tags







def get_version_diff_stats(ecosystem, package, old, new):
    temp_dir_old = tempfile.TemporaryDirectory()
    url = get_package_version_source_url(ecosystem, package, old)
    if url:
        download_package_source(url, ecosystem, package, old, temp_dir_old.name)

    temp_dir_new = tempfile.TemporaryDirectory()
    url = get_package_version_source_url(ecosystem, package, new)
    if url:
        download_package_source(url, ecosystem, package, new, temp_dir_new.name)

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
                    try:
                        # extract the tar file and delete itself
                        t = tarfile.open(filepath)
                        t.extractall(path)
                        t.close()
                        os.remove(filepath)
                        flag = True
                    except:
                        if file == 'temp_data.tar.gz' or file == 'data.tar.gz':
                            raise Exception("cannot extract the main tar")
                        else:
                            # don't bother
                            pass

    return dest_file


def download_package_source(url, ecosystem, package, version, dir_path):
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
            temp = key
            if temp.startswith('v'):
                temp =  temp[1:]
            if temp == version:
                return data[key]["dist"]["url"]
        return None
    elif ecosystem == NPM:
        url = "https://registry.npmjs.org/{}".format(package)
        page = requests.get(url)
        data = json.loads(page.content)
        data = data["versions"]
        for key in data.keys():
            temp = key
            if temp.startswith('v'):
                temp =  temp[1:]
            if temp == version:
                return data[key]["dist"]["tarball"]
        return None
    elif ecosystem == PIP:
        url = "https://pypi.org/pypi/{}/json".format(package)
        page = requests.get(url)
        data = json.loads(page.content)
        data = data["releases"]
        for key in data.keys():
            temp = key
            if temp.startswith('v'):
                temp =  temp[1:]
            if temp == version:
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
