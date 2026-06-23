#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import html
import json
import os
import secrets
import subprocess
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from site_engine import DEFAULT_SETTINGS, ROOT, SITE, git_commit, keyword_meta, load_settings, make_auto_post, published_posts, read_posts, rebuild, save_settings, settings_keywords, slugify, submit_indexnow


HOST = "127.0.0.1"
PORT = 8899
USERS_PATH = ROOT / "data" / "admin_users.json"
CSRF_PATH = ROOT / "data" / "admin_csrf.txt"
HTPASSWD = Path("/etc/nginx/.htpasswd-tl8899")


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def read_users() -> list[dict]:
    if USERS_PATH.exists():
        try:
            users = json.loads(USERS_PATH.read_text(encoding="utf-8"))
        except Exception:
            users = []
    else:
        users = []
    if not any(user.get("username") == "admin" for user in users):
        users.insert(0, {"username": "admin", "role": "站长", "note": "默认管理员", "active": True})
    save_users(users)
    return users


def save_users(users: list[dict]) -> None:
    USERS_PATH.write_text(json.dumps(users, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def current_role(username: str) -> str:
    for user in read_users():
        if user.get("username") == username:
            return user.get("role") or "只读"
    return "只读"


def csrf_token() -> str:
    if CSRF_PATH.exists():
        token = CSRF_PATH.read_text(encoding="utf-8").strip()
        if token:
            return token
    token = secrets.token_urlsafe(32)
    CSRF_PATH.write_text(token + "\n", encoding="utf-8")
    return token


def parse_rows(raw: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if "|" in line:
            name, note = line.split("|", 1)
        elif "：" in line:
            name, note = line.split("：", 1)
        else:
            name, note = line, ""
        rows.append((name.strip(), note.strip()))
    return rows or [("规则", "请在这里填写规则说明。")]


def rows_text(post: dict) -> str:
    return "\n".join(f"{name} | {note}" for name, note in (post.get("rows") or []))


def write_htpasswd(username: str, password: str | None = None, delete: bool = False) -> None:
    lines = []
    if HTPASSWD.exists():
        lines = [line.strip() for line in HTPASSWD.read_text(encoding="utf-8").splitlines() if line.strip()]
    kept = [line for line in lines if not line.startswith(username + ":")]
    if delete:
        HTPASSWD.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")
        return
    if password:
        hashed = subprocess.check_output(["openssl", "passwd", "-apr1", password], text=True).strip()
        kept.append(f"{username}:{hashed}")
        HTPASSWD.write_text("\n".join(kept) + "\n", encoding="utf-8")


def can_content(role: str) -> bool:
    return role in {"站长", "编辑", "SEO"}


def can_settings(role: str) -> bool:
    return role in {"站长", "SEO"}


def can_users(role: str) -> bool:
    return role == "站长"


def admin_page(title: str, body: str, user: str, role: str, flash: str = "", error: str = "") -> bytes:
    settings = load_settings()
    flash_html = f'<div class="flash">{esc(flash)}</div>' if flash else ""
    error_html = f'<div class="flash error">{esc(error)}</div>' if error else ""
    token = csrf_token()
    html_doc = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)}</title><meta name="robots" content="noindex,nofollow"><link rel="stylesheet" href="/assets/site.css?v=2026062306"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"></head><body>
    <header class="top"><a class="brand" href="/"><span class="crest">TL</span><span><strong>{esc(settings['brand_name'])}</strong><small>{esc(settings['brand_subtitle'])}</small></span></a><nav><a href="/">首页</a><a href="/blog/">文章</a><a href="/contact/">联系</a><a href="/admin/">后台</a></nav><div class="quick">当前用户：{esc(user)} · {esc(role)}</div></header>
    <main class="admin-wrap"><div class="admin-hero"><div><p class="eyebrow">后台管理</p><h1>{esc(title)}</h1><p>这里可以添加文章、编辑文章、修改网站联系信息、管理后台用户角色。保存后会自动重建公开页面，访客可以看到更新内容。</p></div><div class="actions"><a class="btn dark" href="/">查看首页</a><a class="btn dark" href="/blog/">查看文章</a></div></div>
    <div class="admin-tabs"><a href="/admin/">总览</a><a href="/admin/post">新增文章</a><a href="/admin/#settings">网站设置</a><a href="/admin/#users">用户角色</a><a href="/admin/status.json">状态JSON</a></div>
    {flash_html}{error_html}
    <script>window.CSRF={json.dumps(token)};</script>
    {body}</main></body></html>"""
    return html_doc.encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = "TL8899Admin/1.0"

    def log_message(self, fmt: str, *args) -> None:
        print("%s - %s" % (self.address_string(), fmt % args))

    @property
    def user(self) -> str:
        return self.headers.get("X-Remote-User") or "admin"

    @property
    def role(self) -> str:
        return current_role(self.user)

    def send_html(self, data: bytes, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def redirect(self, location: str) -> None:
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()

    def form(self) -> dict[str, str]:
        size = int(self.headers.get("Content-Length") or "0")
        raw = self.rfile.read(size).decode("utf-8", "replace")
        parsed = parse_qs(raw, keep_blank_values=True)
        data = {key: values[-1] for key, values in parsed.items()}
        if data.get("csrf") != csrf_token():
            raise PermissionError("表单安全令牌无效，请刷新后台页面后再提交。")
        return data

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/admin/status.json":
            self.status_json()
            return
        if path == "/admin/post":
            self.edit_post()
            return
        self.dashboard()

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            if path == "/admin/post/save":
                self.save_post()
            elif path == "/admin/post/delete":
                self.delete_post()
            elif path == "/admin/settings/save":
                self.save_settings_action()
            elif path == "/admin/user/save":
                self.save_user()
            elif path == "/admin/user/delete":
                self.delete_user()
            else:
                self.send_error(404)
        except PermissionError as error:
            self.send_html(admin_page("权限不足", "<div class='admin-panel'><h2>无法保存</h2><p>%s</p></div>" % esc(error), self.user, self.role), 403)
        except Exception as error:
            self.send_html(admin_page("保存失败", "<div class='admin-panel'><h2>发生错误</h2><p>%s</p></div>" % esc(error), self.user, self.role), 500)

    def status_json(self) -> None:
        posts = read_posts()
        settings = load_settings()
        data = {"site": SITE, "post_count": len(posts), "published_count": len(published_posts(posts)), "latest": posts[0] if posts else None, "settings": {"brand_name": settings["brand_name"], "telegram": settings["telegram"], "email": settings["email"]}, "generated_at": int(time.time())}
        encoded = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def dashboard(self, flash: str = "") -> None:
        posts = read_posts()
        settings = load_settings()
        users = read_users()
        token = csrf_token()
        post_rows = "".join(f"""<div class="post-row"><div><strong>{esc(post['date'])}</strong><br><span class="small">{esc(post.get('topic',''))}</span></div><div><a href="/blog/{esc(post['slug'])}/" target="_blank"><strong>{esc(post['title'])}</strong></a><br><span class="small">/{esc(post['slug'])}/ · {esc(post.get('status','published'))}</span></div><div class="row-actions"><a class="btn dark" href="/admin/post?slug={esc(post['slug'])}">编辑</a><form method="post" action="/admin/post/delete" onsubmit="return confirm('确定删除这篇文章吗？')"><input type="hidden" name="csrf" value="{token}"><input type="hidden" name="slug" value="{esc(post['slug'])}"><button class="btn danger" type="submit">删除</button></form></div></div>""" for post in posts)
        user_rows = "".join(f"""<div class="post-row"><div><strong>{esc(user.get('username'))}</strong><br><span class="small">{'启用' if user.get('active', True) else '停用'}</span></div><div>{esc(user.get('role','只读'))}<br><span class="small">{esc(user.get('note',''))}</span></div><div class="row-actions"><form method="post" action="/admin/user/delete" onsubmit="return confirm('确定删除这个后台用户吗？')"><input type="hidden" name="csrf" value="{token}"><input type="hidden" name="username" value="{esc(user.get('username'))}"><button class="btn danger" type="submit">删除</button></form></div></div>""" for user in users)
        settings_form = "".join(f"""<label>{esc(label)}</label><textarea name="{esc(key)}">{esc(settings.get(key,''))}</textarea>""" if key in {"hero_description", "footer_note", "seo_keywords"} else f"""<label>{esc(label)}</label><input name="{esc(key)}" value="{esc(settings.get(key,''))}">""" for key, label in [
            ("brand_name", "品牌中文名"),
            ("brand_subtitle", "品牌副标题"),
            ("site_title", "首页标题"),
            ("site_description", "SEO描述"),
            ("hero_title", "首页大标题"),
            ("hero_description", "首页介绍"),
            ("telegram", "电报账号"),
            ("telegram_url", "电报链接"),
            ("email", "邮箱"),
            ("seo_keywords", "SEO关键词"),
            ("footer_note", "页脚说明"),
        ])
        body = f"""
        <div class="admin-stats"><div class="stat"><strong>{len(posts)}</strong><span>文章总数</span></div><div class="stat"><strong>{len(published_posts(posts))}</strong><span>公开文章</span></div><div class="stat"><strong>{esc(posts[0]['date'] if posts else '-')}</strong><span>最新文章日期</span></div><div class="stat"><strong>{len(users)}</strong><span>后台用户</span></div></div>
        <div class="admin-layout"><section class="admin-panel"><h2>文章管理</h2><div class="actions"><a class="btn primary" href="/admin/post">新增文章</a><a class="btn dark" href="/blog/" target="_blank">查看公开列表</a></div>{post_rows}</section>
        <aside><section class="admin-panel" id="settings"><h2>网站设置</h2><form method="post" action="/admin/settings/save"><input type="hidden" name="csrf" value="{token}">{settings_form}<button class="btn primary" type="submit">保存网站设置</button></form></section>
        <section class="admin-panel" id="users"><h2>用户与角色</h2>{user_rows}<form method="post" action="/admin/user/save"><input type="hidden" name="csrf" value="{token}"><label>用户名</label><input name="username" required><label>密码</label><input name="password" type="password" placeholder="新增用户必须填写；修改角色可留空"><label>角色</label><select name="role"><option>站长</option><option>编辑</option><option>SEO</option><option>只读</option></select><label>备注</label><input name="note" placeholder="例如：文章编辑"><button class="btn primary" type="submit">保存用户角色</button></form></section></aside></div>
        """
        self.send_html(admin_page("TL8899 中文后台", body, self.user, self.role, flash=flash))

    def edit_post(self) -> None:
        token = csrf_token()
        slug = parse_qs(urlparse(self.path).query).get("slug", [""])[0]
        posts = read_posts()
        post = next((item for item in posts if item.get("slug") == slug), None)
        if not post:
            today = time.strftime("%Y-%m-%d")
            post = make_auto_post(today, slug="")
            post.update({"title": "", "desc": "", "teaser": "", "intro": "", "rows": [("玩法", "请填写说明")], "topic": "真人娱乐", "keywords": settings_keywords(load_settings())})
        body = f"""
        <section class="admin-panel"><h2>{'编辑文章' if slug else '新增文章'}</h2><form method="post" action="/admin/post/save"><input type="hidden" name="csrf" value="{token}"><input type="hidden" name="old_slug" value="{esc(slug)}"><div class="form-grid"><div><label>发布日期</label><input name="date" value="{esc(post.get('date',''))}" required></div><div><label>分类</label><input name="topic" value="{esc(post.get('topic','真人娱乐'))}"></div></div><label>文章标题</label><input name="title" value="{esc(post.get('title',''))}" required><label>URL Slug</label><input name="slug" value="{esc(post.get('slug',''))}" placeholder="留空自动生成英文URL"><label>SEO描述</label><textarea name="desc">{esc(post.get('desc',''))}</textarea><label>列表摘要</label><textarea name="teaser">{esc(post.get('teaser',''))}</textarea><label>正文介绍</label><textarea name="intro" style="min-height:180px">{esc(post.get('intro',''))}</textarea><label>规则表格：每行格式为 项目 | 说明</label><textarea name="rows" style="min-height:180px">{esc(rows_text(post))}</textarea><label>SEO标签：用逗号分隔</label><textarea name="keywords">{esc(', '.join(post.get('keywords') or []))}</textarea><label>状态</label><select name="status"><option value="published" {'selected' if post.get('status','published')=='published' else ''}>公开</option><option value="draft" {'selected' if post.get('status')=='draft' else ''}>草稿</option></select><button class="btn primary" type="submit">保存并发布到网站</button><a class="btn dark" href="/admin/">返回后台</a></form></section>
        """
        self.send_html(admin_page("文章编辑", body, self.user, self.role))

    def save_post(self) -> None:
        if not can_content(self.role):
            raise PermissionError("当前角色不能编辑文章。")
        data = self.form()
        posts = read_posts()
        old_slug = data.get("old_slug", "").strip()
        title = data.get("title", "").strip()
        date_value = data.get("date", "").strip()
        fallback = f"tl8899-article-{date_value.replace('-', '') or int(time.time())}"
        new_slug = slugify(data.get("slug", "").strip() or title, fallback)
        post = {
            "date": date_value,
            "slug": new_slug,
            "topic": data.get("topic", "真人娱乐").strip() or "真人娱乐",
            "title": title,
            "desc": data.get("desc", "").strip() or title,
            "teaser": data.get("teaser", "").strip() or data.get("desc", "").strip() or title,
            "intro": data.get("intro", "").strip(),
            "rows": parse_rows(data.get("rows", "")),
            "keywords": [item.strip() for item in data.get("keywords", "").replace("\n", ",").split(",") if item.strip()] or settings_keywords(load_settings()),
            "status": data.get("status", "published"),
            "source": "admin",
        }
        posts = [item for item in posts if item.get("slug") not in {old_slug, new_slug}]
        posts.insert(0, post)
        posts.sort(key=lambda item: item.get("date", ""), reverse=True)
        rebuild(posts)
        git_commit(f"后台保存文章 {new_slug}")
        submit_indexnow([f"{SITE}/blog/{new_slug}/", f"{SITE}/blog/", f"{SITE}/sitemap.xml", f"{SITE}/rss.xml"])
        self.redirect("/admin/?saved=post")

    def delete_post(self) -> None:
        if not can_content(self.role):
            raise PermissionError("当前角色不能删除文章。")
        data = self.form()
        slug = data.get("slug", "")
        posts = [item for item in read_posts() if item.get("slug") != slug]
        rebuild(posts)
        git_commit(f"后台删除文章 {slug}")
        submit_indexnow([f"{SITE}/blog/", f"{SITE}/sitemap.xml", f"{SITE}/rss.xml"])
        self.redirect("/admin/?deleted=post")

    def save_settings_action(self) -> None:
        if not can_settings(self.role):
            raise PermissionError("当前角色不能修改网站设置。")
        data = self.form()
        settings = load_settings()
        for key in DEFAULT_SETTINGS:
            if key in data:
                settings[key] = data[key]
        save_settings(settings)
        rebuild(read_posts(), settings)
        git_commit("后台更新网站设置")
        submit_indexnow([f"{SITE}/", f"{SITE}/blog/", f"{SITE}/contact/", f"{SITE}/sitemap.xml", f"{SITE}/rss.xml"])
        self.redirect("/admin/?saved=settings")

    def save_user(self) -> None:
        if not can_users(self.role):
            raise PermissionError("当前角色不能管理用户。")
        data = self.form()
        username = data.get("username", "").strip()
        if not username:
            raise ValueError("用户名不能为空。")
        users = [user for user in read_users() if user.get("username") != username]
        users.append({"username": username, "role": data.get("role", "只读"), "note": data.get("note", ""), "active": True})
        save_users(users)
        if data.get("password", ""):
            write_htpasswd(username, data["password"])
        git_commit(f"后台更新用户角色 {username}")
        self.redirect("/admin/?saved=user")

    def delete_user(self) -> None:
        if not can_users(self.role):
            raise PermissionError("当前角色不能管理用户。")
        data = self.form()
        username = data.get("username", "").strip()
        if username == "admin":
            raise PermissionError("默认 admin 用户不能删除。")
        users = [user for user in read_users() if user.get("username") != username]
        save_users(users)
        write_htpasswd(username, delete=True)
        git_commit(f"后台删除用户 {username}")
        self.redirect("/admin/?deleted=user")


def main() -> int:
    read_users()
    rebuild(read_posts(), load_settings())
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"TL8899 admin CMS running at http://{HOST}:{PORT}/admin/")
    httpd.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
