# Lint as: python3
"""Download replay packs via Blizzard Game Data APIs."""

# pylint: disable=bad-indentation, line-too-long

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import collections
import configparser
import itertools
import json
import logging
import os
import requests
import shutil
import subprocess
import sys

try:
    import mpyq
except ImportError:
    logging.warning(
        'Failed to import mpyq; version and corruption detection is disabled.')
    mpyq = None
from six import print_ as print  # To get access to `flush` in python 2.

API_BASE_URL = 'https://us.api.blizzard.com'
API_NAMESPACE = 's2-client-replays'

config = configparser.ConfigParser()
config.read("../settings.conf")

class RequestError(Exception):
    pass


def mkdirs(path):
    if not os.path.exists(path):
        os.makedirs(path)


def print_part(*args):
    print(*args, end='', flush=True)


class BnetAPI(object):
    """Represents a handle to the battle.net api."""

    def __init__(self, key, secret):
        headers = {'Content-Type': 'application/json'}
        params = {'grant_type': 'client_credentials'}
        response = requests.post('https://us.battle.net/oauth/token',
                                 headers=headers, params=params,
                                 auth=requests.auth.HTTPBasicAuth(config["download"]["key"], 
                                 config["download"]["secret"]))
        if response.status_code != requests.codes.ok:
            raise RequestError(
                'Failed to get oauth access token. response={}'.format(response))
        response = json.loads(response.text)
        if 'access_token' in response:
            self._token = response['access_token']
        else:
            raise RequestError(
                'Failed to get oauth access token. response={}'.format(response))

    def get(self, url, params=None):
        """Make an autorized get request to the api by url."""
        params = params or {}
        params['namespace'] = API_NAMESPACE,
        headers = {'Authorization': 'Bearer ' + self._token}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != requests.codes.ok:
            raise RequestError(
                'Request to "{}" failed. response={}'.format(url, response))
        response_json = json.loads(response.text)
        if response_json.get('status') == 'nok':
            raise RequestError(
                'Request to "{}" failed. response={}'.format(
                    url, response_json.get('reason')))
        return response_json

    def url(self, path):
        return requests.compat.urljoin(API_BASE_URL, path)

    def get_base_url(self):
        return self.get(self.url('/data/sc2/archive_url/base_url'))['base_url']

    def search_by_client_version(self, client_version):
        """Search for replay archives by version."""
        meta_urls = []
        for page in itertools.count(1):
            params = {
                'client_version': client_version,
                '_pageSize': 100,
                '_page': page,
            }
            response = self.get(self.url('/data/sc2/search/archive'), params)
            for result in response['results']:
                assert result['data']['client_version'] == client_version
                meta_urls.append(result['key']['href'])
            if response['pageCount'] <= page:
                break
        return meta_urls


def main():
    """Download the replays for a specific vesion. Check help below."""
    # Get OAuth token from us region
    api = BnetAPI(config["download"]["key"], config["download"]["secret"])

    # Get meta file infos for the give client version
    print('Searching replay packs with client version:', config["global"]["version"])
    meta_file_urls = api.search_by_client_version(config["global"]["version"])
    if len(meta_file_urls) == 0:
        sys.exit('No matching replay packs found for the client version!')

    # Download replay packs.
    download_base_url = api.get_base_url()
    print('Found {} replay packs'.format(len(meta_file_urls)))
    print('Downloading to:', config["download"]["download_dir"])
    print('Extracting to:', config["download"]["extract_dir"])
    mkdirs(config["download"]["download_dir"])
    for i, meta_file_url in enumerate(sorted(meta_file_urls), 1):
        # Construct full url to download replay packs
        meta_file_info = api.get(meta_file_url)
        archive_url = requests.compat.urljoin(download_base_url,
                                              meta_file_info['path'])

        print_part('{}/{}: {} ... '.format(i, len(meta_file_urls), archive_url))

        file_name = archive_url.split('/')[-1]
        file_path = os.path.join(config["download"]["download_dir"], file_name)

        with requests.get(archive_url, stream=True) as response:
            content_length = int(response.headers['Content-Length'])
            print_part(content_length // 1024**2, 'Mb ... ')
            if (not os.path.exists(file_path) or
                    os.path.getsize(file_path) != content_length):
                with open(file_path, 'wb') as f:
                    shutil.copyfileobj(response.raw, f)
                print_part('downloaded')
            else:
                print_part('found')

        if config["download"]["extract"]:
            print_part(' ... extracting')
            if os.path.getsize(file_path) <= 22:  # Size of an empty zip file.
                print_part(' ... zip file is empty')
            else:
                subprocess.call(['unzip', '-P', 'iagreetotheeula', '-u', '-o',
                                 '-q', '-d', config["download"]["extract_dir"], file_path])
            if config["download"]["remove"]:
                os.remove(file_path)
        print()

    if mpyq is not None:
        print('Filtering replays.')
        found_versions = collections.defaultdict(int)
        found_str = lambda: ', '.join('{}: {}'.format(v, c)
                                      for v, c in sorted(found_versions.items()))
        all_replays = [f for f in os.listdir(config["download"]["extract_dir"]) if f.endswith('.SC2Replay')]
        for i, file_name in enumerate(all_replays):
            if i % 100 == 0:
                print_part('\r{}/{}: {:.1f}%, found: {}'.format(
                    i, len(all_replays), 100 * i / len(all_replays), found_str()))
            file_path = os.path.join(config["download"]["extract_dir"], file_name)
            with open(file_path, 'rb') as fd:
                try:
                    archive = mpyq.MPQArchive(fd).extract()
                    metadata = json.loads(
                        archive[b'replay.gamemetadata.json'].decode('utf-8'))
                except KeyboardInterrupt:
                  raise
                except:  # pylint: disable=bare-except
                    found_versions['corrupt'] += 1
                    os.remove(file_path)
                    continue
            game_version = '.'.join(metadata['GameVersion'].split('.')[:-1])
            found_versions[game_version] += 1
            if config["download"]["filter"] == 'sort':
                version_dir = os.path.join(config["download"]["extract_dir"], game_version)
                if found_versions[game_version] == 1:  # First one of this version.
                    mkdirs(version_dir)
                os.rename(file_path, os.path.join(version_dir, file_name))
            elif config["download"]["filter"] == 'delete':
                if game_version != config["global"]["version"]:
                    os.remove(file_path)
        print('\nFound replays:', found_str())


if __name__ == '__main__':
    main()
