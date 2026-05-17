# RSS → Email 文章更新通知 / RSS → Email Update Notifier

[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-daily_12:00_CST-blue)](https://github.com)

> 为静态博客提供文章更新邮件订阅功能。每天中午自动抓取 RSS，将最新文章以邮件密送方式推送给订阅者。
> Email subscription for static blogs. Fetches RSS daily at noon and sends new posts via BCC email.

---

## 工作原理 / How It Works

1. GitHub Actions 每天中午 12:00（北京时间）自动触发
2. 脚本从 `RSS_URL` 抓取 Atom/RSS feed
3. 提取最新一篇文章的标题、摘要、链接
4. 与 `link.txt` 中记录的链接比对：相同则跳过，不同则继续
5. 按 `demo.html` 的格式生成 HTML 邮件正文
6. 通过 SMTP 密送给 `EMAIL_LIST` 中的所有订阅者
7. 将本次发送的文章链接写入 `link.txt` 作为缓存

> 1. GitHub Actions triggers daily at 12:00 CST
> 2. Script fetches Atom/RSS feed from `RSS_URL`
> 3. Extracts title, summary, and link of the latest post
> 4. Compares with `link.txt` — skips if already sent
> 5. Builds HTML email body following `demo.html` format
> 6. Sends via SMTP with BCC to all subscribers in `EMAIL_LIST`
> 7. Writes the sent link to `link.txt` as cache

---

## 项目结构 / Project Structure

```
demo2/
├── send_update.py              # 主脚本 / Main script
├── requirements.txt            # Python 依赖 / Dependencies
├── link.txt                    # 已发送链接缓存 / Sent link cache
├── demo.html                   # HTML 邮件模板参考 / Email template reference
└── .github/
    └── workflows/
        └── send.yml            # GitHub Actions 工作流 / Workflow
```

---

## 配置 / Configuration

所有配置通过 GitHub Secrets 管理，在仓库 **Settings → Secrets and variables → Actions** 中添加：

> All configuration is managed via GitHub Secrets. Add them at **Settings → Secrets and variables → Actions**:

| Secret | 说明 / Description | 示例 / Example |
|--------|-------------------|----------------|
| `SMTP_SERVER` | SMTP 服务器地址 / SMTP server | `smtp.resend.com` |
| `SMTP_PORT` | SMTP 端口 / SMTP port | `465` |
| `SMTP_USER` | SMTP 用户名 / SMTP username | `resend` |
| `SMTP_PASS` | SMTP 密码 / SMTP password | `re_xxxx` |
| `SMTP_FROM_NAME` | 发件人名称 / Sender name | `他说` |
| `SMTP_FROM_ADDR` | 发件人邮箱 / Sender email | `subscribe@example.com` |
| `SMTP_SUBJECT` | 邮件标题 / Email subject | `他说，你收到了新的订阅` |
| `RSS_URL` | RSS 订阅地址 / RSS feed URL | `https://example.com/atom.xml` |
| `EMAIL_LIST` | 密送列表（空格分隔）/ BCC list (space-separated) | `a@qq.com b@yeah.net` |
| `TAG_TITLE` | 标题标签名 / Title tag | `h1` |
| `TAG_SUMMARY` | 摘要标签名 / Summary tag | `p` |
| `TAG_LINK` | 链接标签名 / Link tag | `a` |
| `LINK_TEXT` | 链接显示文字 / Link text | `阅读详情` |

---

## 使用 / Usage

### 1. 配置 Secrets
在 GitHub 仓库设置中添加上述 14 个 Secrets。

> Add all 14 Secrets in your GitHub repository settings.

### 2. 启用 Actions
推送代码到默认分支后，工作流将自动生效。每天中午自动运行，也可以在 Actions 页面手动触发。

> Push to the default branch. The workflow runs automatically at noon daily. You can also trigger it manually from the Actions tab.

### 3. 本地测试 / Local Testing

```bash
# 创建虚拟环境 / Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖 / Install dependencies
pip install -r requirements.txt

# 设置环境变量并运行 / Export env vars and run
export SMTP_SERVER="smtp.resend.com"
export SMTP_PORT="465"
export SMTP_USER="resend"
export SMTP_PASS="re_xxxx"
export SMTP_FROM_NAME="他说"
export SMTP_FROM_ADDR="subscribe@example.com"
export SMTP_SUBJECT="他说，你收到了新的订阅"
export RSS_URL="https://example.com/atom.xml"
export EMAIL_LIST="a@qq.com b@yeah.net"

python send_update.py
```

---

## 依赖 / Dependencies

- Python 3.11+
- [feedparser](https://pypi.org/project/feedparser) — RSS/Atom feed 解析
- Python 内置库：`smtplib`, `email`, `ssl`, `xml`, `re`, `os`

---

## 许可 / License

MIT
