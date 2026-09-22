"""Refresh the 'latest videos' block from the channel RSS feed.
Pure stdlib. Keeps existing content if the feed is unreachable."""
import pathlib
import re
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
CHANNEL_ID = "UCVnU81s3bgoYLSgJ3wIdLdQ"
FEED = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
NS = {"a": "http://www.w3.org/2005/Atom", "m": "http://search.yahoo.com/mrss/"}

BEGIN = "<!-- BEGIN LATEST-VIDEOS -->"
END = "<!-- END LATEST-VIDEOS -->"


def fetch_entries(n=3):
    req = urllib.request.Request(FEED, headers={"User-Agent": "amire3m-profile/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        root = ET.fromstring(r.read())
    out = []
    for e in root.findall("a:entry", NS)[:n]:
        vid = e.find("a:id", NS).text.rsplit(":", 1)[-1]
        link = e.find("a:link", NS).attrib["href"]
        title = e.find("a:title", NS).text or "Latest cut"
        title = re.sub(r"\s+", " ", title).strip()
        out.append((vid, link, title))
    return out


def card(vid, link, title):
    safe = title.replace('"', "'")
    return (
        f'<a href="{link}">'
        f'<img width="32%" src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="{safe}" />'
        "</a>"
    )


def main():
    try:
        entries = fetch_entries()
    except Exception as exc:  # noqa: BLE001 - keep old block on failure
        print(f"feed unreachable, keeping existing block: {exc}")
        return
    if not entries:
        print("feed empty, keeping existing block")
        return
    block = (
        BEGIN + "\n<p align=\"center\">\n  "
        + "\n  ".join(card(*e) for e in entries)
        + "\n</p>\n" + END
    )
    text = README.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END), re.S)
    if not pattern.search(text):
        print("markers missing, nothing to update")
        return
    README.write_text(pattern.sub(block, text), encoding="utf-8")
    print(f"wrote {len(entries)} video cards")


if __name__ == "__main__":
    main()
