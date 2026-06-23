#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse

from site_engine import SITE, git_commit, git_push, make_auto_post, read_posts, rebuild, shanghai_today, submit_indexnow, verify_public


DEFAULT_DAILY_COUNT = 2


def posts_for_date(posts: list[dict], date_str: str) -> list[dict]:
    return sorted([post for post in posts if post.get("date") == date_str], key=lambda item: (int(item.get("slot") or 1), item.get("slug", "")))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=shanghai_today().isoformat())
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--count", type=int, default=DEFAULT_DAILY_COUNT, help="Number of posts to publish; default is 2.")
    args = parser.parse_args()

    target_count = max(1, args.count)
    posts = read_posts()
    existing = posts_for_date(posts, args.date)

    if len(existing) >= target_count and not args.force:
        rebuild(posts)
        for post in existing[:target_count]:
            verify_public(post["slug"])
        print(f"{args.date} already has {len(existing)} posts; target is {target_count}.")
        return 0

    if args.force:
        posts = [item for item in posts if item.get("date") != args.date]
        existing = []

    existing_slots = {int(post.get("slot") or index + 1) for index, post in enumerate(existing)}
    new_posts: list[dict] = []
    for slot in range(1, target_count + 1):
        if slot in existing_slots:
            continue
        new_posts.append(make_auto_post(args.date, slot=slot))

    if args.dry_run:
        if not new_posts:
            print(f"{args.date} already satisfies the {target_count}-post target.")
        for post in new_posts:
            print(f"Would publish {post['slug']} - {post['title']}")
        return 0

    posts = new_posts + posts
    posts.sort(key=lambda item: (item.get("date", ""), int(item.get("slot") or 1)), reverse=True)
    rebuild(posts)
    for post in new_posts:
        verify_public(post["slug"])

    if new_posts:
        committed = git_commit(f"Publish TL8899 daily posts for {args.date} ({len(new_posts)} posts)")
        pushed = git_push() if committed else False
        urls = [f"{SITE}/blog/{post['slug']}/" for post in new_posts] + [f"{SITE}/", f"{SITE}/blog/", f"{SITE}/sitemap.xml", f"{SITE}/rss.xml"]
        code = submit_indexnow(urls)
        for post in new_posts:
            print(f"Published {SITE}/blog/{post['slug']}/")
        print(f"Git commit: {'created' if committed else 'skipped'}")
        print(f"GitHub push: {'ok' if pushed else 'skipped or failed'}")
        print(f"IndexNow: {code}")
    else:
        print(f"No new posts needed for {args.date}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
