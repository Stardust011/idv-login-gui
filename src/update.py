import aiohttp
import requests

from src.runtimeLog import runtime_log


def get_idv_login_github_releases_json():
    url = f"https://api.github.com/repos/Alexander-Porter/idv-login/releases"
    response = requests.get(url)

    if response.status_code != 200:
        runtime_log.warning(f"Failed to fetch github releases: {response.status_code}")
        url = f"https://api.kkgithub.com/repos/Alexander-Porter/idv-login/releases"
        response = requests.get(url)
    if response.status_code != 200:
        runtime_log.warning(f"Failed to fetch mirror releases: {response.status_code}")
    releases = response.json()
    return releases


def parse_release(releases):
    parsed_releases = []
    for release in releases:
        parsed_release = {
            'tag_name': release['tag_name'],
        }
        asset_list = []
        for asset in release['assets']:
            parsed_asset = {
                'name': asset['name'],
                'download_url': asset['browser_download_url'],
            }
            asset_list.append(parsed_asset)
        parsed_release['assets'] = asset_list
        parsed_releases.append(parsed_release)
    return parsed_releases


def get_download_url(tag_name, asset_name, parsed_releases):
    for release in parsed_releases:
        if release['tag_name'] == tag_name:
            for asset in release['assets']:
                if asset['name'] == asset_name:
                    download_url = asset['download_url']
                    return download_url, f'{download_url}.sha256'


class UpdateIDVLogin:
    def __init__(self):
        self.releases = get_idv_login_github_releases_json()
        self.parsed_releases = parse_release(self.releases)
        self.progress = 0

    def get_download_url(self, tag_name, asset_name):
        return get_download_url(tag_name, asset_name, self.parsed_releases)

    async def async_download_file(self, url, dest):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    runtime_log.warning(f"Failed to download file: {response.status}")
                    return None
                total_size = int(response.headers.get('content-length', 0))
                chunk_size = 1024
                downloaded_size = 0
                with open(dest, 'wb') as f:
                    async for chunk in response.content.iter_chunked(chunk_size):
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        self.progress = downloaded_size / total_size * 100
        return dest


# Example usage
if __name__ == '__main__':
    # owner = 'octocat'  # Replace with the repository owner
    # repo = 'Hello-World'  # Replace with the repository name
    releases = get_idv_login_github_releases_json()
    releases = parse_release(releases)
    for release in releases:
        print(release)
        # print(f"Release: {release['name']} - Tag: {release['tag_name']}")
