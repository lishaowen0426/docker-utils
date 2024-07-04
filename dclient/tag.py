import requests
from urllib.parse import urljoin
import urllib


class TagManager:
    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {
            "Accept": "application/vnd.docker.distribution.manifest.v2+json",
            "Content-type": "application/vnd.docker.distribution.manifest.v2+json",
        }

    def valid(self):
        resp = requests.get(self.base_url)
        resp.raise_for_status()

    def get_manifest(self, name, tag):
        url = urljoin(self.base_url, f"{name}/manifests/{tag}")
        resp = requests.get(
            url,
            headers={
                "Accept": "application/vnd.docker.distribution.manifest.v2+json",
            },
        )
        return resp

    def get_digest(self, name, tag):
        url = urljoin(self.base_url, f"{name}/manifests/{tag}")
        resp = requests.head(url, headers=self.headers)
        resp.raise_for_status()
        return resp.headers["Docker-Content-Digest"]

    def delete_image(self, name, tag):
        digest = self.get_digest(name, tag)
        url = urljoin(self.base_url, f"{name}/manifests/{digest}")
        resp = requests.delete(url, headers=self.headers)
        resp.raise_for_status()

    def retag(self, name, old_tag, new_tag):
        manifest = self.get_manifest(name, old_tag)
        if manifest.status_code == 404:
            print("old_tag does not exist...")
            return
        else:
            print(f"retag from {old_tag} to {new_tag}")
        url = urljoin(self.base_url, f"{name}/manifests/{new_tag}")
        resp = requests.put(
            url,
            headers={
                "Content-type": "application/vnd.docker.distribution.manifest.v2+json",
            },
            data=manifest.content,
        )
        resp.raise_for_status()
