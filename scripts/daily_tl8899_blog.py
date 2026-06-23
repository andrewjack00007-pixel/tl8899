#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse

from site_engine import SITE, git_commit, make_auto_post, read_posts, rebuild, shanghai_today, submit_indexnow, verify_public


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=shanghai_today().isoformat())
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    posts = read_posts()
    existing = next((post for post in posts if post.get("date") == args.date), None)
    if existing and not args.force:
        rebuild(posts)
        verify_public(existing["slug"])
        print(f"跳过：{args.date} 已有文章 {existing['slug']}")
        return 0

    post = make_auto_post(args.date)
    if args.dry_run:
        print(f"预览：将发布 {post['slug']} - {post['title']}")
        return 0

    posts = [item for item in posts if item.get("date") != args.date]
    posts.insert(0, post)
    posts.sort(key=lambda item: item.get("date", ""), reverse=True)
    rebuild(posts)
    verify_public(post["slug"])
    git_commit(f"发布 TL8899 中文文章 {args.date}")
    code = submit_indexnow([f"{SITE}/blog/{post['slug']}/", f"{SITE}/", f"{SITE}/blog/", f"{SITE}/sitemap.xml", f"{SITE}/rss.xml"])
    print(f"已发布：{SITE}/blog/{post['slug']}/")
    print(f"IndexNow: {code}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
