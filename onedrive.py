import asyncio
import os
from base64 import b64encode
from typing import Optional

import aiofiles
import aiohttp
from requests import Session


class OneDrive:
    """
    Downloads shared file/folder to localhost with persisted structure.

    params:
    `str:url`: url to the shared one drive folder or file
    `str:path`: local filesystem path

    methods:
    `download() -> None`: fire async download of all files found in URL
    """

    def __init__(self, url: Optional[str] = None, path: Optional[str] = None) -> None:
        if not (url and path):
            raise ValueError("URL to shared resource or path to download is missing.")

        self.url = url
        data_bytes64 = b64encode(bytes(url, "utf-8"))
        self.compiled_url = (
            data_bytes64.decode("utf-8").replace("/", "_").replace("+", "-").rstrip("=")
        )
        self.path = path
        self.prefix = "https://api.onedrive.com/v1.0/shares/u!"
        self.suffix = "/root?expand=children"
        self.session = Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
            }
        )

    def _token(self, url: str) -> str:
        return "u!" + b64encode(url.encode()).decode()

    def _traverse_url(self, url: str, name: str = "") -> None:
        """Traverse the folder tree and store leaf urls with filenames"""

        r = self.session.get(f"{self.prefix}{url}{self.suffix}").json()
        name = name + os.sep + r["name"]

        # shared file
        if not r["children"]:
            file: dict[str, str] = {}
            file["name"] = name.lstrip(os.sep)
            file["url"] = r["@content.downloadUrl"]
            self.to_download.append(file)
            print(f"Found {file['name']}")

        # shared folder
        for child in r["children"]:
            print(child["name"])
            if "folder" in child:
                encoded_url = b64encode(bytes(child["webUrl"], "utf-8"))
                self._traverse_url(
                    encoded_url.decode("utf-8")
                    .replace("/", "_")
                    .replace("+", "-")
                    .rstrip("="),
                    name,
                )

            if "file" in child:
                file = {}
                file["name"] = (name + os.sep + child["name"]).lstrip(os.sep)
                file["url"] = child["@content.downloadUrl"]
                self.to_download.append(file)
                print(f"Found {file['name']}")

    async def _download_file(
        self, file: dict[str, str], session: aiohttp.ClientSession
    ) -> None:
        async with session.get(file["url"], timeout=None) as r:
            filename = os.path.join(self.path, file["name"])
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            async with aiofiles.open(filename, "wb") as f:
                async for chunk in r.content.iter_chunked(1024 * 16):
                    if chunk:
                        await f.write(chunk)

        self.downloaded += 1
        progress = int(self.downloaded / len(self.to_download) * 100)
        print(f"Download progress: {progress}%")

    async def _downloader(self) -> None:
        async with aiohttp.ClientSession() as session:
            await asyncio.wait(
                [self._download_file(file, session) for file in self.to_download]
            )

    def download(self) -> None:
        print("Traversing public folder\n")
        self.to_download: list[dict[str, str]] = []
        self.downloaded = 0
        self._traverse_url(self.compiled_url)

        print("\nStarting async download\n")
        asyncio.get_event_loop().run_until_complete(self._downloader())
