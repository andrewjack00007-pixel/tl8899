#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import email.utils
import html
import json
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


ROOT = Path("/var/www/tl8899")
SITE = "https://tl8899.live"
DOMAIN = "tl8899.live"
SERVER_IP = "76.13.216.172"
INDEXNOW_KEY = "f64254d0a708461e8b1f2fce8eee9c30"
INDEXNOW_KEY_LOCATION = f"{SITE}/{INDEXNOW_KEY}.txt"
ASSET_VERSION = "2026062306"

DEFAULT_SETTINGS = {
    "brand_name": "腾龙公司",
    "brand_subtitle": "TL8899 LIVE",
    "site_title": "TL8899 LIVE | 腾龙公司真人娱乐资讯",
    "site_description": "TL8899 LIVE 腾龙公司中文资讯站，展示百家乐、龙虎、牛牛、轮盘、骰宝、21点、联系方式、SEO文章和负责任娱乐提示。",
    "hero_title": "腾龙公司\n真人娱乐资讯指南",
    "hero_description": "参考中文企业官网的清晰结构：品牌介绍、业务项目、现场大厅、新闻文章、联系信息和后台管理。所有公开内容以中文为主，并每天自动更新 SEO 文章。",
    "telegram": "@jhondoe112233",
    "telegram_url": "https://t.me/jhondoe112233",
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
            ("联系渠道", "Telegram 与邮箱应清楚展示，方便内容和业务联系。"),
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
        return datetime.now(ZoneInfo("Asia/Shanghai")).date()
    return datetime.now(timezone(timedelta(hours=8))).date()


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def slugify(value: str, fallback: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or fallback


def ensure_dirs() -> None:
    for path in [ROOT, ROOT / "assets", ROOT / "blog", ROOT / "contact", ROOT / "data", ROOT / "scripts"]:
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
    return {
        "date": date_str,
        "slot": slot,
        "slug": slug or f"tl8899-{topic['slug_base']}-{compact}{slug_suffix}",
        "topic": topic["topic"],
        "title": topic["title"] if slot == 1 else f"{topic['title']}（第{slot}篇）",
        "desc": topic["desc"],
        "teaser": topic["teaser"],
        "intro": topic["intro"],
        "rows": topic["rows"],
        "keywords": BASE_KEYWORDS + [topic["topic"], topic["title"], "https://myanmarcasino.cloud/"],
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
            post["keywords"] = list(dict.fromkeys((post.get("keywords") or []) + BASE_KEYWORDS + [post.get("topic", ""), "https://myanmarcasino.cloud/"]))
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
      <a class="brand" href="/" aria-label="{esc(settings['brand_name'])}首页">
        <span class="crest">TL</span>
        <span><strong>{esc(settings['brand_name'])}</strong><small>{esc(settings['brand_subtitle'])}</small></span>
      </a>
      <button class="menu-toggle" type="button" aria-label="打开导航" aria-expanded="false">菜单</button>
      <nav>
        <a href="/">首页</a>
        <a href="/#about">关于我们</a>
        <a href="/#services">业务项目</a>
        <a href="/#hall">现场大厅</a>
        <a href="/blog/">文章</a>
        <a href="/contact/">联系我们</a>
      </nav>
      <div class="quick">电报 <a href="{esc(settings['telegram_url'])}">{esc(settings['telegram'])}</a></div>
    </header>
    """


def footer(settings: dict) -> str:
    return f"""
    <footer>
      <div>
        <strong>{esc(settings['brand_subtitle'])}</strong>
        <p>{esc(settings['footer_note'])}</p>
      </div>
      <nav>
        <a href="/blog/">文章</a>
        <a href="/contact/">联系</a>
        <a href="/sitemap.xml">站点地图</a>
      </nav>
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
        "sameAs": [settings["telegram_url"]],
        "contactPoint": {"@type": "ContactPoint", "contactType": "内容与业务联系", "email": settings["email"], "url": settings["telegram_url"]},
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
  <meta property="og:image" content="{SITE}/assets/tl8899-og.svg">
  <meta name="twitter:card" content="summary_large_image">
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
          <time datetime="{esc(post['date'])}">{esc(post['date'])}</time>
          <h3><a href="/blog/{esc(post['slug'])}/">{esc(post['title'])}</a></h3>
          <p>{esc(post['teaser'])}</p>
          <span class="read-more">阅读文章 →</span>
    </article>"""
        for post in visible
    )


def write_assets(settings: dict) -> None:
    css = """
:root{--blue:#075db3;--blue-2:#0a76d1;--gold:#f3b42e;--gold-2:#d98b13;--dark:#101621;--ink:#20242c;--muted:#687383;--line:#e6ebf2;--panel:#fff;--bg:#f6f8fb}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;font-family:Inter,"Microsoft YaHei","PingFang SC",Arial,sans-serif;color:var(--ink);background:var(--bg);line-height:1.72}a{color:inherit;text-decoration:none}.skip{position:absolute;left:-999px;top:8px;z-index:100;padding:10px 14px;background:#fff}.skip:focus{left:8px}.top{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:28px;padding:16px clamp(22px,5vw,82px);background:rgba(255,255,255,.96);border-bottom:1px solid var(--line);box-shadow:0 10px 30px rgba(20,30,45,.07);backdrop-filter:blur(12px)}.brand{display:flex;align-items:center;gap:12px;min-width:260px}.crest{display:grid;place-items:center;width:58px;height:58px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#ffe58c,#b51512 48%,#201109 49%,#f6d675 56%,#bb7a14);color:#fff;font-weight:950;letter-spacing:-.05em;box-shadow:0 10px 24px rgba(138,15,8,.22)}.brand strong{display:block;color:#c28a12;font-size:26px;line-height:1}.brand small{display:block;color:#765612;font-weight:800;text-transform:uppercase;letter-spacing:.08em}.top nav{display:flex;align-items:center;gap:24px;margin-left:auto}.top nav a{font-weight:850}.top nav a:hover,.admin-link{color:var(--blue)}.quick{color:var(--blue);font-weight:850;white-space:nowrap}.menu-toggle{display:none}.hero{min-height:650px;display:grid;align-items:center;padding:72px clamp(22px,6vw,96px);position:relative;overflow:hidden;background:linear-gradient(90deg,rgba(0,0,0,.74),rgba(0,0,0,.34)),radial-gradient(circle at 78% 45%,rgba(243,195,81,.42),transparent 27rem),linear-gradient(135deg,#1b2738,#02060b 65%)}.hero:before{content:"";position:absolute;inset:0;background:repeating-linear-gradient(90deg,rgba(255,255,255,.07) 0 2px,transparent 2px 82px),radial-gradient(circle at 75% 70%,rgba(11,111,171,.28),transparent 24rem);opacity:.78}.hero:after{content:"♠ ♥ ♦ ♣";position:absolute;right:clamp(22px,8vw,130px);bottom:54px;font-size:clamp(40px,9vw,132px);color:rgba(243,195,81,.2);letter-spacing:.18em}.hero-inner{position:relative;max-width:890px;color:#fff}.eyebrow{color:var(--gold);font-weight:950;letter-spacing:.14em;text-transform:uppercase}.hero h1{font-size:clamp(42px,7vw,88px);line-height:1.02;margin:12px 0;white-space:pre-line}.hero p{font-size:20px;max-width:740px;color:#e8edf4}.actions{display:flex;flex-wrap:wrap;gap:14px;margin-top:28px}.btn{display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:12px 22px;border-radius:999px;border:1px solid rgba(255,255,255,.35);font-weight:950;cursor:pointer}.btn.primary{background:linear-gradient(135deg,var(--gold),var(--gold-2));border:0;color:#1b1203}.btn.dark{border-color:var(--line);color:var(--ink);background:#fff}.danger{background:#fff1f1!important;color:#a01818!important;border-color:#ffcaca!important}.contact-strip{display:flex;flex-wrap:wrap;gap:12px;margin-top:24px;padding:16px;border:1px solid rgba(243,195,81,.45);border-radius:18px;background:rgba(0,0,0,.28);font-weight:900}.contact-strip a{color:var(--gold)}.section{padding:76px clamp(22px,6vw,96px)}.section.white{background:#fff}.head{max-width:900px;margin-bottom:32px}.head h1,.head h2{font-size:clamp(32px,4vw,54px);line-height:1.1;margin:0}.head p{color:var(--muted);font-size:18px}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}.card{padding:28px;border-radius:24px;background:#fff;border:1px solid var(--line);box-shadow:0 18px 50px rgba(20,30,45,.08)}.card.dark{background:linear-gradient(160deg,#111b28,#0b1018);color:#fff;border:0}.card .icon{font-size:42px;color:var(--gold);font-weight:950}.card h3{font-size:24px;margin:14px 0 8px}.card p{color:var(--muted);margin:0}.card.dark p{color:#c7d1df}.hall{display:grid;grid-template-columns:1.05fr .95fr;gap:28px;align-items:center}.hall-art{min-height:370px;border-radius:30px;background:linear-gradient(180deg,rgba(0,0,0,.1),rgba(0,0,0,.62)),repeating-conic-gradient(from 18deg,#123f31 0 12deg,#7e1111 12deg 24deg,#111827 24deg 36deg);box-shadow:inset 0 0 0 18px rgba(243,195,81,.18),0 24px 70px rgba(0,0,0,.18)}.articles{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}.article-card{display:flex;flex-direction:column;min-height:235px;padding:22px;border:1px solid var(--line);border-radius:22px;background:#fff;transition:transform .2s ease,box-shadow .2s ease}.article-card:hover{transform:translateY(-3px);box-shadow:0 18px 50px rgba(20,30,45,.1)}.article-card time{font-weight:900;color:var(--blue)}.article-card h3{margin:8px 0;font-size:21px}.article-card p{color:var(--muted)}.read-more{margin-top:auto;color:var(--blue);font-weight:900}.contact-box{display:grid;grid-template-columns:1fr 1fr;gap:20px}.contact-pill{display:block;padding:18px 20px;border-radius:18px;background:#10233b;color:#fff;font-size:22px;font-weight:950}.contact-pill.gold{background:#2b2514;color:var(--gold)}.article{max-width:980px;margin:0 auto;padding:70px 22px}.article h1{font-size:clamp(34px,5vw,58px);line-height:1.1}.article h2{font-size:30px;margin-top:38px}.article p,.article li{color:#4d5562}.meta-line{color:var(--blue);font-weight:900}.table{overflow:auto;border:1px solid var(--line);border-radius:18px;margin:22px 0}.table table{width:100%;border-collapse:collapse;min-width:680px;background:#fff}.table th,.table td{padding:14px;border-bottom:1px solid var(--line);text-align:left}.table th{background:#f1f5fb;color:var(--blue)}.note{padding:16px;border-radius:18px;background:#fff8df;border:1px solid #f1cf67;color:#4e3905}.tag-list{display:flex;gap:10px;flex-wrap:wrap}.tag-list span{padding:8px 12px;border-radius:999px;background:#edf4ff;color:#075db3;font-weight:800}.admin-wrap{padding:36px clamp(18px,4vw,60px) 70px;background:#f6f8fb}.admin-hero{display:flex;justify-content:space-between;gap:20px;align-items:flex-start;margin-bottom:24px}.admin-hero h1{font-size:42px;margin:0}.admin-tabs{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0}.admin-tabs a{padding:10px 14px;border-radius:999px;background:#fff;border:1px solid var(--line);font-weight:900}.admin-layout{display:grid;grid-template-columns:1.2fr .8fr;gap:22px;align-items:start}.admin-panel{background:#fff;border:1px solid var(--line);border-radius:24px;padding:24px;box-shadow:0 18px 45px rgba(20,30,45,.07);margin-bottom:22px}.admin-panel h2{margin:0 0 14px;font-size:24px}.admin-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:22px}.stat{padding:18px;border-radius:20px;background:#fff;border:1px solid var(--line)}.stat strong{display:block;font-size:28px;color:var(--blue)}label{display:block;font-weight:900;margin:12px 0 6px}input,textarea,select{width:100%;padding:12px 14px;border:1px solid #dbe3ef;border-radius:14px;font:inherit;background:#fff}textarea{min-height:110px;resize:vertical}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}.post-row{display:grid;grid-template-columns:110px 1fr auto;gap:12px;align-items:center;padding:12px 0;border-bottom:1px solid var(--line)}.post-row:last-child{border-bottom:0}.row-actions{display:flex;gap:8px;flex-wrap:wrap}.small{font-size:13px;color:var(--muted)}.flash{padding:14px 16px;border-radius:16px;background:#eaf7ef;color:#11602f;border:1px solid #bae7c8;margin-bottom:18px;font-weight:850}.error{background:#fff0f0;color:#9c1b1b;border-color:#ffcaca}footer{display:flex;justify-content:space-between;gap:20px;padding:34px clamp(22px,6vw,96px);background:#101621;color:#cfd7e3}footer strong{color:#fff}footer nav{display:flex;gap:18px;flex-wrap:wrap}#top{position:fixed;right:18px;bottom:18px;width:46px;height:46px;border:0;border-radius:50%;background:var(--gold);font-weight:950;opacity:0;pointer-events:none;transition:opacity .2s ease}#top.show{opacity:1;pointer-events:auto}@media(max-width:1100px){.admin-layout,.admin-stats{grid-template-columns:1fr}.post-row{grid-template-columns:1fr}.articles,.grid,.hall,.contact-box,.form-grid{grid-template-columns:1fr}}@media(max-width:980px){.top{align-items:flex-start;flex-direction:column}.top nav{margin-left:0;flex-wrap:wrap;display:none}.top.open nav{display:flex}.menu-toggle{display:inline-flex;border:1px solid var(--line);border-radius:999px;background:#fff;padding:9px 14px;font-weight:900}.quick{white-space:normal}.hero{min-height:auto}.brand{min-width:0}}
"""
    js = """
const topButton=document.getElementById('top');const header=document.querySelector('.top');const menu=document.querySelector('.menu-toggle');window.addEventListener('scroll',()=>{if(!topButton)return;topButton.classList.toggle('show',window.scrollY>500)});topButton?.addEventListener('click',()=>window.scrollTo({top:0,behavior:'smooth'}));menu?.addEventListener('click',()=>{const open=header.classList.toggle('open');menu.setAttribute('aria-expanded',String(open))});
"""
    favicon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96"><rect width="96" height="96" rx="22" fill="#101621"/><circle cx="48" cy="48" r="33" fill="#d98b13"/><circle cx="48" cy="48" r="25" fill="#111827"/><text x="48" y="59" text-anchor="middle" font-family="Arial" font-size="30" font-weight="900" fill="#f3c351">TL</text></svg>"""
    og = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630"><defs><linearGradient id="g" x1="0" x2="1"><stop stop-color="#07111f"/><stop offset="1" stop-color="#075db3"/></linearGradient></defs><rect width="1200" height="630" fill="url(#g)"/><circle cx="865" cy="315" r="180" fill="#f3c351" opacity=".18"/><text x="86" y="220" font-family="Microsoft YaHei, Arial" font-size="74" font-weight="900" fill="#f3c351">{esc(settings['brand_name'])}</text><text x="86" y="305" font-family="Arial" font-size="58" font-weight="900" fill="#fff">{esc(settings['brand_subtitle'])}</text><text x="86" y="388" font-family="Microsoft YaHei, Arial" font-size="34" fill="#dfe8f4">中文资讯 · 每日文章 · 联系方式</text><text x="86" y="455" font-family="Arial" font-size="30" fill="#f3c351">Telegram {esc(settings['telegram'])}</text></svg>"""
    (ROOT / "assets" / "site.css").write_text(css.strip() + "\n", encoding="utf-8")
    (ROOT / "assets" / "site.js").write_text(js.strip() + "\n", encoding="utf-8")
    (ROOT / "assets" / "favicon.svg").write_text(favicon, encoding="utf-8")
    (ROOT / "assets" / "tl8899-og.svg").write_text(og, encoding="utf-8")


def write_home(posts: list[dict], settings: dict) -> None:
    pub = published_posts(posts)
    body = f"""
    <section class="hero"><div class="hero-inner">
      <p class="eyebrow">{esc(settings['brand_subtitle'])} / {esc(settings['brand_name'])}</p>
      <h1>{esc(settings['hero_title'])}</h1>
      <p>{esc(settings['hero_description'])}</p>
      <div class="actions"><a class="btn primary" href="/contact/">立即联系</a><a class="btn" href="/blog/">阅读文章</a></div>
      <div class="contact-strip"><strong>联系方式：</strong><a href="{esc(settings['telegram_url'])}">电报 {esc(settings['telegram'])}</a><span>|</span><a href="mailto:{esc(settings['email'])}">{esc(settings['email'])}</a></div>
    </div></section>
    <section id="about" class="section white"><div class="head"><p class="eyebrow">关于我们</p><h2>关于 {esc(settings['brand_subtitle'])}</h2><p>面向中文用户的真人娱乐资讯站，覆盖百家乐、龙虎、牛牛、骰宝、轮盘、21点、规则说明、联系方式和负责任娱乐提示。</p></div>
      <div class="hall"><div class="hall-art" aria-label="现场大厅风格图形"></div><div class="grid"><div class="card"><div class="icon">龙</div><h3>龙虎</h3><p>快速牌面大小比较，重点理解和局风险。</p></div><div class="card"><div class="icon">百</div><h3>百家乐</h3><p>庄、闲、和、佣金与免佣变体的基础说明。</p></div><div class="card"><div class="icon">牛</div><h3>牛牛</h3><p>五张牌组合、牛数与倍率表的规则提醒。</p></div></div></div>
    </section>
    <section id="services" class="section"><div class="head"><p class="eyebrow">业务项目</p><h2>网站功能</h2></div><div class="grid"><div class="card dark"><div class="icon">01</div><h3>每日中文文章</h3><p>自动生成并发布真人娱乐中文 SEO 文章，更新站点地图和 RSS。</p></div><div class="card dark"><div class="icon">02</div><h3>联系方式展示</h3><p>电报、邮箱和结构化资料帮助搜索引擎识别联系渠道。</p></div><div class="card dark"><div class="icon">03</div><h3>后台管理</h3><p>可添加、编辑、删除文章，修改联系信息和管理后台角色。</p></div></div></section>
    <section class="section white" id="hall"><div class="head"><p class="eyebrow">新闻资讯</p><h2>最新文章</h2><p>所有文章以中文阅读体验为主；SEO 标签用于搜索发现，不代表与其他品牌存在官方关系。</p></div><div class="articles">{article_cards(pub, 6)}</div></section>
    """
    structured = {"@context": "https://schema.org", "@type": "WebSite", "name": settings["brand_subtitle"], "url": SITE}
    (ROOT / "index.html").write_text(layout(settings, settings["site_title"], settings["site_description"], "/", body, structured=structured), encoding="utf-8")


def write_blog_index(posts: list[dict], settings: dict) -> None:
    pub = published_posts(posts)
    body = f"""<section class="section white"><div class="head"><p class="eyebrow">文章</p><h1>真人娱乐中文文章</h1><p>每日更新百家乐、龙虎、牛牛、轮盘、骰宝、21点、赔率、常见错误和负责任娱乐内容。文章不承诺盈利，不提供保证结果的下注方法。</p></div><div class="articles">{article_cards(pub)}</div></section>"""
    (ROOT / "blog" / "index.html").write_text(layout(settings, "文章 | TL8899 真人娱乐中文资讯", "TL8899 中文文章列表，覆盖百家乐、龙虎、牛牛、轮盘、骰宝、21点、赔率说明和负责任娱乐。", "/blog/", body), encoding="utf-8")


def write_contact(settings: dict) -> None:
    body = f"""<section class="section white"><div class="head"><p class="eyebrow">联系我们</p><h1>联系方式</h1><p>内容更新、SEO 修正或业务联系，请使用电报或邮箱。请不要发送账号密码、付款资料或身份证件。</p></div><div class="contact-box"><a class="contact-pill" href="{esc(settings['telegram_url'])}">电报 {esc(settings['telegram'])}</a><a class="contact-pill gold" href="mailto:{esc(settings['email'])}">{esc(settings['email'])}</a></div><div class="note" style="margin-top:24px">本站内容仅供成年人信息参考。请提前设定预算和时间，若影响睡眠、工作、健康或家庭，应立即停止。</div></section>"""
    (ROOT / "contact" / "index.html").write_text(layout(settings, "联系我们 | TL8899", f"通过电报 {settings['telegram']} 或邮箱 {settings['email']} 联系 TL8899。", "/contact/", body, extra_keywords=["联系", settings["email"], settings["telegram"]]), encoding="utf-8")


def write_article(post: dict, settings: dict) -> None:
    rows = "\n".join(f"<tr><td>{esc(name)}</td><td>{esc(note)}</td></tr>" for name, note in (post.get("rows") or []))
    tags = "".join(f"<span>{esc(tag)}</span>" for tag in list(dict.fromkeys((post.get("keywords") or [])[:18])))
    body = f"""
    <article class="article">
      <p class="meta-line">{esc(post['date'])} · {esc(post.get('topic','真人娱乐'))} · {esc(settings['brand_subtitle'])}</p>
      <h1>{esc(post['title'])}</h1>
      <p>{esc(post['desc'])}</p>
      <div class="note">负责任娱乐提示：本文仅供成年人信息参考，不承诺盈利，不提供保证结果的下注方法，也不建议追亏或冲动加注。</div>
      <h2>玩法重点</h2>
      <p>{esc(post.get('intro','进入任何真人桌台前，请先阅读规则面板、赔率表、桌台限额和活动条款。'))}</p>
      <div class="table"><table><thead><tr><th>项目</th><th>说明</th></tr></thead><tbody>{rows}</tbody></table></div>
      <h2>新手提醒</h2>
      <ul><li>先看规则，再看赔率，不要只被高赔率吸引。</li><li>提前设定预算和时间，达到上限就停止。</li><li>不要把短期连赢或连输理解成可预测规律。</li><li>如果娱乐开始变成压力，应暂停并寻求帮助。</li></ul>
      <h2>SEO 标签</h2>
      <p>以下标签用于搜索发现：tamron casino、腾龙娱乐官网、皇家在线公司、百家乐、龙虎、牛牛。本站不声明与其他品牌存在官方关系。</p>
      <div class="tag-list">{tags}</div>
      <h2>相关页面</h2>
      <p>延伸阅读：也可以查看 <a href="https://myanmarcasino.cloud/" rel="noopener">https://myanmarcasino.cloud/</a>，用于补充百家乐、龙虎、牛牛等中文规则资料。</p>
      <p><a href="/blog/">返回文章列表</a> · <a href="/contact/">查看联系方式</a> · <a href="/">返回首页</a></p>
    </article>
    """
    article_schema = {"@context": "https://schema.org", "@type": "Article", "headline": post["title"], "description": post["desc"], "datePublished": post["date"], "dateModified": post["date"], "author": {"@type": "Organization", "name": settings["brand_subtitle"]}, "publisher": {"@type": "Organization", "name": settings["brand_subtitle"]}, "mainEntityOfPage": f"{SITE}/blog/{post['slug']}/", "keywords": post.get("keywords") or settings_keywords(settings)}
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
    urls = [("/", "daily", "1.0"), ("/blog/", "daily", "0.9"), ("/contact/", "monthly", "0.7")] + [(f"/blog/{post['slug']}/", "weekly", "0.8") for post in pub]
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
    cleanup_post_dirs(posts)
    for post in published_posts(posts):
        write_article(post, settings)
    write_discovery(posts, settings)
    return posts, settings


def verify_public(slug: str | None = None) -> None:
    paths = ["/", "/blog/", "/sitemap.xml", "/rss.xml"]
    if slug:
        paths.insert(1, f"/blog/{slug}/")
    for path in paths:
        with urllib.request.urlopen(f"{SITE}{path}", timeout=20) as response:
            if response.status != 200:
                raise RuntimeError(f"验证失败 {path}: {response.status}")


def git_commit(message: str) -> None:
    subprocess.run(["git", "-C", str(ROOT), "config", "user.name", "TL8899 Automation"], check=False)
    subprocess.run(["git", "-C", str(ROOT), "config", "user.email", "automation@tl8899.live"], check=False)
    status = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"], capture_output=True, text=True, check=False)
    if not status.stdout.strip():
        return
    subprocess.run(["git", "-C", str(ROOT), "add", "."], check=False)
    subprocess.run(["git", "-C", str(ROOT), "commit", "-m", message], check=False)


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
