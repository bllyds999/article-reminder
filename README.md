# RSS → Email 文章更新通知 / RSS → Email Update Notifier

[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-daily_12:00_CST-blue)](https://github.com)

> 为静态博客提供文章更新邮件订阅功能。每天中午自动抓取 RSS，将最新文章以邮件密送方式推送给订阅者。
> Email subscription for static blogs. Fetches RSS daily at noon and sends new posts via BCC email.

---

## 工作原理 / How It Works

1. GitHub Actions 每天中午 12:00（北京时间）自动触发
2. 脚本从 `RSS_URL` 抓取 Atom/RSS feed
3. 读取 `link.txt` 中所有已发送的链接记录
4. **遍历 RSS 中的每一篇文章**，逐篇与已发送记录比对
5. 每篇未发送的文章，单独生成一封 HTML 邮件并发给 `EMAIL_LIST` 的所有订阅者
6. 每封邮件包含 `List-Unsubscribe` 邮件头和退订联系方式
7. 将新发送的链接追加写入 `link.txt`

> 1. GitHub Actions triggers daily at 12:00 CST
> 2. Script fetches Atom/RSS feed from `RSS_URL`
> 3. Reads all previously-sent links from `link.txt`
> 4. **Iterates over every entry** in the feed, comparing each against the sent records
> 5. Each unsent article gets its own email to all subscribers in `EMAIL_LIST`
> 6. Every email includes a `List-Unsubscribe` header and unsubscribe contact
> 7. Appends each newly-sent link to `link.txt`

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
| `UNSUBSCRIBE_EMAIL` | 退订邮箱（可选）/ Unsubscribe email (optional) | `unsubscribe@example.com` |

---

## 使用 / Usage

### 1. 配置 Secrets
在 GitHub 仓库设置中添加上述 15 个 Secrets。

> Add all 15 Secrets in your GitHub repository settings.

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
