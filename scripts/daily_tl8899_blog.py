#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import email.utils
import html
import json
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None


ROOT = Path("/var/www/tl8899")
SITE = "https://tl8899.live"
DOMAIN = "tl8899.live"
SERVER_IP = "76.13.216.172"
CONTACT_EMAIL = "andrewjack0007@gmail.com"
TELEGRAM = "@jhondoe112233"
TELEGRAM_URL = "https://t.me/jhondoe112233"
INDEXNOW_KEY = "f64254d0a708461e8b1f2fce8eee9c30"
INDEXNOW_KEY_LOCATION = f"{SITE}/{INDEXNOW_KEY}.txt"
ASSET_VERSION = "2026062303"

KEYWORDS = [
    "TL8899",
    "tl8899.live",
    "腾龙公司",
    "腾龙娱乐官网",
    "皇家在线公司",
    "tamron casino",
    "真人娱乐",
    "真人娱乐场",
    "百家乐",
    "龙虎",
    "牛牛",
    "live casino",
    "baccarat",
    "dragon tiger",
    "niu niu",
    "bull bull",
    "Telegram @jhondoe112233",
]


TOPICS = [
    {
        "slug_base": "baccarat-banker-player-flow",
        "topic": "Baccarat",
        "title": "TL8899 LIVE：百家乐庄闲流程与风险说明",
        "en_title": "Baccarat Banker and Player Flow Guide",
        "desc": "Chinese and English TL8899 guide to baccarat Banker, Player, Tie, commission notes, table flow and responsible play.",
        "teaser": "百家乐庄、闲、和的基础流程，适合新手先理解桌面规则与风险。",
        "intro_cn": "百家乐在亚洲真人娱乐内容里很常见，节奏快、规则短，但每一桌仍要先看清佣金、限红、和局赔付与补牌规则。",
        "intro_en": "Baccarat is simple to learn, but a careful player still checks table limits, commission rules, Tie payout and live-table interruptions before playing.",
        "rows": [
            ("庄 Banker", "常见为较低优势选项，但可能有佣金或免佣变体。"),
            ("闲 Player", "流程直观，赔付通常为 1:1。"),
            ("和 Tie", "赔率高但波动大，新手不应把高赔率理解为更容易出现。"),
        ],
    },
    {
        "slug_base": "dragon-tiger-card-ranking",
        "topic": "Dragon Tiger",
        "title": "TL8899 LIVE：龙虎牌面大小与和局风险",
        "en_title": "Dragon Tiger Card Ranking and Tie Risk",
        "desc": "Bilingual TL8899 Dragon Tiger guide covering Dragon, Tiger, Tie, card ranking, table limits and safer beginner habits.",
        "teaser": "龙虎只有两张主牌，重点是理解大小比较、和局风险和桌面限额。",
        "intro_cn": "龙虎玩法来自简单的高牌比较：龙位与虎位各发一张牌，点数高的一方胜。规则短，但和局赔率与扣半规则要特别注意。",
        "intro_en": "Dragon Tiger is fast because only two main cards decide the result. The key is not speed; the key is knowing the Tie rule and the table's settlement notes.",
        "rows": [
            ("龙 Dragon", "押龙位牌面较高，通常按 1:1 结算。"),
            ("虎 Tiger", "押虎位牌面较高，规则与龙位相同。"),
            ("和 Tie", "赔率看起来吸引人，但命中率低且部分规则会影响主注结算。"),
        ],
    },
    {
        "slug_base": "niu-niu-bull-bull-hand-values",
        "topic": "Niu Niu",
        "title": "TL8899 LIVE：牛牛牌型、倍数与新手规则",
        "en_title": "Niu Niu Bull Bull Hand Values",
        "desc": "TL8899 bilingual guide to Niu Niu hand building, Bull values, multiplier tables, live dealer timing and responsible play.",
        "teaser": "牛牛要先找三张成十的组合，再判断剩余两张的牛数与倍数。",
        "intro_cn": "牛牛的乐趣在于五张牌的组合判断：先找三张合计为十的倍数，再用剩下两张计算牛几。不同场馆倍数表可能不同。",
        "intro_en": "Niu Niu rewards rule knowledge more than speed. Always read the multiplier table before comparing hands or raising stakes.",
        "rows": [
            ("无牛 No Bull", "找不到三张成十组合时通常为较低牌型。"),
            ("牛一至牛九", "剩余两张点数决定牛数，倍数按桌面表执行。"),
            ("牛牛 Bull Bull", "较高牌型，但具体倍率以供应商规则为准。"),
        ],
    },
    {
        "slug_base": "live-hall-table-etiquette",
        "topic": "Live Hall",
        "title": "TL8899 LIVE：真人大厅流程、礼仪与联系指南",
        "en_title": "Live Dealer Table Flow and Etiquette",
        "desc": "TL8899 live dealer guide for lobby selection, dealer timing, table chat etiquette, contact information and responsible-play reminders.",
        "teaser": "进入真人大厅前，先看桌台限额、开牌节奏、规则面板和客服联系方式。",
        "intro_cn": "真人大厅的体验不只是画面漂亮，还包括网络稳定、下注倒计时、桌台限额、规则面板和客服联系是否清楚。",
        "intro_en": "A better live-casino session starts before the first bet: choose a table slowly, read the panel, and keep contact details handy.",
        "rows": [
            ("桌台限额", "确认最低、最高投注与单局限制。"),
            ("倒计时", "真人桌有固定下注窗口，延迟时不要强行追单。"),
            ("联系渠道", f"Telegram {TELEGRAM} 与邮箱 {CONTACT_EMAIL} 应清楚展示。"),
        ],
    },
    {
        "slug_base": "roulette-inside-outside-bets",
        "topic": "Roulette",
        "title": "TL8899 LIVE：轮盘内围外围投注与波动",
        "en_title": "Roulette Inside and Outside Bets",
        "desc": "Bilingual roulette guide for TL8899 readers covering inside bets, outside bets, wheel variants, payout notes and responsible play.",
        "teaser": "轮盘要区分内围、外围、欧式、美式和赔率差异，不能只看数字漂亮。",
        "intro_cn": "轮盘的视觉效果强，但规则核心是赔率与概率的交换。外围投注命中率较高、赔率较低；内围投注赔率高、波动也更大。",
        "intro_en": "Roulette is a probability game. Understand the difference between European and American wheels before comparing payouts.",
        "rows": [
            ("外围 Outside", "红黑、单双、大小等，赔率较低但结果范围更宽。"),
            ("内围 Inside", "直选、分注、街注等，赔率高但波动大。"),
            ("轮盘变体", "欧式单零通常与美式双零有不同理论回报。"),
        ],
    },
    {
        "slug_base": "sic-bo-dice-bets",
        "topic": "Sic Bo",
        "title": "TL8899 LIVE：骰宝大小、围骰与赔率说明",
        "en_title": "Sic Bo Dice Bets and Payout Notes",
        "desc": "TL8899 Sic Bo guide in Chinese and English covering Big Small, triples, totals, payout tables, volatility and beginner mistakes.",
        "teaser": "骰宝看起来热闹，实际要重点看大小、点数、围骰与赔率表。",
        "intro_cn": "骰宝使用三颗骰子，常见选项包括大小、总点数、对子、围骰。新手容易被高赔率吸引，却忽略出现概率。",
        "intro_en": "Sic Bo is easy to watch and easy to misunderstand. Higher payout usually means lower frequency, so read the payout table first.",
        "rows": [
            ("大 / 小", "常见基础选项，但遇到围骰时规则可能排除。"),
            ("总点数", "赔率随点数出现概率变化。"),
            ("围骰 Triple", "赔率高、波动大，不适合作为追回亏损的方法。"),
        ],
    },
    {
        "slug_base": "blackjack-basic-rules",
        "topic": "Blackjack",
        "title": "TL8899 LIVE：21点基础规则与常见决定",
        "en_title": "Blackjack Basic Rules and Decisions",
        "desc": "TL8899 blackjack guide covering hit, stand, double, split, dealer rules, payout notes and responsible budget control.",
        "teaser": "21点要先看庄家规则、Blackjack 赔率、分牌和加倍限制。",
        "intro_cn": "21点比百家乐更依赖规则细节。庄家软 17、Blackjack 赔付、可否投降、分牌限制都会影响桌面体验。",
        "intro_en": "Blackjack decisions only make sense after reading the table rules. Check dealer stands/hits soft 17, blackjack payout and split limits.",
        "rows": [
            ("要牌 Hit", "继续拿牌，目标接近 21 但不能爆牌。"),
            ("停牌 Stand", "保留当前点数等待庄家行动。"),
            ("加倍 / 分牌", "可能提高波动，必须先看桌面是否允许。"),
        ],
    },
    {
        "slug_base": "payout-rtp-notes",
        "topic": "Payout RTP",
        "title": "TL8899 LIVE：赔率、RTP 与规则面板怎么看",
        "en_title": "Payout and RTP Notes for Live Casino",
        "desc": "Bilingual TL8899 guide explaining payout tables, RTP notes, live provider rule panels, volatility and responsible-play limits.",
        "teaser": "赔率不是胜率，RTP 也不是短期保证；规则面板才是每桌的依据。",
        "intro_cn": "很多人把赔率、胜率和 RTP 混在一起。赔率只说明命中后如何赔付；RTP 是长期理论值，不保证任何单局结果。",
        "intro_en": "Payout, probability and RTP are related but not identical. Never treat an RTP number as a short-term promise.",
        "rows": [
            ("赔率 Payout", "命中某选项后的结算比例。"),
            ("RTP", "长期理论回报，不是个人短期结果保证。"),
            ("波动 Volatility", "结果上下起伏程度，高赔率通常伴随更高波动。"),
        ],
    },
    {
        "slug_base": "beginner-mistakes",
        "topic": "Beginner Mistakes",
        "title": "TL8899 LIVE：真人娱乐新手常见错误",
        "en_title": "Common Beginner Mistakes in Live Casino",
        "desc": "TL8899 responsible beginner guide covering chasing losses, ignoring table rules, misunderstanding bonuses and overvaluing high payouts.",
        "teaser": "新手最常见的问题不是不会点按钮，而是忽略预算、规则和波动。",
        "intro_cn": "真人娱乐新手常见错误包括追亏、临时加注、只看高赔率、没有阅读活动条款和把短期结果当成规律。",
        "intro_en": "Most beginner mistakes come from pressure, not from lacking a secret strategy. Slow down and make the rules boring before money is involved.",
        "rows": [
            ("追亏", "亏损后提高投注通常会放大压力。"),
            ("忽略规则", "每个供应商、每张桌、每个活动条款都可能不同。"),
            ("迷信系统", "任何下注系统都不能保证盈利。"),
        ],
    },
    {
        "slug_base": "responsible-play-budget-guide",
        "topic": "Responsible Play",
        "title": "TL8899 LIVE：预算、时间与负责任娱乐指南",
        "en_title": "Responsible Play Budget and Time Guide",
        "desc": "TL8899 Chinese and English responsible-play guide with adult-only reminders, budget limits, time limits and support-minded language.",
        "teaser": "负责任娱乐的核心是预算、时间、冷静和停止能力。",
        "intro_cn": "线上娱乐应只面向成年人，并且只应使用可承受的娱乐预算。先设定上限，比事后补救更重要。",
        "intro_en": "Responsible play means treating gambling content as adult entertainment, setting limits first, and stopping when control feels weaker.",
        "rows": [
            ("预算", "只使用可承受损失的娱乐预算。"),
            ("时间", "提前设定时长，避免疲劳后继续判断。"),
            ("停止", "如果影响睡眠、工作、健康或家庭，应立即停止并寻求帮助。"),
        ],
    },
]


def shanghai_today() -> date:
    if ZoneInfo:
        return datetime.now(ZoneInfo("Asia/Shanghai")).date()
    return datetime.now(timezone(timedelta(hours=8))).date()


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def ensure_dirs() -> None:
    for path in [
        ROOT,
        ROOT / "assets",
        ROOT / "blog",
        ROOT / "contact",
        ROOT / "admin",
        ROOT / "data",
        ROOT / "scripts",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def read_posts() -> list[dict]:
    path = ROOT / "data" / "posts.json"
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


def write_posts(posts: list[dict]) -> None:
    (ROOT / "data" / "posts.json").write_text(
        json.dumps(posts, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def topic_for_date(date_str: str) -> dict:
    start = date(2026, 6, 23)
    try:
        current = date.fromisoformat(date_str)
    except ValueError:
        current = shanghai_today()
    offset = (current - start).days
    return TOPICS[offset % len(TOPICS)]


def make_post(date_str: str, slug: str | None = None) -> dict:
    topic = topic_for_date(date_str)
    compact = date_str.replace("-", "")
    return {
        "date": date_str,
        "slug": slug or f"tl8899-{topic['slug_base']}-{compact}",
        "topic": topic["topic"],
        "title": topic["title"],
        "en_title": topic["en_title"],
        "desc": topic["desc"],
        "teaser": topic["teaser"],
        "intro_cn": topic["intro_cn"],
        "intro_en": topic["intro_en"],
        "rows": topic["rows"],
        "keywords": KEYWORDS + [topic["topic"], topic["title"]],
    }


def bad_text(value: object) -> bool:
    text = str(value)
    return "\ufffd" in text or "????" in text or "����" in text


def normalize_posts(posts: list[dict]) -> list[dict]:
    normalized: list[dict] = []
    seen: set[str] = set()
    for post in posts:
        date_str = post.get("date") or "2026-06-23"
        slug = post.get("slug")
        if bad_text(post.get("title", "")) or bad_text(post.get("teaser", "")) or not post.get("rows"):
            post = make_post(date_str, slug=slug)
        else:
            fixed = make_post(date_str, slug=slug)
            fixed.update(post)
            fixed["keywords"] = list(dict.fromkeys((post.get("keywords") or []) + KEYWORDS + [fixed["topic"]]))
            post = fixed
        if post["slug"] not in seen:
            normalized.append(post)
            seen.add(post["slug"])
    if not normalized:
        normalized.append(make_post("2026-06-23", slug="tl8899-live-casino-guide-20260623"))
    normalized.sort(key=lambda item: item["date"], reverse=True)
    return normalized


def keywords_meta(extra: list[str] | None = None) -> str:
    merged = list(dict.fromkeys(KEYWORDS + (extra or [])))
    return ", ".join(merged)


def json_ld(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def header_nav() -> str:
    return f"""
    <header class="top">
      <a class="brand" href="/" aria-label="TL8899 LIVE 首页">
        <span class="crest">TL</span>
        <span><strong>腾龙公司</strong><small>TL8899 LIVE</small></span>
      </a>
      <button class="menu-toggle" type="button" aria-label="打开导航" aria-expanded="false">菜单</button>
      <nav>
        <a href="/">首页</a>
        <a href="/#about">关于我们</a>
        <a href="/#services">业务项目</a>
        <a href="/#hall">现场大厅</a>
        <a href="/blog/">文章</a>
        <a href="/contact/">联系我们</a>
        <a class="admin-link" href="/admin/">Admin</a>
      </nav>
      <div class="quick">Telegram <a href="{TELEGRAM_URL}">{TELEGRAM}</a></div>
    </header>
    """


def footer() -> str:
    return f"""
    <footer>
      <div>
        <strong>TL8899 LIVE</strong>
        <p>腾龙公司 independent guide. Educational content only. No guaranteed winnings.</p>
      </div>
      <nav>
        <a href="/blog/">Blog</a>
        <a href="/contact/">Contact</a>
        <a href="/sitemap.xml">Sitemap</a>
        <a href="/admin/">Admin</a>
      </nav>
    </footer>
    <button id="top" aria-label="Back to top">↑</button>
    <script src="/assets/site.js?v={ASSET_VERSION}" defer></script>
    """


def layout(
    title: str,
    description: str,
    canonical_path: str,
    body: str,
    *,
    page_type: str = "website",
    robots: str = "index, follow, max-image-preview:large",
    extra_keywords: list[str] | None = None,
    structured: dict | list[dict] | None = None,
) -> str:
    canonical = f"{SITE}{canonical_path}"
    org = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "TL8899 LIVE",
        "alternateName": ["腾龙公司", "腾龙娱乐官网", "皇家在线公司", "tamron casino"],
        "url": SITE,
        "email": CONTACT_EMAIL,
        "sameAs": [TELEGRAM_URL],
        "contactPoint": {
            "@type": "ContactPoint",
            "contactType": "content and SEO contact",
            "email": CONTACT_EMAIL,
            "url": TELEGRAM_URL,
        },
    }
    scripts = [org]
    if structured:
        if isinstance(structured, list):
            scripts.extend(structured)
        else:
            scripts.append(structured)
    script_tags = "\n".join(
        f'<script type="application/ld+json">{json_ld(item)}</script>' for item in scripts
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="keywords" content="{esc(keywords_meta(extra_keywords))}">
  <meta name="robots" content="{esc(robots)}">
  <link rel="canonical" href="{esc(canonical)}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:type" content="{esc(page_type)}">
  <meta property="og:image" content="{SITE}/assets/tl8899-og.svg">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
  <link rel="preload" href="/assets/site.css?v={ASSET_VERSION}" as="style">
  <link rel="stylesheet" href="/assets/site.css?v={ASSET_VERSION}">
  {script_tags}
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  {header_nav()}
  <main id="main">
    {body}
  </main>
  {footer()}
</body>
</html>
"""


def article_cards(posts: list[dict], limit: int | None = None) -> str:
    visible = posts[:limit] if limit else posts
    return "\n".join(
        f"""<article class="article-card">
          <time datetime="{esc(post['date'])}">{esc(post['date'])}</time>
          <h3><a href="/blog/{esc(post['slug'])}/">{esc(post['title'])}</a></h3>
          <p>{esc(post['teaser'])}</p>
          <span class="read-more">Read guide →</span>
        </article>"""
        for post in visible
    )


def write_assets() -> None:
    css = f"""
:root {{
  --blue: #075db3;
  --blue-2: #0a76d1;
  --gold: #f3c351;
  --gold-2: #d98b13;
  --dark: #101621;
  --ink: #20242c;
  --muted: #687383;
  --line: #e6ebf2;
  --panel: #ffffff;
  --bg: #f6f8fb;
}}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
body {{
  margin: 0;
  font-family: Inter, "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
  color: var(--ink);
  background: var(--bg);
  line-height: 1.72;
}}
a {{ color: inherit; text-decoration: none; }}
.skip {{ position: absolute; left: -999px; top: 8px; z-index: 100; padding: 10px 14px; background: #fff; }}
.skip:focus {{ left: 8px; }}
.top {{
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 28px;
  padding: 16px clamp(22px, 5vw, 82px);
  background: rgba(255,255,255,.96);
  border-bottom: 1px solid var(--line);
  box-shadow: 0 10px 30px rgba(20, 30, 45, .07);
  backdrop-filter: blur(12px);
}}
.brand {{ display: flex; align-items: center; gap: 12px; min-width: 260px; }}
.crest {{
  display: grid;
  place-items: center;
  width: 58px;
  height: 58px;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 30%, #ffe58c, #b51512 48%, #201109 49%, #f6d675 56%, #bb7a14);
  color: #fff;
  font-weight: 950;
  letter-spacing: -.05em;
  box-shadow: 0 10px 24px rgba(138, 15, 8, .22);
}}
.brand strong {{ display: block; color: #c28a12; font-size: 26px; line-height: 1; }}
.brand small {{ display: block; color: #765612; font-weight: 800; text-transform: uppercase; letter-spacing: .08em; }}
.top nav {{ display: flex; align-items: center; gap: 24px; margin-left: auto; }}
.top nav a {{ font-weight: 850; }}
.top nav a:hover, .admin-link {{ color: var(--blue); }}
.quick {{ color: var(--blue); font-weight: 850; white-space: nowrap; }}
.menu-toggle {{ display: none; }}
.hero {{
  min-height: 650px;
  display: grid;
  align-items: center;
  padding: 72px clamp(22px, 6vw, 96px);
  position: relative;
  overflow: hidden;
  background:
    linear-gradient(90deg, rgba(0,0,0,.74), rgba(0,0,0,.34)),
    radial-gradient(circle at 78% 45%, rgba(243,195,81,.42), transparent 27rem),
    linear-gradient(135deg, #1b2738, #02060b 65%);
}}
.hero::before {{
  content: "";
  position: absolute;
  inset: 0;
  background:
    repeating-linear-gradient(90deg, rgba(255,255,255,.07) 0 2px, transparent 2px 82px),
    radial-gradient(circle at 75% 70%, rgba(11,111,171,.28), transparent 24rem);
  opacity: .78;
}}
.hero::after {{
  content: "♠ ♥ ♦ ♣";
  position: absolute;
  right: clamp(22px, 8vw, 130px);
  bottom: 54px;
  font-size: clamp(40px, 9vw, 132px);
  color: rgba(243, 195, 81, .2);
  letter-spacing: .18em;
}}
.hero-inner {{ position: relative; max-width: 890px; color: #fff; }}
.eyebrow {{ color: var(--gold); font-weight: 950; letter-spacing: .14em; text-transform: uppercase; }}
.hero h1 {{ font-size: clamp(42px, 7vw, 88px); line-height: 1.02; margin: 12px 0; }}
.hero p {{ font-size: 20px; max-width: 740px; color: #e8edf4; }}
.actions {{ display: flex; flex-wrap: wrap; gap: 14px; margin-top: 28px; }}
.btn {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  padding: 12px 22px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,.35);
  font-weight: 950;
}}
.btn.primary {{ background: linear-gradient(135deg, var(--gold), var(--gold-2)); border: 0; color: #1b1203; }}
.btn.dark {{ border-color: var(--line); color: var(--ink); }}
.contact-strip {{
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 24px;
  padding: 16px;
  border: 1px solid rgba(243,195,81,.45);
  border-radius: 18px;
  background: rgba(0,0,0,.28);
  font-weight: 900;
}}
.contact-strip a {{ color: var(--gold); }}
.section {{ padding: 76px clamp(22px, 6vw, 96px); }}
.section.white {{ background: #fff; }}
.head {{ max-width: 900px; margin-bottom: 32px; }}
.head h1, .head h2 {{ font-size: clamp(32px, 4vw, 54px); line-height: 1.1; margin: 0; }}
.head p {{ color: var(--muted); font-size: 18px; }}
.grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 22px; }}
.card {{
  padding: 28px;
  border-radius: 24px;
  background: #fff;
  border: 1px solid var(--line);
  box-shadow: 0 18px 50px rgba(20,30,45,.08);
}}
.card.dark {{ background: linear-gradient(160deg, #111b28, #0b1018); color: #fff; border: 0; }}
.card .icon {{ font-size: 42px; color: var(--gold); font-weight: 950; }}
.card h3 {{ font-size: 24px; margin: 14px 0 8px; }}
.card p {{ color: var(--muted); margin: 0; }}
.card.dark p {{ color: #c7d1df; }}
.hall {{ display: grid; grid-template-columns: 1.05fr .95fr; gap: 28px; align-items: center; }}
.hall-art {{
  min-height: 370px;
  border-radius: 30px;
  background:
    linear-gradient(180deg, rgba(0,0,0,.10), rgba(0,0,0,.62)),
    repeating-conic-gradient(from 18deg, #123f31 0 12deg, #7e1111 12deg 24deg, #111827 24deg 36deg);
  box-shadow: inset 0 0 0 18px rgba(243,195,81,.18), 0 24px 70px rgba(0,0,0,.18);
}}
.articles {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }}
.article-card {{
  display: flex;
  flex-direction: column;
  min-height: 235px;
  padding: 22px;
  border: 1px solid var(--line);
  border-radius: 22px;
  background: #fff;
  transition: transform .2s ease, box-shadow .2s ease;
}}
.article-card:hover {{ transform: translateY(-3px); box-shadow: 0 18px 50px rgba(20,30,45,.1); }}
.article-card time {{ font-weight: 900; color: var(--blue); }}
.article-card h3 {{ margin: 8px 0; font-size: 21px; }}
.article-card p {{ color: var(--muted); }}
.read-more {{ margin-top: auto; color: var(--blue); font-weight: 900; }}
.contact-box {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
.contact-pill {{
  display: block;
  padding: 18px 20px;
  border-radius: 18px;
  background: #10233b;
  color: #fff;
  font-size: 22px;
  font-weight: 950;
}}
.contact-pill.gold {{ background: #2b2514; color: var(--gold); }}
.article {{ max-width: 980px; margin: 0 auto; padding: 70px 22px; }}
.article h1 {{ font-size: clamp(34px, 5vw, 58px); line-height: 1.1; }}
.article h2 {{ font-size: 30px; margin-top: 38px; }}
.article p, .article li {{ color: #4d5562; }}
.meta-line {{ color: var(--blue); font-weight: 900; }}
.table {{ overflow: auto; border: 1px solid var(--line); border-radius: 18px; margin: 22px 0; }}
.table table {{ width: 100%; border-collapse: collapse; min-width: 680px; background: #fff; }}
.table th, .table td {{ padding: 14px; border-bottom: 1px solid var(--line); text-align: left; }}
.table th {{ background: #f1f5fb; color: var(--blue); }}
.note {{ padding: 16px; border-radius: 18px; background: #fff8df; border: 1px solid #f1cf67; color: #4e3905; }}
footer {{ display: flex; justify-content: space-between; gap: 20px; padding: 34px clamp(22px,6vw,96px); background: #101621; color: #cfd7e3; }}
footer strong {{ color: #fff; }}
footer nav {{ display: flex; gap: 18px; flex-wrap: wrap; }}
#top {{ position: fixed; right: 18px; bottom: 18px; width: 46px; height: 46px; border: 0; border-radius: 50%; background: var(--gold); font-weight: 950; opacity: 0; pointer-events: none; transition: opacity .2s ease; }}
#top.show {{ opacity: 1; pointer-events: auto; }}
.admin-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; }}
.stat {{ padding: 22px; border-radius: 22px; background: #fff; border: 1px solid var(--line); }}
.stat strong {{ display: block; font-size: 28px; color: var(--blue); }}
@media (max-width: 980px) {{
  .top {{ align-items: flex-start; flex-direction: column; }}
  .top nav {{ margin-left: 0; flex-wrap: wrap; display: none; }}
  .top.open nav {{ display: flex; }}
  .menu-toggle {{ display: inline-flex; border: 1px solid var(--line); border-radius: 999px; background: #fff; padding: 9px 14px; font-weight: 900; }}
  .quick {{ white-space: normal; }}
  .grid, .articles, .hall, .contact-box, .admin-grid {{ grid-template-columns: 1fr; }}
  .hero {{ min-height: auto; }}
  .brand {{ min-width: 0; }}
}}
"""
    js = """
const topButton = document.getElementById('top');
const header = document.querySelector('.top');
const menu = document.querySelector('.menu-toggle');
window.addEventListener('scroll', () => {
  if (!topButton) return;
  topButton.classList.toggle('show', window.scrollY > 500);
});
topButton?.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
menu?.addEventListener('click', () => {
  const open = header.classList.toggle('open');
  menu.setAttribute('aria-expanded', String(open));
});
"""
    favicon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96"><rect width="96" height="96" rx="22" fill="#101621"/><circle cx="48" cy="48" r="33" fill="#d98b13"/><circle cx="48" cy="48" r="25" fill="#111827"/><text x="48" y="59" text-anchor="middle" font-family="Arial" font-size="30" font-weight="900" fill="#f3c351">TL</text></svg>"""
    og = """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630"><defs><linearGradient id="g" x1="0" x2="1"><stop stop-color="#07111f"/><stop offset="1" stop-color="#075db3"/></linearGradient></defs><rect width="1200" height="630" fill="url(#g)"/><circle cx="865" cy="315" r="180" fill="#f3c351" opacity=".18"/><text x="86" y="220" font-family="Microsoft YaHei, Arial" font-size="74" font-weight="900" fill="#f3c351">腾龙公司</text><text x="86" y="305" font-family="Arial" font-size="58" font-weight="900" fill="#fff">TL8899 LIVE</text><text x="86" y="388" font-family="Microsoft YaHei, Arial" font-size="34" fill="#dfe8f4">真人娱乐指南 · 每日文章 · 联系方式</text><text x="86" y="455" font-family="Arial" font-size="30" fill="#f3c351">Telegram @jhondoe112233</text></svg>"""
    (ROOT / "assets" / "site.css").write_text(css.strip() + "\n", encoding="utf-8")
    (ROOT / "assets" / "site.js").write_text(js.strip() + "\n", encoding="utf-8")
    (ROOT / "assets" / "favicon.svg").write_text(favicon, encoding="utf-8")
    (ROOT / "assets" / "tl8899-og.svg").write_text(og, encoding="utf-8")


def write_home(posts: list[dict]) -> None:
    body = f"""
    <section class="hero">
      <div class="hero-inner">
        <p class="eyebrow">TL8899 LIVE / 腾龙公司</p>
        <h1>腾龙公司<br>真人娱乐资讯指南</h1>
        <p>参考中文企业官网的清晰结构：品牌介绍、业务项目、现场大厅、新闻文章、联系信息和后台状态。本站展示 Telegram 与邮箱联系，并每天自动更新 SEO 文章。</p>
        <div class="actions">
          <a class="btn primary" href="/contact/">立即联系</a>
          <a class="btn" href="/blog/">阅读文章</a>
        </div>
        <div class="contact-strip">
          <strong>Contact:</strong>
          <a href="{TELEGRAM_URL}">Telegram {TELEGRAM}</a>
          <span>|</span>
          <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>
        </div>
      </div>
    </section>
    <section id="about" class="section white">
      <div class="head">
        <p class="eyebrow">About</p>
        <h2>关于 TL8899 LIVE</h2>
        <p>面向中文和英文用户的真人娱乐资讯站，覆盖百家乐、龙虎、牛牛、骰宝、轮盘、21点、规则说明、联系方式和负责任娱乐提示。</p>
      </div>
      <div class="hall">
        <div class="hall-art" aria-label="casino hall style artwork"></div>
        <div class="grid">
          <div class="card"><div class="icon">龙</div><h3>龙虎</h3><p>快速牌面大小比较，重点理解和局风险。</p></div>
          <div class="card"><div class="icon">B</div><h3>百家乐</h3><p>庄、闲、和、佣金与免佣变体的基础说明。</p></div>
          <div class="card"><div class="icon">牛</div><h3>牛牛</h3><p>五张牌组合、牛数与倍率表的规则提醒。</p></div>
        </div>
      </div>
    </section>
    <section id="services" class="section">
      <div class="head">
        <p class="eyebrow">Business</p>
        <h2>业务项目</h2>
      </div>
      <div class="grid">
        <div class="card dark"><div class="icon">01</div><h3>每日 SEO 文章</h3><p>自动生成并发布 live casino 双语文章，更新 sitemap 和 RSS。</p></div>
        <div class="card dark"><div class="icon">02</div><h3>联系方式展示</h3><p>Telegram、邮箱和结构化资料帮助搜索引擎识别联系渠道。</p></div>
        <div class="card dark"><div class="icon">03</div><h3>后台 Dashboard</h3><p>受密码保护的状态页，查看文章数量、最新日期和自动化信息。</p></div>
      </div>
    </section>
    <section class="section white" id="hall">
      <div class="head">
        <p class="eyebrow">News</p>
        <h2>新闻资讯</h2>
        <p>Latest bilingual guides. Keywords such as tamron casino、腾龙娱乐官网、皇家在线公司 are used as discovery tags only and do not claim official affiliation with another brand.</p>
      </div>
      <div class="articles">{article_cards(posts, 6)}</div>
    </section>
    """
    structured = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "TL8899 LIVE",
        "url": SITE,
        "potentialAction": {
            "@type": "SearchAction",
            "target": f"{SITE}/blog/?q={{search_term_string}}",
            "query-input": "required name=search_term_string",
        },
    }
    (ROOT / "index.html").write_text(
        layout(
            "TL8899 LIVE | 腾龙公司 Contact & Casino Guide",
            f"TL8899 LIVE 腾龙公司 guide with Telegram {TELEGRAM}, email {CONTACT_EMAIL}, daily casino blog, live hall information and responsible-play notes.",
            "/",
            body,
            structured=structured,
        ),
        encoding="utf-8",
    )


def write_blog_index(posts: list[dict]) -> None:
    body = f"""
    <section class="section white">
      <div class="head">
        <p class="eyebrow">Blog</p>
        <h1>TL8899 真人娱乐文章</h1>
        <p>每日更新百家乐、龙虎、牛牛、轮盘、骰宝、21点、RTP、常见错误和负责任娱乐内容。No article promises guaranteed winnings.</p>
      </div>
      <div class="articles">{article_cards(posts)}</div>
    </section>
    """
    path = ROOT / "blog"
    path.mkdir(exist_ok=True)
    (path / "index.html").write_text(
        layout(
            "TL8899 Blog | 真人娱乐规则与 SEO 文章",
            "Daily Chinese and English TL8899 blog posts about baccarat, Dragon Tiger, Niu Niu, live dealer rules and responsible play.",
            "/blog/",
            body,
        ),
        encoding="utf-8",
    )


def write_contact() -> None:
    body = f"""
    <section class="section white">
      <div class="head">
        <p class="eyebrow">Contact</p>
        <h1>联系我们</h1>
        <p>For content updates, SEO corrections, or business contact, use Telegram or email. Do not send passwords, payment details or identity documents.</p>
      </div>
      <div class="contact-box">
        <a class="contact-pill" href="{TELEGRAM_URL}">Telegram {TELEGRAM}</a>
        <a class="contact-pill gold" href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>
      </div>
      <div class="note" style="margin-top:24px">Adult informational content only. Set a budget and stop if play affects sleep, work, health or family.</div>
    </section>
    """
    path = ROOT / "contact"
    path.mkdir(exist_ok=True)
    (path / "index.html").write_text(
        layout(
            "Contact TL8899 | Telegram and Email",
            f"Contact TL8899 LIVE by Telegram {TELEGRAM} or email {CONTACT_EMAIL}.",
            "/contact/",
            body,
            extra_keywords=["contact", CONTACT_EMAIL, TELEGRAM],
        ),
        encoding="utf-8",
    )


def write_admin(posts: list[dict]) -> None:
    latest = posts[0] if posts else make_post(shanghai_today().isoformat())
    body = f"""
    <section class="section white">
      <div class="head">
        <p class="eyebrow">Admin</p>
        <h1>TL8899 Admin Dashboard</h1>
        <p>Protected status page for the static site and daily blog automation.</p>
      </div>
      <div class="admin-grid">
        <div class="stat"><strong>{len(posts)}</strong><span>Total posts</span></div>
        <div class="stat"><strong>{esc(latest['date'])}</strong><span>Latest post</span></div>
        <div class="stat"><strong>09:25</strong><span>Asia/Shanghai cron</span></div>
        <div class="stat"><strong>DNS</strong><span>A record must point to {SERVER_IP}</span></div>
      </div>
      <div class="actions">
        <a class="btn primary dark" href="/blog/">View Blog</a>
        <a class="btn dark" href="/admin/status.json">Status JSON</a>
        <a class="btn dark" href="/sitemap.xml">Sitemap</a>
      </div>
      <p class="note">Cron: /etc/cron.d/tl8899-daily-blog · Log: /var/log/tl8899-daily-blog.log · Script: /var/www/tl8899/scripts/daily_tl8899_blog.py</p>
    </section>
    """
    status = {
        "site": SITE,
        "domain": DOMAIN,
        "server_ip": SERVER_IP,
        "post_count": len(posts),
        "latest_post": latest,
        "cron": "25 1 * * * UTC / 09:25 Asia/Shanghai",
        "contact": {"telegram": TELEGRAM, "telegram_url": TELEGRAM_URL, "email": CONTACT_EMAIL},
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    path = ROOT / "admin"
    path.mkdir(exist_ok=True)
    (path / "index.html").write_text(
        layout(
            "TL8899 Admin Dashboard",
            "Protected TL8899 LIVE admin dashboard for status and automation checks.",
            "/admin/",
            body,
            robots="noindex, nofollow",
        ),
        encoding="utf-8",
    )
    (path / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_article(post: dict) -> None:
    rows = "\n".join(
        f"<tr><td>{esc(name)}</td><td>{esc(note)}</td></tr>" for name, note in post["rows"]
    )
    body = f"""
    <article class="article">
      <p class="meta-line">{esc(post['date'])} · {esc(post['topic'])} · TL8899 LIVE</p>
      <h1>{esc(post['title'])}</h1>
      <p>{esc(post['desc'])}</p>
      <div class="note">Responsible play: this article is for adult informational use only. It does not promise winnings, betting systems, or guaranteed results.</div>
      <h2>中文指南</h2>
      <p>{esc(post['intro_cn'])}</p>
      <div class="table">
        <table>
          <thead><tr><th>项目</th><th>说明</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
      <p>阅读 TL8899 LIVE 内容时，请把 tamron casino、腾龙娱乐官网、皇家在线公司 等词理解为 SEO 检索标签；本站不声明与其他品牌存在官方关系。</p>
      <h2>English Guide</h2>
      <p><strong>{esc(post['en_title'])}</strong></p>
      <p>{esc(post['intro_en'])}</p>
      <ul>
        <li>Check the provider rule panel before every table session.</li>
        <li>High payout does not mean high probability.</li>
        <li>Set a budget and time limit before play starts.</li>
        <li>Stop immediately if entertainment starts to feel like pressure.</li>
      </ul>
      <h2>Related TL8899 Guides</h2>
      <p><a href="/blog/">Blog index</a> · <a href="/contact/">Contact Telegram and Email</a> · <a href="/">TL8899 home</a></p>
    </article>
    """
    article_schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": post["title"],
        "description": post["desc"],
        "datePublished": post["date"],
        "dateModified": post["date"],
        "author": {"@type": "Organization", "name": "TL8899 LIVE"},
        "publisher": {"@type": "Organization", "name": "TL8899 LIVE"},
        "mainEntityOfPage": f"{SITE}/blog/{post['slug']}/",
        "keywords": post["keywords"],
    }
    path = ROOT / "blog" / post["slug"]
    path.mkdir(parents=True, exist_ok=True)
    (path / "index.html").write_text(
        layout(
            f"{post['title']} | {post['en_title']}",
            post["desc"],
            f"/blog/{post['slug']}/",
            body,
            page_type="article",
            extra_keywords=post["keywords"],
            structured=article_schema,
        ),
        encoding="utf-8",
    )


def write_discovery(posts: list[dict]) -> None:
    today = shanghai_today().isoformat()
    urls = [
        ("/", "daily", "1.0"),
        ("/blog/", "daily", "0.9"),
        ("/contact/", "monthly", "0.7"),
    ] + [(f"/blog/{post['slug']}/", "weekly", "0.8") for post in posts]
    sitemap_items = "\n".join(
        f"""  <url>
    <loc>{SITE}{path}</loc>
    <lastmod>{today if path in ['/', '/blog/'] else (posts[0]['date'] if path == '/contact/' and posts else today)}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>"""
        for path, freq, priority in urls
    )
    (ROOT / "sitemap.xml").write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{sitemap_items}
</urlset>
""",
        encoding="utf-8",
    )
    rss_items = "\n".join(
        f"""    <item>
      <title>{esc(post['title'])}</title>
      <link>{SITE}/blog/{esc(post['slug'])}/</link>
      <guid>{SITE}/blog/{esc(post['slug'])}/</guid>
      <pubDate>{email.utils.format_datetime(datetime.fromisoformat(post['date']).replace(tzinfo=timezone.utc))}</pubDate>
      <description>{esc(post['desc'])}</description>
    </item>"""
        for post in posts[:20]
    )
    (ROOT / "rss.xml").write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>TL8899 LIVE Blog</title>
    <link>{SITE}/blog/</link>
    <description>Daily TL8899 live casino guides in Chinese and English.</description>
{rss_items}
  </channel>
</rss>
""",
        encoding="utf-8",
    )
    (ROOT / "robots.txt").write_text(
        f"""User-agent: *
Allow: /
Disallow: /admin/
Sitemap: {SITE}/sitemap.xml
""",
        encoding="utf-8",
    )
    (ROOT / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY + "\n", encoding="utf-8")


def rebuild(posts: list[dict]) -> None:
    ensure_dirs()
    write_assets()
    write_posts(posts)
    write_home(posts)
    write_blog_index(posts)
    write_contact()
    write_admin(posts)
    for post in posts:
        write_article(post)
    write_discovery(posts)


def verify_local(slug: str | None = None) -> None:
    paths = ["/", "/blog/", "/sitemap.xml", "/rss.xml"]
    if slug:
        paths.insert(1, f"/blog/{slug}/")
    for path in paths:
        request = urllib.request.Request(
            f"http://127.0.0.1{path}",
            headers={"Host": DOMAIN, "User-Agent": "tl8899-local-verifier/1.0"},
        )
        with urllib.request.urlopen(request, timeout=15) as response:
            if response.status != 200:
                raise RuntimeError(f"Local verify failed for {path}: {response.status}")


def dns_points_here() -> bool:
    try:
        return socket.gethostbyname(DOMAIN) == SERVER_IP
    except OSError:
        return False


def submit_indexnow(urls: list[str]) -> int | None:
    if not dns_points_here():
        print(f"DNS for {DOMAIN} does not point to {SERVER_IP}; skipping IndexNow.")
        return None
    payload = json.dumps(
        {"host": DOMAIN, "key": INDEXNOW_KEY, "keyLocation": INDEXNOW_KEY_LOCATION, "urlList": urls},
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": "tl8899-indexnow/1.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            print(f"IndexNow response: {response.status}")
            return response.status
    except urllib.error.HTTPError as error:
        print(f"IndexNow response: {error.code}")
        return error.code


def git_commit(message: str) -> None:
    subprocess.run(["git", "-C", str(ROOT), "config", "user.name", "TL8899 Automation"], check=False)
    subprocess.run(["git", "-C", str(ROOT), "config", "user.email", "automation@tl8899.live"], check=False)
    status = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"], capture_output=True, text=True, check=False)
    if not status.stdout.strip():
        print("Git: no changes.")
        return
    subprocess.run(["git", "-C", str(ROOT), "add", "."], check=False)
    result = subprocess.run(["git", "-C", str(ROOT), "commit", "-m", message], capture_output=True, text=True, check=False)
    print(result.stdout.strip())
    if result.returncode != 0:
        print(result.stderr.strip())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=shanghai_today().isoformat())
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()

    posts = normalize_posts(read_posts())
    if args.rebuild:
        rebuild(posts)
        verify_local(posts[0]["slug"] if posts else None)
        print(f"Rebuilt TL8899 site with {len(posts)} posts.")
        return 0

    existing = next((post for post in posts if post.get("date") == args.date), None)
    if existing and not args.force:
        rebuild(posts)
        verify_local(existing["slug"])
        print(f"Skip: post already exists for {args.date}: {existing['slug']}")
        return 0

    new_post = make_post(args.date)
    if args.dry_run:
        print(f"Dry run: would publish {new_post['slug']} - {new_post['title']}")
        return 0

    posts = [post for post in posts if post.get("date") != args.date]
    posts.insert(0, new_post)
    posts.sort(key=lambda item: item["date"], reverse=True)
    rebuild(posts)
    verify_local(new_post["slug"])
    print(f"Published: {SITE}/blog/{new_post['slug']}/")
    git_commit(f"Publish TL8899 daily blog {args.date}")
    submit_indexnow([
        f"{SITE}/blog/{new_post['slug']}/",
        f"{SITE}/",
        f"{SITE}/blog/",
        f"{SITE}/sitemap.xml",
        f"{SITE}/rss.xml",
    ])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
