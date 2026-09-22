"""Refresh the 'latest videos' block by scraping the channel videos page.
Pure stdlib. Keeps existing content if the page is unreachable."""
import pathlib
import re
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
VIDEOS_URL = "https://www.youtube.com/@amire3m/videos"

BEGIN = "<!-- BEGIN LATEST-VIDEOS -->"
END = "<!-- END LATEST-VIDEOS -->"
ID_RE = re.compile(r'"videoId":"([A-Za-z0-9_-]{11})"')
TITLE_RE = re.compile(r'"title":\{"runs":\[{"text":"((?:[^"\\]|\\.)*)"')


def fetch_latest(n=3):
    req = urllib.request.Request(
        VIDEOS_URL,
        headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode("utf-8", "ignore")
    seen, out = set(), []
    for m in ID_RE.finditer(html):
        vid = m.group(1)
        if vid in seen:
            continue
        seen.add(vid)
        tail = html[m.end() : m.end() + 4000]
        tm = TITLE_RE.search(tail)
        title = "Latest cut"
        if tm:
            title = tm.group(1).encode().decode("unicode_escape", "ignore")
            title = re.sub(r"\s+", " ", title).strip()[:80]
        out.append((vid, f"https://www.youtube.com/watch?v={vid}", title))
        if len(out) == n:
            break
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
        entries = fetch_latest()
    except Exception as exc:  # noqa: BLE001 - keep old block on failure
        print(f"page unreachable, keeping existing block: {exc}")
        return
    if not entries:
        print("no videos found, keeping existing block")
        return
    block = (
        BEGIN + '\n<p align="center">\n  '
        + "\n  ".join(card(*e) for e in entries)
        + "\n</p>\n" + END
    )
    text = README.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END), re.S)
    if not pattern.search(text):
        print("markers missing, nothing to update")
        return
    README.write_text(pattern.sub(block, text), encoding="utf-8")
    print("wrote:", [t for _, _, t in entries])


if __name__ == "__main__":
    main()
