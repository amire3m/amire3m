"""Daily reel generator: re-tints the filmstrip divider with a day-seeded
gradient rotation and stamps the reel day. Pure stdlib, no dependencies."""
import datetime
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DAY = datetime.date.today().timetuple().tm_yday

HUES = [(123, 97, 255), (0, 229, 255), (255, 77, 109)]  # violet, cyan, rec-red
rot = DAY % 3
c = HUES[rot:] + HUES[:rot]
stops = "\n      ".join(
    f'<stop offset="{o}" stop-color="rgb({r},{g},{b})"/>'
    for (r, g, b), o in zip(c, (0, 0.5, 1))
)

divider = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="56" viewBox="0 0 1200 56">
  <defs>
    <linearGradient id="strip" x1="0" y1="0" x2="1" y2="0">
      {stops}
    </linearGradient>
    <pattern id="sp" width="40" height="56" patternUnits="userSpaceOnUse">
      <rect width="40" height="56" fill="#060512"/>
      <rect x="10" y="8" width="20" height="12" rx="2" fill="#2a2654"/>
      <rect x="10" y="36" width="20" height="12" rx="2" fill="#2a2654"/>
    </pattern>
  </defs>
  <rect width="1200" height="56" fill="url(#sp)"/>
  <rect x="70" y="24" width="960" height="4" fill="url(#strip)"/>
  <text x="1040" y="34" fill="#8f8ab8" font-size="13" font-family="monospace" letter-spacing="2">REEL DAY {DAY}</text>
</svg>
"""
(ROOT / "assets" / "divider.svg").write_text(divider, encoding="utf-8")
print(f"reel day {DAY} written")
