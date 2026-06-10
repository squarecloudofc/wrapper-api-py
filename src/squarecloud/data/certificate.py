from __future__ import annotations

import base64
import os
from typing import Literal

from .base import BaseDataClass


class Certificate(BaseDataClass):
    base64_certificate: str

    def _extract_block(self, block: str) -> bytes:
        decoded_certificate = base64.b64decode(self.base64_certificate)

        begin = f"-----BEGIN {block}-----".encode()
        end = f"-----END {block}-----".encode()

        start = decoded_certificate.find(begin)
        if start == -1:
            raise ValueError(f"{block} not found")

        final = decoded_certificate.find(end, start)
        if final == -1:
            raise ValueError(f"{block} not found")

        final += len(end)
        return decoded_certificate[start:final]

    def _save_pem(self, dir: str, filename: str):
        with open(os.path.join(dir, filename + '.pem'), 'wb') as file:
            file.write(base64.b64decode(self.base64_certificate))

    def _save_cert(self, dir: str, filename: str):
        with open(os.path.join(dir, filename + '.crt'), 'wb') as file:
            file.write(self._extract_block('CERTIFICATE'))

    def _save_key(self, dir: str, filename: str):
        with open(os.path.join(dir, filename + '.key'), 'wb') as file:
            file.write(self._extract_block('PRIVATE KEY'))

    def _get_backend(self, ext: str):
        try:
            return getattr(self, f"_save_{ext}")
        except AttributeError:
            raise ValueError('Invalid certificate format')

    def save(
        self,
        *,
        dir: str = 'certs',
        filename: str = 'certificate',
        export_to: Literal['pem', 'cert', 'key'] = 'pem'
    ) -> None:
        backend = self._get_backend(export_to)

        os.makedirs(dir, exist_ok=True)
        backend(dir, filename)
