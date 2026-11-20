# news-image-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/reronalendra/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/reronalendra/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

Thursday 19 November 2026, on one page: a newspaper front page drawn
entirely in code. The lead is the first-ever three-way meeting of Xi
Jinping, Donald Trump and Vladimir Putin at the APEC summit in Shenzhen,
which ended in a joint "peace declaration" covering nuclear risk, energy
and UN reform. Around it, six panels carry the rest of the day — GTA VI
going on sale, a third strike on the Crimean bridge, a tanker hit off
Oman, Cyclone Akvan nearing India, Anthropic's record $81.3B IPO, and
Ukraine's allies meeting in Berlin — plus a record $190.4m Van Gogh sale
in the "Also today" strip.

`build_image.py` draws the page with Pillow (DejaVu fonts, no photos, no
copied art) and writes `entry.png` (1024×1024). `main.ts` copies that
image to the output directory the grader reads.

## Run it

```sh
python3 build_image.py
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=2s61jrxf&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>
