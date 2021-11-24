from itertools import islice
from base64 import b64encode
from pathlib import Path
import httpx
import trio
import os
import io


def url_to_id(url: str) -> str:
    return (
        b64encode(url.encode()).decode().replace("/", "_").replace("+", "-").rstrip("=")
    )


def chunks(it: dict[str, str], size: int) -> tuple:
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


class OneDriveSharedFolder:
    def __init__(self, root_url: str) -> None:
        self._root_url = root_url
        self._api = "https://api.onedrive.com/v1.0/shares/u!"
        self._client = httpx.AsyncClient(timeout=300)
        self._files = {}
        self._downloaded_files = 0

    async def _traverse_url(self, url: str, name: str = "") -> None:
        url = self._api + url_to_id(url) + "/root?expand=children"
        r = (await self._client.get(url)).json()
        name = name + os.sep + r.get("name")

        if not r.get("children"):
            path = name.lstrip(os.sep)
            self._files[path] = r.get("@content.downloadUrl")

        for child in r.get("children"):
            if "folder" in child:
                await self._traverse_url(child.get("webUrl"), name)

            if "file" in child:
                path = (name + os.sep + child.get("name")).lstrip(os.sep)
                self._files[path] = child.get("@content.downloadUrl")

    async def _download(self, file: str) -> None:
        buff = io.BytesIO()
        async with self._client.stream("GET", self._files.get(file)) as r:
            async for chunk in r.aiter_bytes():
                buff.write(chunk)

        p = Path(file)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(buff.getvalue())
        self._downloaded_files += 1
        print(
            f"Download progress: {(self._downloaded_files / len(self._files))*100:.2f}%"
        )

    def download(self, path: str = ".", concurrent_reqs: int = 5) -> None:
        async def _runner() -> None:
            print("Traversing directory tree..")
            await self._traverse_url(self._root_url)
            print(f"Found {len(self._files)} files, going to download them..")

            for chunk in chunks(self._files, concurrent_reqs):
                async with trio.open_nursery() as n:
                    for file in chunk:
                        n.start_soon(self._download, file)

            await self._client.aclose()

        trio.run(_runner)
