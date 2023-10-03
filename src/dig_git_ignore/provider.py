from typing import List
from urllib.request import urlopen, Request
from .constants import PROVIDER_URL  # pylint: disable=relative-beyond-top-level


def get_templates(url: str = PROVIDER_URL) -> List[str]:
    output: List[str] = []
    with urlopen(Request(url + "list", headers={"User-Agent": "Python"})) as request:
        response: str = request.read().decode("utf-8")
        for line in response.splitlines():
            output.extend(line.split(","))
    return output
