#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import email.utils
import html
import json
import os
import re
import shutil
import socket
import subprocess
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None


ROOT = Path(os.environ.get("TL8899_ROOT", "/var/www/tl8899"))
SITE = "https://tl8899.live"
DOMAIN = "tl8899.live"
GAME_PLAY_URL = "https://tl616.cc/"
SERVER_IP = "76.13.216.172"
INDEXNOW_KEY = "f64254d0a708461e8b1f2fce8eee9c30"
INDEXNOW_KEY_LOCATION = f"{SITE}/{INDEXNOW_KEY}.txt"
ASSET_VERSION = "2026071702"
BLOG_PAGE_SIZE = 12
DEALER_IMAGE_WEBP = f"/assets/casino-dealer-live.webp?v={ASSET_VERSION}"
DEALER_IMAGE_JPG = f"/assets/casino-dealer-live.jpg?v={ASSET_VERSION}"
HERO_IMAGE_WEBP = f"/assets/tl8899-hero-v2.webp?v={ASSET_VERSION}"
HERO_IMAGE_PNG = f"/assets/tl8899-hero-v2.png?v={ASSET_VERSION}"

DEFAULT_SETTINGS = {
    "brand_name": "腾龙公司",
    "brand_subtitle": "TL8899 LIVE",
    "site_title": "TL8899 LIVE | 腾龙公司真人娱乐资讯",
    "site_description": "TL8899 LIVE 腾龙公司中文资讯站，展示百家乐、龙虎、牛牛、轮盘、骰宝、21点、联系方式、搜索文章和负责任娱乐提示。",
    "hero_title": "腾龙公司\n真人娱乐资讯指南",
    "hero_description": "参考中文企业官网的清晰结构：品牌介绍、业务项目、现场大厅、新闻文章、联系信息和后台管理。所有公开内容以中文为主，并每天自动更新搜索文章。",
    "telegram": "@jhondoe112233",
    "telegram_url": "https://t.me/jhondoe112233",
    "phone": "15393938358",
    "email": "andrewjack0007@gmail.com",
    "footer_note": "本站为独立中文资讯站，仅提供成年人信息参考，不承诺盈利，不提供保证结果的下注方法。",
    "seo_keywords": "TL8899, tl8899.live, 腾龙公司, 腾龙娱乐官网, 皇家在线公司, tamron casino, 真人娱乐, 真人娱乐场, 百家乐, 龙虎, 牛牛, 轮盘, 骰宝, 21点",
}

BASE_KEYWORDS = [
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
    "轮盘",
    "骰宝",
    "21点",
]

TOPICS = [
    {
        "slug_base": "baccarat-banker-player-flow",
        "topic": "百家乐",
        "title": "TL8899 LIVE：百家乐庄闲流程与风险说明",
        "desc": "中文说明百家乐庄、闲、和、佣金、免佣变体、桌台规则与负责任娱乐提醒。",
        "teaser": "百家乐庄、闲、和的基础流程，适合新手先理解桌面规则与风险。",
        "intro": "百家乐在亚洲真人娱乐内容里很常见，节奏快、规则短，但每一桌仍要先看清佣金、限红、和局赔付与补牌规则。不要把短期结果当成规律，也不要相信任何保证盈利的方法。",
        "rows": [
            ("庄", "常见为较低优势选项，但可能有佣金或免佣变体。"),
            ("闲", "流程直观，赔付通常为 1:1。"),
            ("和", "赔率高但波动大，新手不应把高赔率理解为更容易出现。"),
        ],
    },
    {
        "slug_base": "dragon-tiger-card-ranking",
        "topic": "龙虎",
        "title": "TL8899 LIVE：龙虎牌面大小与和局风险",
        "desc": "中文说明龙虎的龙、虎、和、牌面大小、桌台限制与新手风险控制。",
        "teaser": "龙虎只有两张主牌，重点是理解大小比较、和局风险和桌面限额。",
        "intro": "龙虎玩法来自简单的高牌比较：龙位与虎位各发一张牌，点数高的一方胜。规则短，但和局赔率与扣半规则要特别注意，不能因为开牌快就忽略预算。",
        "rows": [
            ("龙", "押龙位牌面较高，通常按 1:1 结算。"),
            ("虎", "押虎位牌面较高，规则与龙位相同。"),
            ("和", "赔率看起来吸引人，但命中率低且部分规则会影响主注结算。"),
        ],
    },
    {
        "slug_base": "niu-niu-bull-bull-hand-values",
        "topic": "牛牛",
        "title": "TL8899 LIVE：牛牛牌型、倍数与新手规则",
        "desc": "中文说明牛牛五张牌组合、牛数、倍数表、开牌节奏和负责任娱乐。",
        "teaser": "牛牛要先找三张成十的组合，再判断剩余两张的牛数与倍数。",
        "intro": "牛牛的乐趣在于五张牌的组合判断：先找三张合计为十的倍数，再用剩下两张计算牛几。不同场馆倍数表可能不同，进入桌台前必须先读规则。",
        "rows": [
            ("无牛", "找不到三张成十组合时通常为较低牌型。"),
            ("牛一至牛九", "剩余两张点数决定牛数，倍数按桌面表执行。"),
            ("牛牛", "较高牌型，但具体倍率以供应商规则为准。"),
        ],
    },
    {
        "slug_base": "live-hall-table-etiquette",
        "topic": "现场大厅",
        "title": "TL8899 LIVE：真人大厅流程、礼仪与联系指南",
        "desc": "中文说明真人大厅选桌、倒计时、桌台礼仪、联系信息和安全提醒。",
        "teaser": "进入真人大厅前，先看桌台限额、开牌节奏、规则面板和客服联系方式。",
        "intro": "真人大厅的体验不只是画面漂亮，还包括网络稳定、下注倒计时、桌台限额、规则面板和客服联系是否清楚。新手应先观察几局，再决定是否参与。",
        "rows": [
            ("桌台限额", "确认最低、最高投注与单局限制。"),
            ("倒计时", "真人桌有固定下注窗口，延迟时不要强行追单。"),
            ("联系渠道", "Telegram、电话与邮箱应清楚展示，方便内容和业务联系。"),
        ],
    },
    {
        "slug_base": "roulette-inside-outside-bets",
        "topic": "轮盘",
        "title": "TL8899 LIVE：轮盘内围外围投注与波动",
        "desc": "中文说明轮盘内围、外围、欧式、美式、赔率差异和风险控制。",
        "teaser": "轮盘要区分内围、外围、欧式、美式和赔率差异，不能只看数字漂亮。",
        "intro": "轮盘的视觉效果强，但规则核心是赔率与概率的交换。外围投注命中率较高、赔率较低；内围投注赔率高、波动也更大。",
        "rows": [
            ("外围", "红黑、单双、大小等，赔率较低但结果范围更宽。"),
            ("内围", "直选、分注、街注等，赔率高但波动大。"),
            ("轮盘变体", "欧式单零通常与美式双零有不同理论回报。"),
        ],
    },
    {
        "slug_base": "sic-bo-dice-bets",
        "topic": "骰宝",
        "title": "TL8899 LIVE：骰宝大小、围骰与赔率说明",
        "desc": "中文说明骰宝大小、点数、围骰、赔率表、波动与新手常见误区。",
        "teaser": "骰宝看起来热闹，实际要重点看大小、点数、围骰与赔率表。",
        "intro": "骰宝使用三颗骰子，常见选项包括大小、总点数、对子、围骰。新手容易被高赔率吸引，却忽略出现概率。",
        "rows": [
            ("大 / 小", "常见基础选项，但遇到围骰时规则可能排除。"),
            ("总点数", "赔率随点数出现概率变化。"),
            ("围骰", "赔率高、波动大，不适合作为追回亏损的方法。"),
        ],
    },
    {
        "slug_base": "blackjack-basic-rules",
        "topic": "21点",
        "title": "TL8899 LIVE：21点基础规则与常见决定",
        "desc": "中文说明21点要牌、停牌、加倍、分牌、庄家规则和预算控制。",
        "teaser": "21点要先看庄家规则、Blackjack 赔率、分牌和加倍限制。",
        "intro": "21点比百家乐更依赖规则细节。庄家软 17、Blackjack 赔付、可否投降、分牌限制都会影响桌面体验。",
        "rows": [
            ("要牌", "继续拿牌，目标接近 21 但不能爆牌。"),
            ("停牌", "保留当前点数等待庄家行动。"),
            ("加倍 / 分牌", "可能提高波动，必须先看桌面是否允许。"),
        ],
    },
    {
        "slug_base": "payout-rtp-notes",
        "topic": "赔率与RTP",
        "title": "TL8899 LIVE：赔率、RTP 与规则面板怎么看",
        "desc": "中文说明赔率、概率、RTP、波动、规则面板和负责任娱乐边界。",
        "teaser": "赔率不是胜率，RTP 也不是短期保证；规则面板才是每桌的依据。",
        "intro": "很多人把赔率、胜率和 RTP 混在一起。赔率只说明命中后如何赔付；RTP 是长期理论值，不保证任何单局结果。",
        "rows": [
            ("赔率", "命中某选项后的结算比例。"),
            ("RTP", "长期理论回报，不是个人短期结果保证。"),
            ("波动", "结果上下起伏程度，高赔率通常伴随更高波动。"),
        ],
    },
    {
        "slug_base": "beginner-mistakes",
        "topic": "新手误区",
        "title": "TL8899 LIVE：真人娱乐新手常见错误",
        "desc": "中文说明追亏、忽略规则、误解优惠、迷信高赔率等新手常见问题。",
        "teaser": "新手最常见的问题不是不会点按钮，而是忽略预算、规则和波动。",
        "intro": "真人娱乐新手常见错误包括追亏、临时加注、只看高赔率、没有阅读活动条款和把短期结果当成规律。",
        "rows": [
            ("追亏", "亏损后提高投注通常会放大压力。"),
            ("忽略规则", "每个供应商、每张桌、每个活动条款都可能不同。"),
            ("迷信系统", "任何下注系统都不能保证盈利。"),
        ],
    },
    {
        "slug_base": "responsible-play-budget-guide",
        "topic": "负责任娱乐",
        "title": "TL8899 LIVE：预算、时间与负责任娱乐指南",
        "desc": "中文说明成年人信息、预算上限、时间管理、停止条件和健康提醒。",
        "teaser": "负责任娱乐的核心是预算、时间、冷静和停止能力。",
        "intro": "线上娱乐应只面向成年人，并且只应使用可承受的娱乐预算。先设定上限，比事后补救更重要。",
        "rows": [
            ("预算", "只使用可承受损失的娱乐预算。"),
            ("时间", "提前设定时长，避免疲劳后继续判断。"),
            ("停止", "如果影响睡眠、工作、健康或家庭，应立即停止并寻求帮助。"),
        ],
    },
]


def shanghai_today() -> date:
    if ZoneInfo:
        try:
            return datetime.now(ZoneInfo("Asia/Shanghai")).date()
        except Exception:
            pass
    return datetime.now(timezone(timedelta(hours=8))).date()


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def slugify(value: str, fallback: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or fallback


def ensure_dirs() -> None:
    for path in [
        ROOT,
        ROOT / "assets",
        ROOT / "blog",
        ROOT / "contact",
        ROOT / "privacy-policy",
        ROOT / "terms-of-service",
        ROOT / "data",
        ROOT / "scripts",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def load_settings() -> dict:
    path = ROOT / "data" / "settings.json"
    settings = DEFAULT_SETTINGS.copy()
    if path.exists():
        try:
            settings.update(json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            pass
    save_settings(settings)
    return settings


def save_settings(settings: dict) -> None:
    path = ROOT / "data" / "settings.json"
    data = DEFAULT_SETTINGS.copy()
    data.update({k: v for k, v in settings.items() if k in DEFAULT_SETTINGS})
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def settings_keywords(settings: dict) -> list[str]:
    raw = settings.get("seo_keywords", "")
    values = [item.strip() for item in raw.replace("\n", ",").split(",") if item.strip()]
    return list(dict.fromkeys(BASE_KEYWORDS + values))


def public_title(value: object) -> str:
    return str(value).replace("TL8899 LIVE：", "腾龙公司：").replace("TL8899 LIVE:", "腾龙公司：")


def normalize_keywords(values: list[object], topic: object = "") -> list[str]:
    cleaned = [public_title(item).strip() for item in values if str(item).strip()]
    cleaned += BASE_KEYWORDS + [str(topic).strip(), "https://myanmarcasino.cloud/"]
    return list(dict.fromkeys(item for item in cleaned if item))


def visible_article_keywords(post: dict) -> list[str]:
    visible: list[str] = []
    for tag in post.get("keywords") or []:
        text = public_title(tag).strip()
        if not text or re.search(r"[A-Za-z]", text):
            continue
        if text.startswith("http") or len(text) > 18:
            continue
        visible.append(text)
    visible += ["腾龙公司", "腾龙娱乐官网", "皇家在线公司", "百家乐", "龙虎", "牛牛", "轮盘", "骰宝", "二十一点"]
    return list(dict.fromkeys(visible))[:18]


def topic_for_date(date_str: str, shift: int = 0) -> dict:
    start = date(2026, 6, 23)
    try:
        current = date.fromisoformat(date_str)
    except ValueError:
        current = shanghai_today()
    return TOPICS[((current - start).days + shift) % len(TOPICS)]


def make_auto_post(date_str: str, slug: str | None = None, slot: int = 1) -> dict:
    topic = topic_for_date(date_str, max(slot - 1, 0))
    compact = date_str.replace("-", "")
    slug_suffix = "" if slot == 1 else f"-{slot}"
    topic_title = public_title(topic["title"])
    return {
        "date": date_str,
        "slot": slot,
        "slug": slug or f"tl8899-{topic['slug_base']}-{compact}{slug_suffix}",
        "topic": topic["topic"],
        "title": topic_title if slot == 1 else f"{topic_title}（第{slot}篇）",
        "desc": topic["desc"],
        "teaser": topic["teaser"],
        "intro": topic["intro"],
        "rows": topic["rows"],
        "keywords": normalize_keywords([topic["topic"], topic_title], topic["topic"]),
        "status": "published",
        "source": "auto",
    }


def bad_text(value: object) -> bool:
    text = str(value)
    return "\ufffd" in text or "??" in text or "\ufffd" in text


def read_posts() -> list[dict]:
    path = ROOT / "data" / "posts.json"
    if not path.exists():
        return [make_auto_post(shanghai_today().isoformat())]
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        raw = []
    posts: list[dict] = []
    seen: set[str] = set()
    for item in raw:
        date_str = item.get("date") or shanghai_today().isoformat()
        slug = item.get("slug") or None
        if bad_text(item.get("title", "")) or not item.get("intro") or not item.get("rows"):
            post = make_auto_post(date_str, slug=slug)
        else:
            post = make_auto_post(date_str, slug=slug)
            post.update(item)
            post.pop("en_title", None)
            post["status"] = post.get("status") or "published"
            post["slot"] = int(post.get("slot") or 1)
            post["keywords"] = normalize_keywords(post.get("keywords") or [], post.get("topic", ""))
        post["title"] = public_title(post.get("title", ""))
        post["keywords"] = normalize_keywords(post.get("keywords") or [], post.get("topic", ""))
        if post["slug"] not in seen:
            posts.append(post)
            seen.add(post["slug"])
    if not posts:
        posts.append(make_auto_post(shanghai_today().isoformat()))
    posts.sort(key=lambda item: item.get("date", ""), reverse=True)
    return posts


def write_posts(posts: list[dict]) -> None:
    (ROOT / "data" / "posts.json").write_text(json.dumps(posts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def published_posts(posts: list[dict]) -> list[dict]:
    return [post for post in posts if post.get("status", "published") == "published"]


def json_ld(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def keyword_meta(settings: dict, extra: list[str] | None = None) -> str:
    return ", ".join(list(dict.fromkeys(settings_keywords(settings) + (extra or []))))


def header_nav(settings: dict) -> str:
    return f"""
    <header class="top">
      <div class="top-inner">
        <a class="brand" href="/" aria-label="{esc(settings['brand_name'])}首页">
          <img class="brand-logo" src="/assets/tl8899-logo.png?v={ASSET_VERSION}" alt="{esc(settings['brand_name'])} {esc(settings['brand_subtitle'])} logo" width="290" height="297">
          <span><strong>{esc(settings['brand_name'])}</strong><small>{esc(settings['brand_subtitle'])}</small></span>
        </a>
        <button class="menu-toggle" type="button" aria-label="打开导航" aria-expanded="false">菜单</button>
        <nav>
          <a class="active" href="/">首页</a>
          <a href="/#about">关于我们</a>
          <a href="/#services">业务项目</a>
          <a href="/#hall">现场大厅</a>
          <a href="/blog/">文章</a>
          <a href="/contact/">联系我们</a>
        </nav>
        <div class="header-actions">
          <a class="contact-chip game" href="{GAME_PLAY_URL}" target="_blank" rel="noopener nofollow sponsored">进入游戏</a>
          <a class="contact-chip telegram" href="{esc(settings['telegram_url'])}">Telegram {esc(settings['telegram'])}</a>
          <a class="contact-chip mail" href="tel:{esc(settings['phone'])}">电话 {esc(settings['phone'])}</a>
        </div>
      </div>
    </header>
    """


def footer(settings: dict) -> str:
    return f"""
    <footer>
      <div class="footer-brand">
        <img class="footer-logo" src="/assets/tl8899-logo.png?v={ASSET_VERSION}" alt="{esc(settings['brand_name'])} logo" width="290" height="297">
        <div><strong>{esc(settings['brand_name'])} {esc(settings['brand_subtitle'])}</strong>
        <p>专业的真人娱乐资讯指南平台</p></div>
      </div>
      <nav>
        <a href="/">首页</a>
        <a href="/#about">关于我们</a>
        <a href="/#services">业务项目</a>
        <a href="/#hall">现场大厅</a>
        <a href="/blog/">文章</a>
        <a href="/contact/">联系我们</a>
        <a href="/privacy-policy/">隐私政策</a>
        <a href="/terms-of-service/">服务条款</a>
      </nav>
      <p class="footer-note">© 2026 {esc(settings['brand_name'])} {esc(settings['brand_subtitle'])}。保留所有权利。本站为资讯与指南站点，不提供任何形式的赌博服务。</p>
      <span class="age-mark">18+</span>
    </footer>
    <button id="top" aria-label="返回顶部">↑</button>
    <script src="/assets/site.js?v={ASSET_VERSION}" defer></script>
    """


def layout(settings: dict, title: str, description: str, canonical_path: str, body: str, *, page_type: str = "website", robots: str = "index, follow, max-image-preview:large", extra_keywords: list[str] | None = None, structured: dict | list[dict] | None = None) -> str:
    canonical = f"{SITE}{canonical_path}"
    org = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": settings["brand_subtitle"],
        "alternateName": ["腾龙公司", "腾龙娱乐官网", "皇家在线公司", "tamron casino"],
        "url": SITE,
        "email": settings["email"],
        "telephone": settings["phone"],
        "sameAs": [settings["telegram_url"]],
        "contactPoint": {"@type": "ContactPoint", "contactType": "内容与业务联系", "email": settings["email"], "telephone": settings["phone"], "url": settings["telegram_url"]},
    }
    scripts = [org]
    if structured:
        scripts.extend(structured if isinstance(structured, list) else [structured])
    script_tags = "\n".join(f'<script type="application/ld+json">{json_ld(item)}</script>' for item in scripts)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="keywords" content="{esc(keyword_meta(settings, extra_keywords))}">
  <meta name="robots" content="{esc(robots)}">
  <link rel="canonical" href="{esc(canonical)}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:type" content="{esc(page_type)}">
  <meta property="og:image" content="{SITE}/assets/casino-dealer-live.jpg">
  <meta property="og:image:alt" content="{esc(settings['brand_subtitle'])} 真人荷官资讯图片">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="{SITE}/assets/casino-dealer-live.jpg">
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
  <link rel="preload" href="/assets/site.css?v={ASSET_VERSION}" as="style">
  <link rel="stylesheet" href="/assets/site.css?v={ASSET_VERSION}">
  {script_tags}
</head>
<body>
  <a class="skip" href="#main">跳到正文</a>
  {header_nav(settings)}
  <main id="main">{body}</main>
  {footer(settings)}
</body>
</html>
"""


def article_cards(posts: list[dict], limit: int | None = None) -> str:
    visible = posts[:limit] if limit else posts
    return "\n".join(
        f"""<article class="article-card">
          <a class="article-card-media" href="/blog/{esc(post['slug'])}/" aria-label="阅读 {esc(post['title'])}">
            <picture><source srcset="{DEALER_IMAGE_WEBP}" type="image/webp"><img src="{DEALER_IMAGE_JPG}" alt="TL8899 LIVE 真人荷官与百家乐桌台" width="1280" height="720" loading="lazy" decoding="async"></picture>
          </a>
          <div class="article-card-body">
            <time datetime="{esc(post['date'])}">{esc(post['date'])}</time>
            <h3><a href="/blog/{esc(post['slug'])}/">{esc(post['title'])}</a></h3>
            <p>{esc(post['teaser'])}</p>
            <span class="read-more">阅读文章 →</span>
          </div>
    </article>"""
        for post in visible
    )


def blog_page_url(page: int) -> str:
    return "/blog/" if page == 1 else f"/blog/page/{page}/"


def blog_page_path(page: int) -> Path:
    if page == 1:
        return ROOT / "blog" / "index.html"
    return ROOT / "blog" / "page" / str(page) / "index.html"


def blog_page_count(posts: list[dict]) -> int:
    return max(1, (len(posts) + BLOG_PAGE_SIZE - 1) // BLOG_PAGE_SIZE)


def pagination_nav(current: int, total: int) -> str:
    if total <= 1:
        return ""
    items: list[str] = []
    if current > 1:
        items.append(f'<a class="page-link page-prev" href="{blog_page_url(current - 1)}">上一页</a>')
    for page in range(1, total + 1):
        if page == current:
            items.append(f'<span class="page-link current" aria-current="page">{page}</span>')
        else:
            items.append(f'<a class="page-link" href="{blog_page_url(page)}">{page}</a>')
    if current < total:
        items.append(f'<a class="page-link page-next" href="{blog_page_url(current + 1)}">下一页</a>')
    return '<nav class="pagination" aria-label="文章分页">' + ''.join(items) + '</nav>'


def latest_home_list(posts: list[dict], limit: int = 4) -> str:
    icons = ["🂡", "🐉", "♉", "🎲"]
    items = []
    for idx, post in enumerate(posts[:limit]):
        items.append(
            f"""<a class="mini-post" href="/blog/{esc(post['slug'])}/">
              <span class="mini-thumb">{icons[idx % len(icons)]}</span>
              <span><strong>{esc(post['title'])}</strong><small>{esc(post['date'])}</small></span>
            </a>"""
        )
    return "\n".join(items)


def write_assets(settings: dict) -> None:
    css = """
:root{--blue:#075db3;--blue-2:#0a76d1;--gold:#f3b42e;--gold-2:#d98b13;--dark:#101621;--ink:#20242c;--muted:#687383;--line:#e6ebf2;--panel:#fff;--bg:#f6f8fb}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;font-family:Inter,"Microsoft YaHei","PingFang SC",Arial,sans-serif;color:var(--ink);background:var(--bg);line-height:1.72}a{color:inherit;text-decoration:none}.skip{position:absolute;left:-999px;top:8px;z-index:100;padding:10px 14px;background:#fff}.skip:focus{left:8px}.top{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:28px;padding:16px clamp(22px,5vw,82px);background:rgba(255,255,255,.96);border-bottom:1px solid var(--line);box-shadow:0 10px 30px rgba(20,30,45,.07);backdrop-filter:blur(12px)}.brand{display:flex;align-items:center;gap:12px;min-width:260px}.crest{display:grid;place-items:center;width:58px;height:58px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#ffe58c,#b51512 48%,#201109 49%,#f6d675 56%,#bb7a14);color:#fff;font-weight:950;letter-spacing:-.05em;box-shadow:0 10px 24px rgba(138,15,8,.22)}.brand strong{display:block;color:#c28a12;font-size:26px;line-height:1}.brand small{display:block;color:#765612;font-weight:800;text-transform:uppercase;letter-spacing:.08em}.top nav{display:flex;align-items:center;gap:24px;margin-left:auto}.top nav a{font-weight:850}.top nav a:hover,.admin-link{color:var(--blue)}.quick{color:var(--blue);font-weight:850;white-space:nowrap}.menu-toggle{display:none}.hero{min-height:650px;display:grid;align-items:center;padding:72px clamp(22px,6vw,96px);position:relative;overflow:hidden;background:linear-gradient(90deg,rgba(0,0,0,.74),rgba(0,0,0,.34)),radial-gradient(circle at 78% 45%,rgba(243,195,81,.42),transparent 27rem),linear-gradient(135deg,#1b2738,#02060b 65%)}.hero:before{content:"";position:absolute;inset:0;background:repeating-linear-gradient(90deg,rgba(255,255,255,.07) 0 2px,transparent 2px 82px),radial-gradient(circle at 75% 70%,rgba(11,111,171,.28),transparent 24rem);opacity:.78}.hero:after{content:"♠ ♥ ♦ ♣";position:absolute;right:clamp(22px,8vw,130px);bottom:54px;font-size:clamp(40px,9vw,132px);color:rgba(243,195,81,.2);letter-spacing:.18em}.hero-inner{position:relative;max-width:890px;color:#fff}.eyebrow{color:var(--gold);font-weight:950;letter-spacing:.14em;text-transform:uppercase}.hero h1{font-size:clamp(42px,7vw,88px);line-height:1.02;margin:12px 0;white-space:pre-line}.hero p{font-size:20px;max-width:740px;color:#e8edf4}.actions{display:flex;flex-wrap:wrap;gap:14px;margin-top:28px}.btn{display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:12px 22px;border-radius:999px;border:1px solid rgba(255,255,255,.35);font-weight:950;cursor:pointer}.btn.primary{background:linear-gradient(135deg,var(--gold),var(--gold-2));border:0;color:#1b1203}.btn.dark{border-color:var(--line);color:var(--ink);background:#fff}.danger{background:#fff1f1!important;color:#a01818!important;border-color:#ffcaca!important}.contact-strip{display:flex;flex-wrap:wrap;gap:12px;margin-top:24px;padding:16px;border:1px solid rgba(243,195,81,.45);border-radius:18px;background:rgba(0,0,0,.28);font-weight:900}.contact-strip a{color:var(--gold)}.section{padding:76px clamp(22px,6vw,96px)}.section.white{background:#fff}.head{max-width:900px;margin-bottom:32px}.head h1,.head h2{font-size:clamp(32px,4vw,54px);line-height:1.1;margin:0}.head p{color:var(--muted);font-size:18px}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}.card{padding:28px;border-radius:24px;background:#fff;border:1px solid var(--line);box-shadow:0 18px 50px rgba(20,30,45,.08)}.card.dark{background:linear-gradient(160deg,#111b28,#0b1018);color:#fff;border:0}.card .icon{font-size:42px;color:var(--gold);font-weight:950}.card h3{font-size:24px;margin:14px 0 8px}.card p{color:var(--muted);margin:0}.card.dark p{color:#c7d1df}.hall{display:grid;grid-template-columns:1.05fr .95fr;gap:28px;align-items:center}.hall-art{min-height:370px;border-radius:30px;background:linear-gradient(180deg,rgba(0,0,0,.1),rgba(0,0,0,.62)),repeating-conic-gradient(from 18deg,#123f31 0 12deg,#7e1111 12deg 24deg,#111827 24deg 36deg);box-shadow:inset 0 0 0 18px rgba(243,195,81,.18),0 24px 70px rgba(0,0,0,.18)}.articles{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}.article-card{display:flex;flex-direction:column;min-height:235px;padding:22px;border:1px solid var(--line);border-radius:22px;background:#fff;transition:transform .2s ease,box-shadow .2s ease}.article-card:hover{transform:translateY(-3px);box-shadow:0 18px 50px rgba(20,30,45,.1)}.article-card time{font-weight:900;color:var(--blue)}.article-card h3{margin:8px 0;font-size:21px}.article-card p{color:var(--muted)}.read-more{margin-top:auto;color:var(--blue);font-weight:900}.contact-box{display:grid;grid-template-columns:1fr 1fr;gap:20px}.contact-pill{display:block;padding:18px 20px;border-radius:18px;background:#10233b;color:#fff;font-size:22px;font-weight:950}.contact-pill.gold{background:#2b2514;color:var(--gold)}.article{max-width:980px;margin:0 auto;padding:70px 22px}.article h1{font-size:clamp(34px,5vw,58px);line-height:1.1}.article h2{font-size:30px;margin-top:38px}.article p,.article li{color:#4d5562}.meta-line{color:var(--blue);font-weight:900}.table{overflow:auto;border:1px solid var(--line);border-radius:18px;margin:22px 0}.table table{width:100%;border-collapse:collapse;min-width:680px;background:#fff}.table th,.table td{padding:14px;border-bottom:1px solid var(--line);text-align:left}.table th{background:#f1f5fb;color:var(--blue)}.note{padding:16px;border-radius:18px;background:#fff8df;border:1px solid #f1cf67;color:#4e3905}.tag-list{display:flex;gap:10px;flex-wrap:wrap}.tag-list span{padding:8px 12px;border-radius:999px;background:#edf4ff;color:#075db3;font-weight:800}.admin-wrap{padding:36px clamp(18px,4vw,60px) 70px;background:#f6f8fb}.admin-hero{display:flex;justify-content:space-between;gap:20px;align-items:flex-start;margin-bottom:24px}.admin-hero h1{font-size:42px;margin:0}.admin-tabs{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0}.admin-tabs a{padding:10px 14px;border-radius:999px;background:#fff;border:1px solid var(--line);font-weight:900}.admin-layout{display:grid;grid-template-columns:1.2fr .8fr;gap:22px;align-items:start}.admin-panel{background:#fff;border:1px solid var(--line);border-radius:24px;padding:24px;box-shadow:0 18px 45px rgba(20,30,45,.07);margin-bottom:22px}.admin-panel h2{margin:0 0 14px;font-size:24px}.admin-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:22px}.stat{padding:18px;border-radius:20px;background:#fff;border:1px solid var(--line)}.stat strong{display:block;font-size:28px;color:var(--blue)}label{display:block;font-weight:900;margin:12px 0 6px}input,textarea,select{width:100%;padding:12px 14px;border:1px solid #dbe3ef;border-radius:14px;font:inherit;background:#fff}textarea{min-height:110px;resize:vertical}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}.post-row{display:grid;grid-template-columns:110px 1fr auto;gap:12px;align-items:center;padding:12px 0;border-bottom:1px solid var(--line)}.post-row:last-child{border-bottom:0}.row-actions{display:flex;gap:8px;flex-wrap:wrap}.small{font-size:13px;color:var(--muted)}.flash{padding:14px 16px;border-radius:16px;background:#eaf7ef;color:#11602f;border:1px solid #bae7c8;margin-bottom:18px;font-weight:850}.error{background:#fff0f0;color:#9c1b1b;border-color:#ffcaca}footer{display:flex;justify-content:space-between;gap:20px;padding:34px clamp(22px,6vw,96px);background:#101621;color:#cfd7e3}footer strong{color:#fff}footer nav{display:flex;gap:18px;flex-wrap:wrap}#top{position:fixed;right:18px;bottom:18px;width:46px;height:46px;border:0;border-radius:50%;background:var(--gold);font-weight:950;opacity:0;pointer-events:none;transition:opacity .2s ease}#top.show{opacity:1;pointer-events:auto}@media(max-width:1100px){.admin-layout,.admin-stats{grid-template-columns:1fr}.post-row{grid-template-columns:1fr}.articles,.grid,.hall,.contact-box,.form-grid{grid-template-columns:1fr}}@media(max-width:980px){.top{align-items:flex-start;flex-direction:column}.top nav{margin-left:0;flex-wrap:wrap;display:none}.top.open nav{display:flex}.menu-toggle{display:inline-flex;border:1px solid var(--line);border-radius:999px;background:#fff;padding:9px 14px;font-weight:900}.quick{white-space:normal}.hero{min-height:auto}.brand{min-width:0}}
"""
    css += """
/* Premium TL8899 visual layer */
:root{--blue:#075db3;--blue-2:#0a76d1;--gold:#f5b83f;--gold-2:#d4840e;--red:#b71718;--dark:#080d15;--ink:#17202c;--muted:#687385;--line:#e6d8b8;--panel:#fff;--bg:#f5f1e8;--shadow:0 24px 70px rgba(10,16,26,.14)}body{background:linear-gradient(180deg,#fff 0,#f5f1e8 34%,#fff 100%);color:var(--ink)}.top{min-height:94px;padding:18px clamp(24px,5vw,86px);background:rgba(255,255,255,.94);border-bottom:1px solid rgba(160,116,31,.18);box-shadow:0 18px 48px rgba(13,20,33,.09)}.brand{gap:14px;min-width:310px}.crest{width:64px;height:64px;background:radial-gradient(circle at 32% 25%,#fff1ad 0 12%,#e0a326 26%,#c01f1f 52%,#2a1110 53%,#f2c764 64%,#8a4e05 100%);border:1px solid rgba(255,220,122,.85);box-shadow:0 14px 34px rgba(140,33,20,.22),inset 0 2px 0 rgba(255,255,255,.48);font-family:Georgia,serif}.brand strong{font-size:28px;color:#bd7d08;letter-spacing:.02em}.brand small{color:#805310;font-size:12px}.top nav{gap:28px}.top nav a{position:relative;color:#1c2532;font-size:16px}.top nav a:after{content:"";position:absolute;left:0;right:0;bottom:-8px;height:2px;background:linear-gradient(90deg,var(--gold),var(--red));transform:scaleX(0);transform-origin:left;transition:transform .22s ease}.top nav a:hover:after{transform:scaleX(1)}.quick{padding:10px 14px;border-radius:999px;background:#fff7e7;border:1px solid rgba(200,139,24,.28);color:#9a6206}.hero{min-height:720px;grid-template-columns:minmax(0,760px) minmax(360px,1fr);padding:88px clamp(24px,6vw,104px);background:radial-gradient(circle at 78% 28%,rgba(245,184,63,.25),transparent 24rem),linear-gradient(115deg,rgba(5,8,14,.96),rgba(8,13,21,.86) 53%,rgba(34,22,6,.84)),linear-gradient(135deg,#05080e,#111a27);border-bottom:1px solid rgba(245,184,63,.24)}.hero:before{background:linear-gradient(90deg,rgba(245,184,63,.12) 1px,transparent 1px),linear-gradient(0deg,rgba(255,255,255,.05) 1px,transparent 1px);background-size:82px 82px;mask-image:linear-gradient(90deg,#000 0,transparent 94%);opacity:.55}.hero:after{content:"";top:122px;right:clamp(22px,6vw,104px);bottom:84px;width:min(42vw,530px);font-size:0;letter-spacing:0;border-radius:36px;background:radial-gradient(circle at 50% 44%,rgba(245,184,63,.5) 0 8%,transparent 9%),radial-gradient(circle at 50% 44%,#111827 0 20%,#bd1718 21% 29%,#111827 30% 39%,#f4b73d 40% 44%,transparent 45%),linear-gradient(150deg,rgba(255,255,255,.13),rgba(255,255,255,.02));border:1px solid rgba(245,184,63,.42);box-shadow:0 36px 90px rgba(0,0,0,.34),inset 0 1px 0 rgba(255,255,255,.22)}.hero-inner{max-width:790px}.hero h1{font-size:clamp(46px,6.6vw,92px);letter-spacing:-.045em;text-shadow:0 18px 45px rgba(0,0,0,.35)}.hero p{max-width:700px;color:#e9edf4;font-size:20px}.eyebrow{color:#ffd16a;letter-spacing:.18em}.btn{min-height:54px;padding:14px 26px;border-radius:16px;font-size:16px;box-shadow:none}.btn.primary{background:linear-gradient(135deg,#ffd36b,#e78b0d);box-shadow:0 16px 34px rgba(218,132,14,.28)}.hero .btn:not(.primary){background:rgba(255,255,255,.09);border-color:rgba(255,255,255,.28);color:#fff}.contact-strip{max-width:720px;border-color:rgba(245,184,63,.36);background:rgba(7,13,22,.64);box-shadow:inset 0 1px 0 rgba(255,255,255,.08)}.section{padding:92px clamp(24px,6vw,104px)}.section.white{background:linear-gradient(180deg,#fff,#fffaf1)}.head{max-width:980px;margin-bottom:38px}.head h1,.head h2{font-size:clamp(36px,4.4vw,64px);letter-spacing:-.035em}.head p{font-size:19px;color:#5c6675}.grid{gap:24px}.card{border-color:rgba(172,125,37,.2);border-radius:28px;background:rgba(255,255,255,.88);box-shadow:var(--shadow);transition:transform .22s ease,box-shadow .22s ease}.card:hover{transform:translateY(-5px);box-shadow:0 30px 80px rgba(10,16,26,.18)}.card.dark{position:relative;overflow:hidden;background:linear-gradient(155deg,#101826,#0c111a 62%,#261707);border:1px solid rgba(245,184,63,.28)}.card.dark:before{content:"";position:absolute;inset:auto -60px -80px auto;width:190px;height:190px;border-radius:50%;background:rgba(245,184,63,.12)}.card .icon{font-family:Georgia,serif;color:#d99818}.hall{gap:36px}.hall-art{position:relative;min-height:430px;border-radius:38px;background:radial-gradient(circle at 50% 50%,rgba(245,184,63,.7) 0 7%,transparent 8%),radial-gradient(circle at 50% 52%,#0c1420 0 22%,#a21518 23% 31%,#0c1420 32% 42%,#d99a18 43% 46%,transparent 47%),linear-gradient(145deg,#0a111c,#1e150b);box-shadow:inset 0 0 0 1px rgba(245,184,63,.35),inset 0 0 0 18px rgba(255,255,255,.03),0 30px 90px rgba(18,16,12,.26)}.hall-art:before{content:"TL8899 LIVE";position:absolute;left:34px;top:32px;color:#f8d27b;font-weight:950;letter-spacing:.16em}.hall-art:after{content:"BACCARAT  DRAGON TIGER  NIU NIU";position:absolute;left:34px;right:34px;bottom:30px;color:#fff;font-weight:900;letter-spacing:.1em}.articles{gap:24px}.article-card{position:relative;overflow:hidden;min-height:260px;border-radius:28px;border-color:rgba(172,125,37,.22);background:linear-gradient(180deg,#fff,#fffaf1);box-shadow:0 18px 55px rgba(15,24,38,.08)}.article-card:before{content:"";position:absolute;left:0;top:0;bottom:0;width:5px;background:linear-gradient(180deg,var(--gold),var(--red))}.article-card time{color:#b27307}.article-card h3{font-size:22px;line-height:1.35}.read-more{color:#9b6307}.contact-box{gap:22px}.contact-pill{border:1px solid rgba(245,184,63,.28);background:linear-gradient(135deg,#101827,#142947);box-shadow:0 18px 50px rgba(10,22,42,.16)}.contact-pill.gold{background:linear-gradient(135deg,#fff3c8,#f0a21d);color:#1f1606}.article{max-width:1040px;background:#fff;margin:52px auto;border:1px solid rgba(172,125,37,.18);border-radius:34px;padding:54px clamp(24px,5vw,70px);box-shadow:var(--shadow)}.article h1{font-size:clamp(34px,4.8vw,64px)}.article h2{color:#111827}.note{background:linear-gradient(135deg,#fff8df,#fff1bd);border-color:#e7bd49}.tag-list span{background:#fff5db;color:#8a5a07;border:1px solid rgba(180,124,20,.18)}footer{background:linear-gradient(135deg,#080d15,#101827);border-top:1px solid rgba(245,184,63,.18)}#top{background:linear-gradient(135deg,#ffd36b,#d4840e);box-shadow:0 16px 34px rgba(0,0,0,.22)}@media(max-width:1120px){.hero{grid-template-columns:1fr}.hero:after{position:relative;display:block;right:auto;top:auto;bottom:auto;width:min(100%,520px);height:340px;margin-top:36px}.hero-inner{max-width:850px}}@media(max-width:760px){.top{min-height:auto;padding:14px 18px}.brand strong{font-size:22px}.crest{width:52px;height:52px}.hero{padding:58px 20px}.hero h1{font-size:42px}.hero p{font-size:17px}.section{padding:62px 20px}.article{margin:24px 12px;padding:30px 18px;border-radius:24px}.quick{font-size:14px}.contact-strip{font-size:14px}.hall-art{min-height:300px}}
"""
    css += """
.hall-art:before{content:"腾龙公司"}
.hall-art:after{content:"百家乐  龙虎  牛牛"}
"""
    css += """
/* Screenshot reference layout */
body{background:#05070b;color:#141922}
main{background:#fff}.top{position:sticky;top:0;z-index:60;display:block;min-height:0;padding:0;background:#fff;border-bottom:1px solid #eceff5;box-shadow:0 8px 24px rgba(10,16,28,.06)}.top-inner{max-width:1220px;height:58px;margin:0 auto;padding:0 28px;display:flex;align-items:center;gap:24px}.brand{min-width:210px;gap:10px}.crest{width:44px;height:44px;font-size:15px;border:2px solid #f1c269;background:radial-gradient(circle at 33% 24%,#fff6bf 0 9%,#e0a332 21%,#be1917 48%,#2b100e 49%,#f7cc62 62%,#7a4308 100%);box-shadow:0 8px 20px rgba(126,34,20,.22);letter-spacing:-.05em}.brand strong{font-size:22px;line-height:1;color:#b97808}.brand small{font-size:11px;letter-spacing:.08em;color:#6e4708}.top nav{display:flex;margin-left:auto;gap:24px;align-items:center}.top nav a{position:relative;font-size:13px;font-weight:900;color:#1c2330}.top nav a:after{content:"";position:absolute;left:35%;right:35%;bottom:-12px;height:2px;background:#c5161d;opacity:0;transform:scaleX(.5);transition:.18s ease}.top nav a:hover:after,.top nav a.active:after{left:18%;right:18%;opacity:1;transform:scaleX(1)}.header-actions{display:flex;gap:10px;align-items:center}.contact-chip{display:inline-flex;align-items:center;gap:6px;min-height:30px;padding:0 12px;border-radius:6px;border:1px solid #d9e8fb;background:#fff;color:#0969c3;font-size:11px;font-weight:900;white-space:nowrap}.contact-chip:before{content:"";width:17px;height:17px;border-radius:50%;display:inline-grid;place-items:center;background:#2396f3}.contact-chip.telegram:before{content:"↗";color:#fff;font-size:12px}.contact-chip.mail{border-color:#e8c987;color:#9a6206;background:#fffdf8}.contact-chip.mail:before{content:"✉";border-radius:4px;background:#d9a63a;color:#fff}.menu-toggle{display:none}
.casino-hero{position:relative;overflow:hidden;display:grid;grid-template-columns:minmax(440px,1fr) minmax(380px,.98fr);gap:32px;align-items:center;min-height:365px;padding:34px max(34px,calc((100vw - 1180px)/2 + 34px));background:radial-gradient(circle at 72% 44%,rgba(235,175,58,.22),transparent 20rem),linear-gradient(90deg,#080d14 0,#050a11 53%,#121008 100%);border-bottom:1px solid #d9dfe8}.casino-hero:before{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(245,183,63,.08) 1px,transparent 1px);background-size:42px 100%;opacity:.75;pointer-events:none}.casino-hero:after{content:"";position:absolute;inset:auto 0 0 0;height:80px;background:linear-gradient(180deg,transparent,rgba(0,0,0,.22));pointer-events:none}.hero-copy,.hero-showpiece{position:relative;z-index:1}.hero-kicker{margin:0 0 8px;color:#fff;font-size:13px;font-weight:850}.hero-kicker span{color:#f0b639}.hero-copy h1{margin:0 0 10px;line-height:.98;letter-spacing:-.045em;text-shadow:0 14px 38px rgba(0,0,0,.38)}.hero-copy h1 span{display:block;color:#f7c768;font-size:clamp(46px,5.6vw,78px);font-family:Georgia,"Microsoft YaHei",serif;font-weight:950}.hero-copy h1 strong{display:block;color:#fff;font-size:clamp(36px,4vw,58px);font-weight:950}.hero-text{max-width:590px;margin:14px 0 20px;color:#eef3f7;font-size:15px;line-height:1.68}.hero-buttons{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:18px}.hero-btn{display:inline-flex;align-items:center;justify-content:center;height:38px;padding:0 18px;border-radius:7px;font-size:13px;font-weight:950;border:1px solid rgba(255,255,255,.25)}.hero-btn.primary{color:#301d04;background:linear-gradient(135deg,#f8d06c,#bd760b);box-shadow:0 10px 20px rgba(201,136,27,.25)}.hero-btn.dark{color:#fff;background:rgba(255,255,255,.08);border-color:rgba(245,195,86,.38)}.trust-row{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;max-width:560px;margin-bottom:12px}.trust-row span{position:relative;min-height:42px;padding:5px 6px 5px 44px;color:#fff;font-size:12px;font-weight:900}.trust-row span:before{content:"";position:absolute;left:0;top:2px;width:31px;height:31px;border-radius:50%;border:1px solid rgba(245,190,72,.65);background:radial-gradient(circle,#17212e,#080c12);box-shadow:0 0 0 4px rgba(245,190,72,.08)}.trust-row span:nth-child(1):after{content:"盾"}.trust-row span:nth-child(2):after{content:"闪"}.trust-row span:nth-child(3):after{content:"安"}.trust-row span:after{position:absolute;left:7px;top:8px;color:#f3bd48;font-size:13px;font-weight:950}.trust-row small{display:block;margin-top:2px;color:#b9c5d0;font-size:11px;font-weight:700}.responsible-bar{display:flex;align-items:center;gap:8px;max-width:560px;min-height:30px;padding:6px 11px;border-radius:7px;border:1px solid rgba(210,54,55,.78);background:rgba(125,24,26,.22);color:#ffe1df;font-size:12px}.responsible-bar b{display:inline-grid;place-items:center;width:24px;height:24px;border-radius:50%;border:1px solid #e74848;color:#ff7272;font-size:10px}
.hero-showpiece{height:320px}.royal-crest{position:absolute;left:50%;top:50%;transform:translate(-50%,-48%);width:260px;height:260px;border-radius:50%;display:grid;place-items:center;background:radial-gradient(circle at 50% 45%,#812018 0 24%,#e3ad3c 25% 30%,#17110c 31% 46%,#c99331 47% 52%,transparent 53%),radial-gradient(circle,#3a1d10,#0d0b0b 68%);border:3px solid #f4ce76;box-shadow:0 0 0 16px rgba(245,183,63,.11),0 26px 80px rgba(0,0,0,.55)}.royal-crest:before{content:"";position:absolute;inset:-32px;border-radius:42px;background:linear-gradient(135deg,transparent 13%,rgba(245,194,80,.33) 14% 16%,transparent 17% 83%,rgba(245,194,80,.33) 84% 86%,transparent 87%);filter:drop-shadow(0 20px 20px rgba(0,0,0,.28));z-index:-1}.royal-crest:after{content:"TL8899 LIVE";position:absolute;left:50%;bottom:28px;transform:translateX(-50%) rotate(-5deg);padding:4px 24px;border-radius:4px;background:linear-gradient(135deg,#392311,#040404);border:1px solid #d6a037;color:#f5c45d;font-family:Georgia,serif;font-size:20px;font-weight:950;white-space:nowrap}.royal-crest strong{font-family:Georgia,serif;font-size:78px;color:#f9d57d;text-shadow:0 4px 0 #611,0 12px 24px rgba(0,0,0,.55)}.royal-crest em{display:none}.crown{position:absolute;top:-56px;left:50%;transform:translateX(-50%);font-size:70px;color:#f8cf69;text-shadow:0 12px 25px rgba(0,0,0,.5)}.hero-showpiece .card{position:absolute;width:64px;height:92px;border-radius:9px;background:#fffdf5;border:1px solid #ebd8a7;color:#171717;font-family:Georgia,serif;font-size:22px;font-weight:950;box-shadow:0 18px 30px rgba(0,0,0,.34)}.card-a{left:24px;top:82px;transform:rotate(-18deg)}.card-b{left:78px;top:76px;transform:rotate(-6deg);color:#b61a1d}.chip-stack{position:absolute;left:28px;bottom:38px;width:94px;height:70px;background:radial-gradient(ellipse at center,#fff 0 18%,#d92724 19% 44%,#f8f0e1 45% 54%,#c91d21 55%);border-radius:50%;box-shadow:0 12px 0 #7f1818,0 24px 0 #d9d2bd,0 36px 0 #a41619,22px 11px 0 #d11e22,22px 23px 0 #f2ead7,22px 35px 0 #991318}.roulette-wheel{position:absolute;right:38px;top:94px;width:132px;height:132px;border-radius:50%;background:repeating-conic-gradient(#151515 0 10deg,#ad171b 10deg 20deg,#111 20deg 30deg,#d5a33e 30deg 34deg),radial-gradient(circle,#111 0 42%,#d8a13a 43% 48%,transparent 49%);border:8px solid #17100b;box-shadow:inset 0 0 0 4px #c18a23,0 18px 36px rgba(0,0,0,.42)}.gold-spade{position:absolute;right:10px;bottom:22px;width:80px;height:80px;border-radius:50%;display:grid;place-items:center;background:radial-gradient(circle,#2b2313,#050505 70%);border:2px solid #d3a33f;color:#f8d27d;font-size:54px;box-shadow:0 16px 38px rgba(0,0,0,.4)}
.game-strip{position:relative;z-index:3;display:grid;grid-template-columns:repeat(6,1fr);max-width:1168px;margin:0 auto;padding:12px 12px;background:#fff;border:1px solid #edf0f5;border-top:0;box-shadow:0 10px 30px rgba(14,20,30,.08)}.game-strip a{display:grid;grid-template-columns:46px 1fr;column-gap:11px;align-items:center;min-height:66px;padding:6px 14px;border-right:1px solid #edf0f5}.game-strip a:last-child{border-right:0}.game-strip span{grid-row:1/4;width:45px;height:45px;border-radius:50%;display:grid;place-items:center;background:radial-gradient(circle at 35% 25%,#fff4c6,#0b0f16 43%,#090b0f 72%);border:1px solid #d4a84d;color:#f5c35f;font-size:22px;font-weight:950}.game-strip strong{font-size:15px;line-height:1;color:#1b2029}.game-strip small{font-size:11px;color:#68717d}.game-strip em{font-style:normal;color:#d33132;font-size:11px;font-weight:900}
.home-cards{display:grid;grid-template-columns:1.15fr .96fr .96fr .98fr 1fr;gap:12px;max-width:1168px;margin:0 auto;padding:14px 12px 18px;background:#f7f8fb}.info-panel{min-height:210px;padding:14px;border-radius:8px;background:#fff;border:1px solid #e7ebf1;box-shadow:0 6px 18px rgba(14,20,30,.05)}.info-panel h2{position:relative;margin:0 0 10px;color:#1f2630;font-size:15px}.info-panel h2:after{content:"";display:block;width:22px;height:2px;margin-top:5px;background:#c89127}.info-panel p{font-size:12px;line-height:1.72;color:#4d5664;margin:8px 0}.panel-media{height:86px;border-radius:6px;margin-bottom:10px;overflow:hidden;position:relative;background:#111}.panel-media.lounge{background:linear-gradient(160deg,rgba(0,0,0,.1),rgba(0,0,0,.6)),repeating-linear-gradient(90deg,#1b1510 0 32px,#2e2114 32px 64px);border:1px solid #2c2419}.panel-media.lounge span{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:44px;height:44px;border-radius:50%;display:grid;place-items:center;background:radial-gradient(circle,#a91618,#150d0d);border:2px solid #e1b65a;color:#fbd172;font-weight:950}.panel-media.dealer{height:96px;background:radial-gradient(circle at 50% 22%,#f0d2ba 0 9%,transparent 10%),linear-gradient(90deg,transparent 43%,#141922 44% 56%,transparent 57%),radial-gradient(ellipse at center,#254c2e 0 38%,#14271b 39% 65%,#0e1218 66%);border:1px solid #4a3111}.panel-media.dealer:after{content:"";position:absolute;left:8%;right:8%;bottom:10px;height:28px;border-radius:50%;background:linear-gradient(90deg,#194f2d,#0d301b);border:1px solid rgba(235,185,70,.42)}.panel-media.dealer span{position:absolute;left:50%;bottom:16px;transform:translateX(-50%);color:#f8ca63;font-weight:950;font-size:11px;letter-spacing:.12em}.service-list{list-style:none;padding:0;margin:2px 0 12px;display:grid;gap:9px}.service-list li{display:grid;grid-template-columns:28px 1fr;gap:10px;align-items:start}.service-list b{width:26px;height:26px;border-radius:50%;display:grid;place-items:center;background:#171716;color:#e2ad36;font-size:12px}.service-list span{font-size:12px;font-weight:900;color:#202733}.service-list small{display:block;margin-top:2px;color:#7a8390;font-size:11px;font-weight:600}.outline-link,.gold-link{display:inline-flex;align-items:center;justify-content:center;min-height:30px;padding:0 18px;border-radius:5px;border:1px solid #e3b45d;color:#bb7d0e;font-size:12px;font-weight:900}.gold-link{background:linear-gradient(135deg,#d8a239,#ad6f0a);color:#fff;border:0}.wide{width:100%}.text-link{color:#c02e2e;font-size:12px;font-weight:950}.mini-post{display:grid;grid-template-columns:40px 1fr;gap:9px;align-items:center;padding:5px 0;border-bottom:1px solid #edf0f5}.mini-post:last-of-type{border-bottom:0}.mini-thumb{display:grid;place-items:center;width:36px;height:36px;border-radius:5px;background:#161616;color:#e7b348;border:1px solid #e5c176;font-size:20px}.mini-post strong{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;font-size:12px;line-height:1.35;color:#202733}.mini-post small{display:block;margin-top:3px;font-size:11px;color:#78818e}.contact-panel p{display:grid;grid-template-columns:66px 1fr;gap:8px;margin:8px 0;font-size:11px}.contact-panel b{color:#354052}.contact-panel span{color:#677282}
footer{position:relative;display:grid;grid-template-columns:1fr auto 1.1fr auto;align-items:center;gap:24px;min-height:72px;padding:14px max(34px,calc((100vw - 1180px)/2 + 34px));background:linear-gradient(135deg,#060b12,#0e1723);border-top:1px solid rgba(246,195,86,.18);color:#dbe3ed}.footer-brand{display:flex;align-items:center;gap:10px}.footer-brand .crest{width:36px;height:36px;font-size:12px}.footer-brand strong{font-size:14px;color:#f8d06d}.footer-brand p{margin:1px 0 0;font-size:11px;color:#b8c4d0}footer nav{display:flex;gap:26px;font-size:12px;color:#fff}.footer-note{max-width:390px;margin:0;color:#97a4b3;font-size:11px;text-align:right}.age-mark{width:38px;height:38px;border-radius:50%;display:grid;place-items:center;border:1px solid #d23a39;color:#fff;background:#121923;font-weight:900}
@media(max-width:1180px){.top-inner{padding:0 18px}.header-actions .mail{display:none}.casino-hero{grid-template-columns:1fr .82fr;padding:30px 60px}.game-strip,.home-cards{max-width:calc(100% - 48px)}.home-cards{grid-template-columns:repeat(3,1fr)}.contact-panel{grid-column:span 2}}@media(max-width:900px){.top-inner{height:auto;min-height:64px;align-items:flex-start;flex-wrap:wrap;padding:12px 18px}.top nav{display:none;width:100%;order:4;margin-left:0;gap:14px;flex-wrap:wrap}.top.open nav{display:flex}.menu-toggle{display:inline-flex;margin-left:auto;border:1px solid #e5e9f0;border-radius:999px;background:#fff;padding:7px 12px;font-weight:900}.header-actions{width:100%;order:3}.casino-hero{grid-template-columns:1fr;min-height:0;padding:34px 22px}.hero-showpiece{height:250px}.game-strip{grid-template-columns:repeat(2,1fr);max-width:100%;padding:8px}.game-strip a{border-bottom:1px solid #edf0f5}.home-cards{max-width:100%;grid-template-columns:1fr;padding:12px}.contact-panel{grid-column:auto}footer{grid-template-columns:1fr;padding:20px;text-align:left}footer nav{gap:14px;flex-wrap:wrap}.footer-note{text-align:left}.age-mark{position:absolute;right:20px;bottom:18px}}@media(max-width:560px){.brand{min-width:0}.brand strong{font-size:20px}.contact-chip{font-size:10px}.hero-copy h1 span{font-size:42px}.hero-copy h1 strong{font-size:34px}.trust-row{grid-template-columns:1fr}.royal-crest{width:205px;height:205px}.royal-crest strong{font-size:60px}.card-a{left:8px}.card-b{left:54px}.roulette-wheel{right:8px;width:98px;height:98px}.gold-spade{width:58px;height:58px;font-size:38px}.chip-stack{left:12px;transform:scale(.76);transform-origin:left bottom}.game-strip{grid-template-columns:1fr}}
"""
    css += """
@media(min-width:901px){.top-inner{height:54px;padding:0 20px}.brand{min-width:176px}.crest{width:40px;height:40px}.brand strong{font-size:21px}.brand small{font-size:10px}.top nav{gap:18px}.top nav a{font-size:12px}.header-actions{gap:8px}.header-actions .mail{display:inline-flex!important}.contact-chip{min-height:28px;padding:0 9px;font-size:10px}.contact-chip:before{width:15px;height:15px}.casino-hero{grid-template-columns:minmax(420px,1fr) minmax(420px,.98fr);min-height:292px;gap:16px;padding:22px max(30px,calc((100vw - 1180px)/2 + 30px))}.hero-kicker{font-size:12px;margin-bottom:5px}.hero-copy h1{margin-bottom:7px}.hero-copy h1 span{font-size:clamp(42px,5vw,58px)}.hero-copy h1 strong{font-size:clamp(32px,3.9vw,45px)}.hero-text{max-width:500px;margin:10px 0 14px;font-size:12px;line-height:1.56}.hero-buttons{margin-bottom:12px}.hero-btn{height:31px;padding:0 15px;font-size:12px;border-radius:6px}.trust-row{max-width:500px;gap:10px;margin-bottom:7px}.trust-row span{min-height:35px;padding:2px 4px 2px 37px;font-size:11px}.trust-row span:before{width:27px;height:27px}.trust-row span:after{left:6px;top:6px;font-size:12px}.trust-row small{font-size:10px}.responsible-bar{max-width:500px;min-height:27px;padding:4px 10px;font-size:11px}.responsible-bar b{width:22px;height:22px}.hero-showpiece{height:248px}.royal-crest{width:214px;height:214px}.royal-crest strong{font-size:64px}.royal-crest:after{bottom:24px;font-size:16px;padding:3px 20px}.crown{top:-47px;font-size:57px}.hero-showpiece .card{width:52px;height:76px;font-size:18px}.card-a{left:54px;top:70px}.card-b{left:96px;top:64px}.chip-stack{left:62px;bottom:34px;transform:scale(.78);transform-origin:left bottom}.roulette-wheel{right:54px;top:76px;width:104px;height:104px;border-width:6px}.gold-spade{right:22px;bottom:20px;width:62px;height:62px;font-size:41px}.game-strip{max-width:1168px;padding:8px 10px}.game-strip a{min-height:58px;padding:4px 12px;grid-template-columns:40px 1fr}.game-strip span{width:38px;height:38px;font-size:19px}.game-strip strong{font-size:13px}.game-strip small,.game-strip em{font-size:10px}.home-cards{max-width:1168px;padding:10px 12px 12px}.info-panel{min-height:180px;padding:11px}.info-panel h2{font-size:14px;margin-bottom:8px}.info-panel p{font-size:10.5px;line-height:1.6}.panel-media{height:70px}.panel-media.dealer{height:78px}.service-list{gap:6px;margin-bottom:8px}.service-list b{width:22px;height:22px}.service-list span{font-size:10.5px}.service-list small{font-size:10px}.mini-post{grid-template-columns:34px 1fr;padding:3px 0}.mini-thumb{width:31px;height:31px;font-size:17px}.mini-post strong{font-size:10.5px}.mini-post small{font-size:9.5px}.contact-panel p{grid-template-columns:52px 1fr;margin:6px 0;font-size:10px}.outline-link,.gold-link{min-height:27px;font-size:10.5px}footer{min-height:60px;padding-top:10px;padding-bottom:10px}.footer-brand .crest{width:32px;height:32px}.footer-brand strong{font-size:12px}.footer-brand p,footer nav,.footer-note{font-size:10px}.age-mark{width:32px;height:32px}}
@media(min-width:901px) and (max-width:1180px){.game-strip,.home-cards{max-width:calc(100% - 48px)}.home-cards{grid-template-columns:1.05fr .95fr .95fr .95fr 1fr}.casino-hero{padding-left:60px;padding-right:40px}.top-inner{padding-left:36px;padding-right:26px}.brand{min-width:180px}.top nav{gap:16px}.contact-chip.mail{max-width:138px;overflow:hidden;text-overflow:ellipsis}.contact-chip.telegram{max-width:146px;overflow:hidden;text-overflow:ellipsis}}
"""
    css += """
@media(min-width:901px){.casino-hero{height:304px;min-height:304px;padding-top:18px;padding-bottom:18px}.hero-kicker{font-size:11px}.hero-copy h1 span{font-size:clamp(38px,4.6vw,52px)}.hero-copy h1 strong{font-size:clamp(29px,3.45vw,39px)}.hero-text{max-width:475px;margin:8px 0 12px;font-size:11px;line-height:1.48}.hero-buttons{margin-bottom:9px}.hero-btn{height:29px;padding:0 14px}.trust-row{gap:8px;margin-bottom:6px}.trust-row span{min-height:31px;padding-left:34px;font-size:10.5px}.trust-row span:before{width:25px;height:25px}.trust-row small{font-size:9.5px}.responsible-bar{min-height:25px;padding:3px 9px;font-size:10.5px}.hero-showpiece{height:226px}.royal-crest{width:198px;height:198px}.royal-crest strong{font-size:58px}.royal-crest:after{font-size:15px;bottom:21px}.crown{top:-43px;font-size:52px}.card-a{left:70px;top:62px}.card-b{left:108px;top:58px}.chip-stack{left:74px;bottom:24px;transform:scale(.68);transform-origin:left bottom}.roulette-wheel{right:66px;top:70px;width:94px;height:94px}.gold-spade{right:34px;bottom:18px;width:54px;height:54px;font-size:36px}.game-strip{padding-top:6px;padding-bottom:6px}.game-strip a{min-height:52px}.home-cards{padding-top:8px}.info-panel{min-height:168px}.panel-media{height:64px}.panel-media.dealer{height:70px}footer{min-height:56px}}
@media(min-width:901px) and (max-width:1180px){.casino-hero{height:304px;min-height:304px}.contact-chip.mail{max-width:126px}.contact-chip.telegram{max-width:144px}}
"""
    css += """
@media(min-width:901px){.casino-hero{height:292px;min-height:292px}.hero-text{margin-bottom:10px}.hero-buttons{margin-bottom:8px}.trust-row{margin-bottom:5px}.game-strip{padding-top:5px;padding-bottom:5px}.game-strip a{min-height:48px}.game-strip span{width:35px;height:35px;font-size:17px}.game-strip strong{font-size:12px}.game-strip small,.game-strip em{font-size:9.5px}.home-cards{padding-top:8px;padding-bottom:8px}.info-panel{height:176px;min-height:176px;overflow:hidden}.panel-media{height:58px}.panel-media.dealer{height:62px}.info-panel p{margin:6px 0}.service-list{gap:4px}.service-list b{width:20px;height:20px}.mini-post{padding:2px 0}.outline-link,.gold-link{min-height:25px}footer{min-height:54px}}
@media(min-width:901px) and (max-width:1180px){.home-cards{grid-template-columns:1.08fr .96fr .96fr .96fr 1fr}.contact-panel{grid-column:auto!important}.casino-hero{height:292px;min-height:292px}.game-strip,.home-cards{max-width:calc(100% - 48px)}}
"""
    css += """
/* Wide readable desktop pass: make the public site use the screen instead of a tiny centered strip. */
@media(min-width:901px){
body{font-size:16px;background:#05080d}.top{box-shadow:0 12px 36px rgba(8,12,20,.1)}.top-inner{width:min(100% - 64px,1600px);max-width:none;height:82px;padding:0;gap:34px}.brand{min-width:260px}.crest{width:56px;height:56px;font-size:18px}.brand strong{font-size:28px}.brand small{font-size:12px}.top nav{gap:28px}.top nav a{display:inline-flex;align-items:center;min-height:58px;padding:0 4px;font-size:16px;line-height:1;font-weight:950}.top nav a:after{bottom:8px;height:3px}.header-actions{gap:12px}.contact-chip{min-height:40px;padding:0 16px;font-size:13px;border-radius:10px}.contact-chip:before{width:20px;height:20px}
.casino-hero{height:auto;min-height:540px;grid-template-columns:minmax(560px,1fr) minmax(520px,.92fr);gap:60px;padding:clamp(54px,4.3vw,82px) clamp(56px,6.5vw,132px)}.hero-kicker{font-size:15px;margin-bottom:12px}.hero-copy h1{margin-bottom:18px}.hero-copy h1 span{font-size:clamp(70px,5.7vw,102px)}.hero-copy h1 strong{font-size:clamp(48px,4.1vw,76px)}.hero-text{max-width:760px;margin:18px 0 26px;font-size:18px;line-height:1.72}.hero-buttons{gap:16px;margin-bottom:22px}.hero-btn{height:48px;padding:0 26px;border-radius:10px;font-size:15px}.trust-row{max-width:760px;gap:18px;margin-bottom:14px}.trust-row span{min-height:52px;padding:7px 8px 7px 54px;font-size:14px}.trust-row span:before{width:40px;height:40px}.trust-row span:after{left:11px;top:11px;font-size:16px}.trust-row small{font-size:12px}.responsible-bar{max-width:760px;min-height:42px;padding:8px 14px;font-size:14px}.responsible-bar b{width:30px;height:30px;font-size:12px}
.hero-showpiece{height:400px}.royal-crest{width:330px;height:330px}.royal-crest strong{font-size:98px}.royal-crest:after{bottom:34px;font-size:22px;padding:5px 30px}.crown{top:-70px;font-size:86px}.hero-showpiece .card{width:78px;height:112px;font-size:28px}.card-a{left:58px;top:110px}.card-b{left:122px;top:102px}.chip-stack{left:64px;bottom:58px;transform:scale(1.05);transform-origin:left bottom}.roulette-wheel{right:80px;top:128px;width:148px;height:148px}.gold-spade{right:32px;bottom:44px;width:92px;height:92px;font-size:62px}
.game-strip{max-width:min(100% - 64px,1600px);padding:14px 18px}.game-strip a{min-height:82px;padding:10px 20px;grid-template-columns:58px 1fr}.game-strip span{width:54px;height:54px;font-size:25px}.game-strip strong{font-size:17px}.game-strip small,.game-strip em{font-size:13px}
.home-cards{max-width:min(100% - 64px,1600px);padding:22px 18px 30px;gap:18px}.info-panel{height:auto;min-height:270px;padding:22px;border-radius:14px;overflow:visible}.info-panel h2{font-size:20px;margin-bottom:14px}.info-panel h2:after{width:34px;height:3px}.info-panel p{font-size:15px;line-height:1.78;margin:10px 0}.panel-media{height:126px;border-radius:10px}.panel-media.dealer{height:138px}.service-list{gap:13px}.service-list li{grid-template-columns:36px 1fr;gap:13px}.service-list b{width:34px;height:34px;font-size:15px}.service-list span{font-size:15px}.service-list small{font-size:13px}.mini-post{grid-template-columns:52px 1fr;gap:12px;padding:8px 0}.mini-thumb{width:46px;height:46px;font-size:24px}.mini-post strong{font-size:14px}.mini-post small{font-size:12px}.contact-panel p{grid-template-columns:82px 1fr;gap:12px;font-size:14px;margin:12px 0}.outline-link,.gold-link{min-height:40px;padding:0 22px;font-size:14px}.text-link{font-size:14px}
footer{grid-template-columns:1fr auto 1.2fr auto;min-height:88px;padding:18px max(56px,calc((100vw - 1600px)/2 + 56px))}.footer-brand .crest{width:44px;height:44px;font-size:15px}.footer-brand strong{font-size:16px}.footer-brand p,footer nav,.footer-note{font-size:13px}.age-mark{width:44px;height:44px}
}
@media(min-width:901px) and (max-width:1280px){.top-inner{width:min(100% - 40px,1180px);gap:20px}.top nav{gap:16px}.top nav a{font-size:14px}.contact-chip{font-size:12px;padding:0 12px}.casino-hero{grid-template-columns:1fr .8fr;gap:34px;padding:42px 44px}.hero-copy h1 span{font-size:58px}.hero-copy h1 strong{font-size:44px}.hero-text{font-size:16px}.hero-showpiece{height:310px}.royal-crest{width:250px;height:250px}.royal-crest strong{font-size:76px}.game-strip,.home-cards{max-width:calc(100% - 40px)}.home-cards{grid-template-columns:repeat(3,1fr)}.contact-panel{grid-column:span 2}}
"""
    css += """
.brand-logo,.footer-logo{display:block;object-fit:contain;flex:0 0 auto}.brand-logo{width:58px;height:64px;filter:drop-shadow(0 8px 18px rgba(120,60,20,.18))}.footer-logo{width:42px;height:46px;filter:drop-shadow(0 6px 12px rgba(0,0,0,.18))}
@media(min-width:901px){.brand-logo{width:74px;height:74px}.footer-logo{width:52px;height:56px}.brand{gap:14px}}
@media(max-width:900px){.brand-logo{width:54px;height:54px}.footer-logo{width:42px;height:44px}.brand{gap:10px}}
"""
    css += """
.panel-media.dealer{display:block;position:relative;overflow:hidden;background:#0d1118;border:1px solid #d7a548;box-shadow:inset 0 0 0 1px rgba(255,255,255,.08)}.panel-media.dealer img{display:block;width:100%;height:100%;object-fit:cover;object-position:center 28%}.panel-media.dealer:before{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,0) 46%,rgba(0,0,0,.55));z-index:1}.panel-media.dealer:after{content:"LIVE DEALER";position:absolute;left:12px;bottom:10px;z-index:2;padding:4px 9px;border-radius:999px;background:rgba(10,14,21,.78);border:1px solid rgba(245,196,83,.55);color:#f8cf69;font-size:11px;font-weight:950;letter-spacing:.12em}.panel-media.dealer span{display:none}
.article-card{padding:0}.article-card:before{display:none}.article-card-media{display:block;position:relative;aspect-ratio:16/9;overflow:hidden;background:#0d1118}.article-card-media picture,.article-card-media img{display:block;width:100%;height:100%}.article-card-media img{object-fit:cover;object-position:center 28%;transition:transform .28s ease}.article-card:hover .article-card-media img{transform:scale(1.04)}.article-card-body{display:flex;flex:1;flex-direction:column;padding:18px 22px 22px}.article-card-body p{margin-bottom:16px}.article-cover{margin:24px 0 28px}.article-cover picture{display:block;overflow:hidden;border-radius:24px;border:1px solid rgba(202,145,36,.28);box-shadow:0 20px 58px rgba(12,18,28,.16);background:#0d1118}.article-cover img{display:block;width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;object-position:center 28%}.article-cover figcaption{margin-top:10px;color:#7a8390;font-size:13px;text-align:center}
@media(min-width:901px){.article-card-body{padding:20px 24px 24px}.article-cover{margin-top:30px}.article-cover picture{border-radius:30px}.panel-media.dealer:after{font-size:12px}}
@media(max-width:900px){.article-card-body{padding:16px 18px 20px}.article-cover picture{border-radius:18px}.article-cover figcaption{text-align:left}}
.pagination{display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:10px;margin:34px auto 0}.page-link{display:inline-flex;align-items:center;justify-content:center;min-width:42px;min-height:42px;padding:9px 14px;border:1px solid rgba(172,125,37,.28);border-radius:14px;background:#fff;color:#17202c;font-weight:950;box-shadow:0 12px 28px rgba(15,24,38,.06)}.page-link:hover{color:#9b6307;border-color:#d99818}.page-link.current{background:linear-gradient(135deg,#ffd36b,#e78b0d);color:#1f1606;border-color:transparent}.page-prev,.page-next{padding-inline:18px}@media(max-width:760px){.pagination{justify-content:flex-start}.page-link{min-width:38px;min-height:38px;padding:8px 12px}}
"""
    css += """
/* Real hero artwork replaces the earlier CSS-drawn casino emblem. */
.hero-copy{z-index:2}.hero-showpiece{position:relative;display:block;height:320px;overflow:hidden;isolation:isolate;background:#090906}
.hero-showpiece:after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,#050a11 0,transparent 22%);pointer-events:none}
.hero-showpiece img{display:block;width:100%;height:100%}
.hero-showpiece img{object-fit:cover;object-position:70% center;filter:saturate(.96) contrast(1.04);transform:scale(1.02)}
@media(min-width:901px){.hero-showpiece{position:absolute;inset:0 0 0 48%;height:auto}}
@media(min-width:901px) and (max-width:1280px){.hero-showpiece{inset:0 0 0 50%;height:auto}}
@media(max-width:900px){.hero-showpiece{position:relative;inset:auto;height:300px;margin-top:8px;border-radius:18px}.hero-showpiece:after{background:linear-gradient(90deg,#050a11 0,transparent 14%)}.hero-showpiece img{object-position:67% center}}
@media(max-width:560px){.hero-showpiece{height:238px}.hero-showpiece img{object-position:66% center}}
"""
    css += """
/* External game entry shared by the homepage and every article. */
.contact-chip.game{border-color:#d9a53b;background:linear-gradient(135deg,#ffe18a,#d78b11);color:#2a1902}.contact-chip.game:before{content:"▶";background:#9d1517;color:#fff;font-size:9px}.game-play-cta{position:relative;overflow:hidden;margin:30px 0;padding:28px;border:1px solid rgba(194,132,18,.34);border-radius:24px;background:radial-gradient(circle at 92% 12%,rgba(245,184,63,.26),transparent 13rem),linear-gradient(135deg,#0b111b,#171107);color:#fff;box-shadow:0 22px 58px rgba(13,18,26,.18)}.game-play-cta:after{content:"♠";position:absolute;right:24px;bottom:-36px;color:rgba(245,184,63,.14);font:900 150px/1 Georgia,serif;pointer-events:none}.game-play-cta h2{position:relative;z-index:1;margin:4px 0 8px;color:#fff}.game-play-cta p{position:relative;z-index:1;max-width:720px;margin:0 0 18px;color:#dbe3ed}.game-play-kicker{color:#f8cf69!important;font-size:13px;font-weight:950;letter-spacing:.12em}.game-play-button{position:relative;z-index:1;display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:12px 24px;border-radius:12px;background:linear-gradient(135deg,#ffd66f,#d7860d);color:#241501!important;font-weight:950;box-shadow:0 14px 30px rgba(211,131,12,.27)}.game-play-cta small{position:relative;z-index:1;display:block;margin-top:12px;color:#aeb9c7}@media(max-width:760px){.game-play-cta{padding:22px 18px;border-radius:18px}.game-play-button{width:100%}}
"""
    js = """
const topButton=document.getElementById('top');const header=document.querySelector('.top');const menu=document.querySelector('.menu-toggle');window.addEventListener('scroll',()=>{if(!topButton)return;topButton.classList.toggle('show',window.scrollY>500)});topButton?.addEventListener('click',()=>window.scrollTo({top:0,behavior:'smooth'}));menu?.addEventListener('click',()=>{const open=header.classList.toggle('open');menu.setAttribute('aria-expanded',String(open))});
"""
    favicon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96"><rect width="96" height="96" rx="22" fill="#101621"/><circle cx="48" cy="48" r="33" fill="#d98b13"/><circle cx="48" cy="48" r="25" fill="#111827"/><text x="48" y="59" text-anchor="middle" font-family="Arial" font-size="30" font-weight="900" fill="#f3c351">TL</text></svg>"""
    og = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630"><defs><linearGradient id="g" x1="0" x2="1"><stop stop-color="#07111f"/><stop offset="1" stop-color="#075db3"/></linearGradient></defs><rect width="1200" height="630" fill="url(#g)"/><circle cx="865" cy="315" r="180" fill="#f3c351" opacity=".18"/><text x="86" y="220" font-family="Microsoft YaHei, Arial" font-size="74" font-weight="900" fill="#f3c351">{esc(settings['brand_name'])}</text><text x="86" y="305" font-family="Arial" font-size="58" font-weight="900" fill="#fff">{esc(settings['brand_subtitle'])}</text><text x="86" y="388" font-family="Microsoft YaHei, Arial" font-size="34" fill="#dfe8f4">中文资讯 · 每日文章 · 联系方式</text><text x="86" y="455" font-family="Arial" font-size="30" fill="#f3c351">Telegram {esc(settings['telegram'])} · Phone {esc(settings['phone'])}</text></svg>"""
    (ROOT / "assets" / "site.css").write_text(css.strip() + "\n", encoding="utf-8")
    (ROOT / "assets" / "site.js").write_text(js.strip() + "\n", encoding="utf-8")
    (ROOT / "assets" / "favicon.svg").write_text(favicon, encoding="utf-8")
    (ROOT / "assets" / "tl8899-og.svg").write_text(og, encoding="utf-8")


def write_home(posts: list[dict], settings: dict) -> None:
    pub = published_posts(posts)
    body = f"""
    <section class="casino-hero" id="hero">
      <div class="hero-copy">
        <p class="hero-kicker"><span>{esc(settings['brand_subtitle'])}</span> / {esc(settings['brand_name'])}</p>
        <h1><span>{esc(settings['brand_name'])}</span><strong>真人娱乐资讯指南</strong></h1>
        <p class="hero-text">专业提供百家乐、龙虎、牛牛、轮盘、骰宝、黑杰克等真人娱乐场资讯、规则与策略指南，助您轻松掌握游戏精髓。</p>
        <div class="hero-buttons"><a class="hero-btn primary" href="{GAME_PLAY_URL}" target="_blank" rel="noopener nofollow sponsored">立即进入游戏</a><a class="hero-btn dark" href="/blog/">浏览资讯指南</a></div>
        <div class="trust-row"><span>信息权威<small>专业团队撰写</small></span><span>更新及时<small>每日资讯更新</small></span><span>安全可靠<small>18+ 负责任娱乐</small></span></div>
        <div class="responsible-bar"><b>18+</b> 负责任娱乐：请在个人可承受的预算内游戏，切勿追逐损失。娱乐有度，理性投注。</div>
      </div>
      <picture class="hero-showpiece">
        <source srcset="{HERO_IMAGE_WEBP}" type="image/webp">
        <img src="{HERO_IMAGE_PNG}" alt="TL8899 LIVE 金色皇冠、扑克牌、筹码与轮盘主题视觉" width="1672" height="941" loading="eager" decoding="async" fetchpriority="high">
      </picture>
    </section>

    <section class="game-strip" aria-label="游戏指南">
      <a href="/blog/"><span>♠</span><strong>百家乐</strong><small>经典玩法 · 策略攻略</small><em>查看指南 →</em></a>
      <a href="/blog/"><span>龙</span><strong>龙虎</strong><small>龙虎对决 · 制胜天机</small><em>查看指南 →</em></a>
      <a href="/blog/"><span>牛</span><strong>牛牛</strong><small>斗牛比拼 · 运气与技巧</small><em>查看指南 →</em></a>
      <a href="/blog/"><span>◎</span><strong>轮盘</strong><small>欧洲轮盘 · 公平公正</small><em>查看指南 →</em></a>
      <a href="/blog/"><span>骰</span><strong>骰宝</strong><small>骰子游戏 · 简单易懂</small><em>查看指南 →</em></a>
      <a href="/blog/"><span>♠</span><strong>黑杰克</strong><small>21点挑战 · 智慧对决</small><em>查看指南 →</em></a>
    </section>

    <section class="home-cards">
      <article class="info-panel" id="about"><h2>关于我们</h2><div class="panel-media lounge"><span>TL</span></div><p>腾龙公司 {esc(settings['brand_subtitle'])} LIVE 致力于为全球用户提供高质量的真人娱乐资讯与专业游戏指南。我们的内容团队由资深玩家与行业专家组成，确保信息的权威性与实用性。</p><a class="outline-link" href="/#about">了解更多</a></article>
      <article class="info-panel" id="services"><h2>业务项目</h2><ul class="service-list"><li><b>♣</b><span>真人娱乐资讯指南<small>提供详细的游戏规则与策略</small></span></li><li><b>技</b><span>游戏技巧与策略<small>专业玩家分享实战经验</small></span></li><li><b>公</b><span>行业动态与公告<small>最新行业资讯与平台公告</small></span></li><li><b>搜</b><span>搜索优化与技术支持<small>快速、稳定、安全的静态站点</small></span></li></ul><a class="text-link" href="/blog/">查看全部项目 →</a></article>
      <article class="info-panel live-panel" id="hall"><h2>现场大厅</h2><picture class="panel-media dealer"><source srcset="{DEALER_IMAGE_WEBP}" type="image/webp"><img src="{DEALER_IMAGE_JPG}" alt="TL8899 LIVE 真人荷官与现场百家乐桌台" width="1280" height="720" loading="lazy" decoding="async"><span>LIVE</span></picture><p>进入 TL8899 LIVE 现场大厅，体验真实的荷官互动与沉浸式游戏氛围，支持多种热门游戏。</p><a class="gold-link" href="{GAME_PLAY_URL}" target="_blank" rel="noopener nofollow sponsored">立即进入游戏</a></article>
      <article class="info-panel latest-panel"><h2>最新文章</h2>{latest_home_list(pub, 4)}<a class="text-link" href="/blog/">查看全部文章 →</a></article>
      <article class="info-panel contact-panel"><h2>联系方式</h2><p><b>Telegram</b><span>{esc(settings['telegram'])}</span></p><p><b>电话</b><span>{esc(settings['phone'])}</span></p><p><b>邮箱</b><span>{esc(settings['email'])}</span></p><p><b>工作时间</b><span>09:00 - 18:00（GMT+8）</span></p><a class="outline-link wide" href="/contact/">发送消息</a></article>
    </section>
    """
    structured = {"@context": "https://schema.org", "@type": "WebSite", "name": settings["brand_subtitle"], "url": SITE}
    (ROOT / "index.html").write_text(layout(settings, settings["site_title"], settings["site_description"], "/", body, structured=structured), encoding="utf-8")


def write_blog_index(posts: list[dict], settings: dict) -> None:
    pub = published_posts(posts)
    total = blog_page_count(pub)
    for page in range(1, total + 1):
        start = (page - 1) * BLOG_PAGE_SIZE
        page_posts = pub[start:start + BLOG_PAGE_SIZE]
        page_label = "" if page == 1 else f" · 第 {page} 页"
        body = f"""<section class="section white"><div class="head"><p class="eyebrow">文章</p><h1>真人娱乐中文文章{page_label}</h1><p>每日更新百家乐、龙虎、牛牛、轮盘、骰宝、21点、赔率、常见错误和负责任娱乐内容。文章不承诺盈利，不提供保证结果的下注方法。</p></div><div class="articles">{article_cards(page_posts)}</div>{pagination_nav(page, total)}</section>"""
        title = "文章 | TL8899 真人娱乐中文资讯" if page == 1 else f"文章第 {page} 页 | TL8899 真人娱乐中文资讯"
        desc = "TL8899 中文文章列表，覆盖百家乐、龙虎、牛牛、轮盘、骰宝、21点、赔率说明和负责任娱乐。"
        out_path = blog_page_path(page)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(layout(settings, title, desc, blog_page_url(page), body), encoding="utf-8")
    page_root = ROOT / "blog" / "page"
    if page_root.exists():
        for child in page_root.iterdir():
            if child.is_dir() and child.name.isdigit() and int(child.name) > total:
                shutil.rmtree(child)


def write_contact(settings: dict) -> None:
    body = f"""<section class="section white"><div class="head"><p class="eyebrow">联系我们</p><h1>联系方式</h1><p>内容更新、搜索修正或业务联系，请使用电报、电话或邮箱。请不要发送账号密码、付款资料或身份证件。</p></div><div class="contact-box"><a class="contact-pill" href="{esc(settings['telegram_url'])}">电报 {esc(settings['telegram'])}</a><a class="contact-pill gold" href="tel:{esc(settings['phone'])}">电话 {esc(settings['phone'])}</a><a class="contact-pill" href="mailto:{esc(settings['email'])}">{esc(settings['email'])}</a></div><div class="note" style="margin-top:24px">本站内容仅供成年人信息参考。请提前设定预算和时间，若影响睡眠、工作、健康或家庭，应立即停止。</div></section>"""
    (ROOT / "contact" / "index.html").write_text(layout(settings, "联系我们 | TL8899", f"通过电报 {settings['telegram']}、电话 {settings['phone']} 或邮箱 {settings['email']} 联系 TL8899。", "/contact/", body, extra_keywords=["联系", settings["email"], settings["telegram"], settings["phone"]]), encoding="utf-8")


def write_privacy_policy(settings: dict) -> None:
    body = f"""
    <article class="article">
      <p class="meta-line">TL8899 LIVE · Privacy Policy · 隐私政策</p>
      <h1>隐私政策 Privacy Policy</h1>
      <p>最后更新：{esc(shanghai_today().isoformat())}</p>
      <div class="note">本站为成年人资讯与指南站点，不提供任何形式的赌博服务，也不承诺盈利结果。</div>

      <h2>我们收集的信息</h2>
      <p>当您浏览 https://tl8899.live/ 时，服务器可能会记录基本技术信息，例如访问时间、页面路径、浏览器类型和安全日志。这些信息用于维护网站安全、排查错误和改进页面体验。</p>
      <p>如果您通过电报或邮箱联系我们，我们会收到您主动提供的联系信息和消息内容。请不要发送账号密码、付款资料、身份证件或其他不必要的敏感资料。</p>

      <h2>Google OAuth 与 Blogger API</h2>
      <p>本项目可能使用 Google OAuth 连接 Blogger API，用于在已授权的 Blogger 博客中创建或管理文章。授权时，本应用只请求执行 Blogger 发布任务所需的权限。</p>
      <p>Google OAuth token 仅用于您授权的 Blogger 自动发布流程，不会出售、出租或用于广告画像。若您取消授权，自动发布功能将无法继续访问对应的 Google/Blogger 资源。</p>

      <h2>信息使用方式</h2>
      <ul>
        <li>维护网站与自动发布工具的正常运行。</li>
        <li>回复用户主动发送的联系请求。</li>
        <li>保护网站、服务器和自动化任务的安全。</li>
        <li>改进成人资讯内容、导航和搜索可见性。</li>
      </ul>

      <h2>第三方服务与链接</h2>
      <p>网站可能链接到 Telegram、Google Blogger、Google OAuth 或其他外部页面。第三方网站有自己的隐私政策和服务条款，本站无法控制其数据处理方式。</p>

      <h2>数据保留与安全</h2>
      <p>我们只在完成上述用途所需的时间内保留相关信息，并采取合理措施保护本地凭据、服务器配置和自动化 token。互联网传输无法保证绝对安全，请避免发送不必要的敏感资料。</p>

      <h2>联系我们</h2>
      <p>如需询问隐私相关问题，请通过 <a href="{esc(settings['telegram_url'])}">Telegram {esc(settings['telegram'])}</a>、电话 <a href="tel:{esc(settings['phone'])}">{esc(settings['phone'])}</a> 或 <a href="mailto:{esc(settings['email'])}">{esc(settings['email'])}</a> 联系。</p>

      <h2>English Summary</h2>
      <p>TL8899 LIVE is an adult informational website. We use basic technical logs to operate and secure the site. If Google OAuth is used, access is limited to the authorized Blogger publishing workflow and is not sold or used for advertising profiling. Contact us by Telegram {esc(settings['telegram'])}, phone {esc(settings['phone'])}, or email {esc(settings['email'])} for privacy questions.</p>
    </article>
    """
    structured = {
        "@context": "https://schema.org",
        "@type": "PrivacyPolicy",
        "name": "TL8899 LIVE Privacy Policy",
        "url": f"{SITE}/privacy-policy/",
        "dateModified": shanghai_today().isoformat(),
        "publisher": {"@type": "Organization", "name": settings["brand_subtitle"]},
    }
    (ROOT / "privacy-policy" / "index.html").write_text(
        layout(
            settings,
            "隐私政策 | TL8899 LIVE",
            "TL8899 LIVE 隐私政策，说明网站日志、联系信息、Google OAuth 与 Blogger API 自动发布数据的使用方式。",
            "/privacy-policy/",
            body,
            extra_keywords=["隐私政策", "Privacy Policy", "Google OAuth", "Blogger API"],
            structured=structured,
        ),
        encoding="utf-8",
    )


def write_terms_of_service(settings: dict) -> None:
    body = f"""
    <article class="article">
      <p class="meta-line">TL8899 LIVE · Terms of Service · 服务条款</p>
      <h1>服务条款 Terms of Service</h1>
      <p>最后更新：{esc(shanghai_today().isoformat())}</p>
      <div class="note">使用本站即表示您理解：本站只提供成年人信息参考，不提供赌博服务，不处理投注，不保证任何收益。</div>

      <h2>网站用途</h2>
      <p>https://tl8899.live/ 是一个中文资讯与指南网站，内容包括真人娱乐规则、风险提示、文章更新、联系方式和负责任娱乐说明。本站内容不构成法律、财务、投资或赌博建议。</p>

      <h2>成年人使用</h2>
      <p>本站内容仅面向达到当地法定年龄的成年人。未成年人、所在地区不允许相关内容的用户，或无法理性控制预算和时间的用户，不应使用本站内容作为参与依据。</p>

      <h2>负责任娱乐</h2>
      <ul>
        <li>请提前设定预算和时间限制。</li>
        <li>不要借钱、追亏或相信保证盈利的方法。</li>
        <li>如果娱乐影响睡眠、工作、健康或家庭，应立即停止并寻求帮助。</li>
        <li>所有桌台规则、赔率、活动和限制以对应平台实际说明为准。</li>
      </ul>

      <h2>Google OAuth 与自动发布</h2>
      <p>如您授权本项目使用 Google OAuth，本项目只会将相关权限用于 Blogger 文章发布或管理流程。您可以随时在 Google 账号安全设置中撤销授权。</p>

      <h2>知识产权与链接</h2>
      <p>本站页面、排版和原创文字用于 TL8899 LIVE 资讯展示。外部品牌、平台名称或第三方链接仅用于说明和导航，不表示本站与其存在官方合作或背书关系。</p>

      <h2>免责声明</h2>
      <p>本站尽力保持内容清晰、及时和准确，但不保证所有信息适用于每个地区、平台或桌台。使用者应自行确认当地规定、平台条款和个人风险承受能力。</p>

      <h2>联系我们</h2>
      <p>如需联系，请使用 <a href="{esc(settings['telegram_url'])}">Telegram {esc(settings['telegram'])}</a>、电话 <a href="tel:{esc(settings['phone'])}">{esc(settings['phone'])}</a> 或 <a href="mailto:{esc(settings['email'])}">{esc(settings['email'])}</a>。</p>

      <h2>English Summary</h2>
      <p>TL8899 LIVE provides adult informational content only. We do not operate gambling services, process bets, promise winnings, or provide legal or financial advice. Google OAuth access, when granted, is used only for the authorized Blogger publishing workflow.</p>
    </article>
    """
    structured = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": "TL8899 LIVE Terms of Service",
        "url": f"{SITE}/terms-of-service/",
        "dateModified": shanghai_today().isoformat(),
        "publisher": {"@type": "Organization", "name": settings["brand_subtitle"]},
    }
    (ROOT / "terms-of-service" / "index.html").write_text(
        layout(
            settings,
            "服务条款 | TL8899 LIVE",
            "TL8899 LIVE 服务条款，说明成年人信息参考、负责任娱乐、Google OAuth 自动发布和免责声明。",
            "/terms-of-service/",
            body,
            extra_keywords=["服务条款", "Terms of Service", "Google OAuth", "Blogger API"],
            structured=structured,
        ),
        encoding="utf-8",
    )


def write_article(post: dict, settings: dict) -> None:
    rows = "\n".join(f"<tr><td>{esc(name)}</td><td>{esc(note)}</td></tr>" for name, note in (post.get("rows") or []))
    tags = "".join(f"<span>{esc(tag)}</span>" for tag in visible_article_keywords(post))
    body = f"""
    <article class="article">
      <p class="meta-line">{esc(post['date'])} · {esc(post.get('topic','真人娱乐'))} · {esc(settings['brand_name'])}</p>
      <h1>{esc(post['title'])}</h1>
      <p>{esc(post['desc'])}</p>
      <figure class="article-cover">
        <picture><source srcset="{DEALER_IMAGE_WEBP}" type="image/webp"><img src="{DEALER_IMAGE_JPG}" alt="{esc(post['title'])} 真人荷官桌台配图" width="1280" height="720" loading="eager" decoding="async"></picture>
        <figcaption>TL8899 LIVE 真人荷官资讯配图，仅用于成年人游戏规则与风险提示内容。</figcaption>
      </figure>
      <div class="note">负责任娱乐提示：本文仅供成年人信息参考，不承诺盈利，不提供保证结果的下注方法，也不建议追亏或冲动加注。</div>
      <h2>玩法重点</h2>
      <p>{esc(post.get('intro','进入任何真人桌台前，请先阅读规则面板、赔率表、桌台限额和活动条款。'))}</p>
      <section class="game-play-cta" data-game-play-link="tl616">
        <p class="game-play-kicker">18+ 外部游戏入口</p>
        <h2>准备好后进入游戏</h2>
        <p>请先确认游戏规则、桌台限额和个人预算。外部平台内容与服务由其运营方负责；任何玩法都不能保证盈利。</p>
        <a class="game-play-button" href="{GAME_PLAY_URL}" target="_blank" rel="noopener nofollow sponsored">立即进入游戏</a>
        <small>外部链接：tl616.cc · 娱乐有度，切勿追逐损失。</small>
      </section>
      <div class="table"><table><thead><tr><th>项目</th><th>说明</th></tr></thead><tbody>{rows}</tbody></table></div>
      <h2>新手提醒</h2>
      <ul><li>先看规则，再看赔率，不要只被高赔率吸引。</li><li>提前设定预算和时间，达到上限就停止。</li><li>不要把短期连赢或连输理解成可预测规律。</li><li>如果娱乐开始变成压力，应暂停并寻求帮助。</li></ul>
      <h2>搜索标签</h2>
      <p>以下中文标签用于搜索发现：腾龙娱乐官网、皇家在线公司、百家乐、龙虎、牛牛、轮盘、骰宝、二十一点。本站不声明与其他品牌存在官方关系。</p>
      <div class="tag-list">{tags}</div>
      <h2>联系方式</h2>
      <div class="note">Telegram <a href="{esc(settings['telegram_url'])}" rel="noopener" target="_blank">{esc(settings['telegram'])}</a> · 电话 <a href="tel:{esc(settings['phone'])}">{esc(settings['phone'])}</a></div>
      <h2>相关页面</h2>
      <p>延伸阅读：也可以查看 <a href="https://myanmarcasino.cloud/" rel="noopener">https://myanmarcasino.cloud/</a>，用于补充百家乐、龙虎、牛牛等中文规则资料。</p>
      <p><a href="/blog/">返回文章列表</a> · <a href="/contact/">查看联系方式</a> · <a href="/">返回首页</a></p>
    </article>
    """
    article_schema = {"@context": "https://schema.org", "@type": "Article", "headline": post["title"], "description": post["desc"], "image": f"{SITE}/assets/casino-dealer-live.jpg", "datePublished": post["date"], "dateModified": post["date"], "author": {"@type": "Organization", "name": settings["brand_subtitle"]}, "publisher": {"@type": "Organization", "name": settings["brand_subtitle"]}, "mainEntityOfPage": f"{SITE}/blog/{post['slug']}/", "keywords": post.get("keywords") or settings_keywords(settings)}
    path = ROOT / "blog" / post["slug"]
    path.mkdir(parents=True, exist_ok=True)
    (path / "index.html").write_text(layout(settings, post["title"], post["desc"], f"/blog/{post['slug']}/", body, page_type="article", extra_keywords=post.get("keywords") or [], structured=article_schema), encoding="utf-8")


def cleanup_post_dirs(posts: list[dict]) -> None:
    valid = {post["slug"] for post in published_posts(posts)}
    blog = ROOT / "blog"
    for child in blog.iterdir():
        if child.is_dir() and child.name.startswith("tl8899-") and child.name not in valid:
            shutil.rmtree(child)


def write_discovery(posts: list[dict], settings: dict) -> None:
    pub = published_posts(posts)
    today = shanghai_today().isoformat()
    page_urls = [(blog_page_url(page), "daily", "0.7") for page in range(2, blog_page_count(pub) + 1)]
    urls = [
        ("/", "daily", "1.0"),
        ("/blog/", "daily", "0.9"),
        *page_urls,
        ("/contact/", "monthly", "0.7"),
        ("/privacy-policy/", "monthly", "0.6"),
        ("/terms-of-service/", "monthly", "0.6"),
    ] + [(f"/blog/{post['slug']}/", "weekly", "0.8") for post in pub]
    sitemap_items = "\n".join(f"  <url>\n    <loc>{SITE}{path}</loc>\n    <lastmod>{today if path in ['/', '/blog/'] else today}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{priority}</priority>\n  </url>" for path, freq, priority in urls)
    (ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sitemap_items}\n</urlset>\n', encoding="utf-8")
    rss_items = "\n".join(f"    <item>\n      <title>{esc(post['title'])}</title>\n      <link>{SITE}/blog/{esc(post['slug'])}/</link>\n      <guid>{SITE}/blog/{esc(post['slug'])}/</guid>\n      <pubDate>{email.utils.format_datetime(datetime.fromisoformat(post['date']).replace(tzinfo=timezone.utc))}</pubDate>\n      <description>{esc(post['desc'])}</description>\n    </item>" for post in pub[:20])
    (ROOT / "rss.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>{esc(settings["brand_subtitle"])} 中文文章</title><link>{SITE}/blog/</link><description>TL8899 真人娱乐中文文章。</description>\n{rss_items}\n  </channel></rss>\n', encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    (ROOT / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY + "\n", encoding="utf-8")


def rebuild(posts: list[dict] | None = None, settings: dict | None = None) -> tuple[list[dict], dict]:
    ensure_dirs()
    settings = settings or load_settings()
    posts = posts or read_posts()
    write_posts(posts)
    write_assets(settings)
    write_home(posts, settings)
    write_blog_index(posts, settings)
    write_contact(settings)
    write_privacy_policy(settings)
    write_terms_of_service(settings)
    cleanup_post_dirs(posts)
    for post in published_posts(posts):
        write_article(post, settings)
    write_discovery(posts, settings)
    return posts, settings


def verify_public(slug: str | None = None) -> None:
    paths = ["/", "/blog/", "/privacy-policy/", "/terms-of-service/", "/sitemap.xml", "/rss.xml"]
    if slug:
        paths.insert(1, f"/blog/{slug}/")
    for path in paths:
        with urllib.request.urlopen(f"{SITE}{path}", timeout=20) as response:
            if response.status != 200:
                raise RuntimeError(f"验证失败 {path}: {response.status}")


def git_commit(message: str) -> bool:
    subprocess.run(["git", "-C", str(ROOT), "config", "user.name", "TL8899 Automation"], check=False)
    subprocess.run(["git", "-C", str(ROOT), "config", "user.email", "automation@tl8899.live"], check=False)
    status = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"], capture_output=True, text=True, check=False)
    if not status.stdout.strip():
        return False
    subprocess.run(["git", "-C", str(ROOT), "add", "."], check=False)
    result = subprocess.run(["git", "-C", str(ROOT), "commit", "-m", message], check=False)
    return result.returncode == 0


def git_push(remote: str = "github", branch: str = "main") -> bool:
    key = Path.home() / ".ssh" / "tl8899_github_deploy_ed25519"
    env = os.environ.copy()
    if key.exists():
        env["GIT_SSH_COMMAND"] = f"ssh -i {key} -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"
    result = subprocess.run(["git", "-C", str(ROOT), "push", remote, branch], env=env, check=False)
    return result.returncode == 0


def dns_points_here() -> bool:
    try:
        return socket.gethostbyname(DOMAIN) == SERVER_IP
    except OSError:
        return False


def submit_indexnow(urls: list[str]) -> int | None:
    if not dns_points_here():
        return None
    payload = json.dumps({"host": DOMAIN, "key": INDEXNOW_KEY, "keyLocation": INDEXNOW_KEY_LOCATION, "urlList": urls}, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request("https://api.indexnow.org/indexnow", data=payload, headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status
    except urllib.error.HTTPError as error:
        return error.code


if __name__ == "__main__":
    rebuild()
