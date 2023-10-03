from typing import Set
from pathlib import Path
from ..constants import PROVIDER_URL, GITIGNORE_DOWNLOAD
from ..provider import download_gitignore


def update(template: Set[str], url: str = PROVIDER_URL) -> None:
    download_gitignore(Path(GITIGNORE_DOWNLOAD), template, url)
    pass
