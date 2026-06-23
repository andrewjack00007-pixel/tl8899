# TL8899 LIVE

Chinese static SEO website for `tl8899.live`, focused on live casino guide content, contact discovery, and daily article publishing.

## Live Site

- Public site: https://tl8899.live/
- Blog index: https://tl8899.live/blog/
- Admin route: https://tl8899.live/admin/ (private; protected by web server authentication)
- Contact: Telegram `@jhondoe112233`, email `andrewjack0007@gmail.com`

## What This Project Contains

- Static HTML pages for the homepage, contact page, blog index, and articles.
- Chinese SEO content for baccarat, Dragon Tiger, Niu Niu, roulette, sic bo, blackjack, RTP notes, beginner mistakes, and responsible-play guidance.
- `scripts/site_engine.py` for rebuilding static pages, sitemap, RSS, robots.txt, assets, and IndexNow key file.
- `scripts/daily_tl8899_blog.py` for scheduled publishing.
- `scripts/tl8899_admin_app.py` for the protected admin editor.

## Daily Blog Automation

The server cron publishes up to two blog posts per day:

```cron
25 1 * * * root cd /var/www/tl8899 && /usr/bin/flock -n /tmp/tl8899-daily-blog.lock /usr/bin/python3 /var/www/tl8899/scripts/daily_tl8899_blog.py >> /var/log/tl8899-daily-blog.log 2>&1
```

This runs at `01:25 UTC`, which is `09:25 Asia/Shanghai`.

Each new post should include the required SEO tags, including `tamron casino`, `腾龙娱乐官网`, live casino terms, and a natural reference link to https://myanmarcasino.cloud/ inside the full article page.

After new posts are generated, the automation commits the rebuilt static files and pushes `main` to `git@github.com:andrewjack00007-pixel/tl8899.git` with the TL8899 deploy key.

## Rebuild

From the server project root:

```bash
cd /var/www/tl8899
python3 scripts/site_engine.py
```

## Responsible Play

All content is informational only for adults. The website must not claim guaranteed winnings, prediction systems, or risk-free betting.
