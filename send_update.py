#!/usr/bin/env python3
"""
RSS 文章更新邮件通知脚本。

功能：
1. 从 RSS 地址抓取最新文章
2. 检查是否已发送过（与 link.txt 比对）
3. 如未发送，生成 HTML 邮件并通过 SMTP 密送订阅者
4. 记录本次发送的文章链接

所有敏感配置均从环境变量读取，适用于 GitHub Actions Secrets。
"""

import os
import sys
import re
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

import feedparser

# ── 配置：全部来自环境变量 ──────────────────────────────────
def _env(key, fallback=None):
  """读取环境变量，必须存在则 fallback 为 None。"""
  val = os.environ.get(key, fallback)
  if val is None:
    print(f"错误: 缺少环境变量 {key}")
    sys.exit(1)
  return val


SMTP_SERVER   = _env("SMTP_SERVER")       # smtp.resend.com
SMTP_PORT   = int(_env("SMTP_PORT", "465"))   # 465
SMTP_USER   = _env("SMTP_USER")         # resend
SMTP_PASS   = _env("SMTP_PASS")         # API Key / 密码
SMTP_FROM_NAME = _env("SMTP_FROM_NAME")      # 他说
SMTP_FROM_ADDR = _env("SMTP_FROM_ADDR")      # subscribe@090909.top
SMTP_SUBJECT  = _env("SMTP_SUBJECT")      # 他说，你收到了新的订阅

RSS_URL     = _env("RSS_URL")         # https://090909.top/atom.xml
EMAIL_LIST  = _env("EMAIL_LIST")        # 空格分隔的密送邮箱列表

TAG_TITLE   = _env("TAG_TITLE", "h1")       # 标题标签名
TAG_SUMMARY   = _env("TAG_SUMMARY", "p")    # 摘要标签名
TAG_LINK    = _env("TAG_LINK", "a")         # 链接标签名
LINK_TEXT   = _env("LINK_TEXT", "阅读详情")  # 链接显示文字

UNSUBSCRIBE_EMAIL = _env("UNSUBSCRIBE_EMAIL", "")  # 退订邮箱（可选）

LINK_FILE   = "link.txt"                      # 缓存已发送链接的文件（每行一个）


# ── 工具函数 ────────────────────────────────────────────────

def load_sent_links():
  """读取所有已发送的文章链接（每行一个），返回集合。"""
  if not os.path.exists(LINK_FILE):
    return set()
  with open(LINK_FILE, "r", encoding="utf-8") as f:
    links = {line.strip() for line in f if line.strip()}
  return links


def save_sent_link(link):
  """将新发送的链接追加到缓存文件。"""
  with open(LINK_FILE, "a", encoding="utf-8") as f:
    f.write(link.strip() + "\n")
  print(f"已记录发送链接: {link}")


def strip_html_tags(text):
  """移除 HTML 标签，保留纯文本。用于生成纯文本版邮件。"""
  clean = re.sub(r"<[^>]+>", "", text)
  return clean.strip()


def build_html_content(title, summary, link):
  """
  根据模板生成 HTML 邮件正文。
  格式与 demo.html 一致：
    <TAG_TITLE>《标题》</TAG_TITLE>
    <TAG_SUMMARY>摘要</TAG_SUMMARY>
    <TAG_LINK href="链接">LINK_TEXT</TAG_LINK>
  """
  parts = [
    f'<{TAG_TITLE}>《{title}》</{TAG_TITLE}>',
    f'<{TAG_SUMMARY}>{summary}</{TAG_SUMMARY}>',
    f'<{TAG_LINK} href="{link}">{LINK_TEXT}</{TAG_LINK}>',
  ]
  if UNSUBSCRIBE_EMAIL:
    parts.append(
      f'<hr><p style="color:#888;font-size:12px;">'
      f'如不希望收到此类邮件，请联系退订：'
      f'<a href="mailto:{UNSUBSCRIBE_EMAIL}">{UNSUBSCRIBE_EMAIL}</a>'
      f'</p>'
    )
  return "\n".join(parts)


def build_plain_content(title, summary, link):
  """纯文本版邮件。"""
  clean_summary = strip_html_tags(summary)
  lines = [
    f"《{title}》",
    "",
    clean_summary,
    "",
    f"{LINK_TEXT}: {link}",
  ]
  if UNSUBSCRIBE_EMAIL:
    lines.extend([
      "",
      "---",
      f"如不希望收到此类邮件，请联系退订：{UNSUBSCRIBE_EMAIL}",
    ])
  return "\n".join(lines)


def send_email(html_body, plain_body, bcc_list):
  """
  通过 SMTP_SSL 发送邮件。
  收件人设为发件人自己，实际订阅者放在密送中。
  """
  msg = MIMEMultipart("alternative")
  msg["From"] = formataddr((SMTP_FROM_NAME, SMTP_FROM_ADDR))
  msg["To"] = formataddr((SMTP_FROM_NAME, SMTP_FROM_ADDR))
  msg["Subject"] = SMTP_SUBJECT
  msg["List-Unsubscribe"] = f"<mailto:{UNSUBSCRIBE_EMAIL}>" if UNSUBSCRIBE_EMAIL else ""

  msg.attach(MIMEText(plain_body, "plain", "utf-8"))
  msg.attach(MIMEText(html_body, "html", "utf-8"))

  # 收件人列表：发件人 + 所有密送地址
  recipients = [SMTP_FROM_ADDR] + bcc_list

  context = ssl.create_default_context()
  try:
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
      server.login(SMTP_USER, SMTP_PASS)
      server.sendmail(SMTP_FROM_ADDR, recipients, msg.as_string())
  except smtplib.SMTPException as e:
    print(f"SMTP 发送失败: {e}")
    sys.exit(1)

  print(f"邮件已发送 → 密送 {len(bcc_list)} 位订阅者")


# ── 主流程 ──────────────────────────────────────────────────

def main():
  # 1. 解析密送列表
  bcc_list = [addr.strip() for addr in EMAIL_LIST.split() if addr.strip()]
  if not bcc_list:
    print("错误: EMAIL_LIST 为空")
    sys.exit(1)
  print(f"订阅者数量: {len(bcc_list)}")

  # 2. 抓取并解析 RSS
  print(f"正在抓取 RSS: {RSS_URL}")
  feed = feedparser.parse(RSS_URL)

  if feed.bozo and not feed.entries:
    print(f"RSS 解析失败: {feed.bozo_exception}")
    sys.exit(1)

  if not feed.entries:
    print("RSS 中没有文章，退出")
    sys.exit(0)

  # 3. 读取已发送记录
  sent_links = load_sent_links()
  print(f"已发送记录: {len(sent_links)} 篇")

  # 4. 遍历所有文章，逐篇判断并发送
  new_count = 0
  for entry in feed.entries:
    title = entry.get("title", "").strip()
    summary = entry.get("summary", "").strip()
    link = entry.get("link", "").strip()

    if not title or not link:
      print(f"跳过缺少标题或链接的条目")
      continue

    if link in sent_links:
      print(f"已发送过: 《{title}》，跳过")
      continue

    # 未发送 → 逐篇发信
    print(f"新文章: 《{title}》 — {link}")

    html_body = build_html_content(title, summary, link)
    plain_body = build_plain_content(title, summary, link)

    send_email(html_body, plain_body, bcc_list)
    save_sent_link(link)
    sent_links.add(link)
    new_count += 1

  print(f"完成。本次共发送 {new_count} 篇新文章")
  if new_count == 0:
    sys.exit(0)


if __name__ == "__main__":
  main()
