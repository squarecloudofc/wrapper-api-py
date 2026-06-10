from __future__ import annotations

import os
import zipfile

from ..http import HTTPClient


class Snapshot:
    """
    Snapshot data class

    :ivar url: Url for download your Snapshot
    :ivar key: The Snapshot's key

    :type url: str
    :type key: str
    """

    __slots__ = ('url', 'key')

    def __init__(self, url: str, key: str) -> None:
        self.url = url
        self.key = key

    def to_dict(self) -> dict[str, str]:
        return {'url': self.url, 'key': self.key}

    async def download(self, path: str = './') -> zipfile.ZipFile:
        file_name = os.path.basename(self.url.split('?')[0])
        content = await HTTPClient.fetch_snapshot_content(self.url)
        with zipfile.ZipFile(f'{path}/{file_name}', 'w') as zip_file:
            zip_file.writestr(f'{path}/{file_name}', content)
            return zip_file
