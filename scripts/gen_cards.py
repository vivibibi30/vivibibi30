#!/usr/bin/env python3
"""生成 GitHub 主页自绘卡片（stats / contributions），输出到 assets/。

只用标准库，token 从环境变量 GH_TOKEN / GITHUB_TOKEN 或 `gh auth token` 读取。
"""
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone

USER = os.environ.get("GH_USER", "vivibibi30")
API = "https://api.github.com"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

FONT = ("-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,"
        "'PingFang SC','Microsoft YaHei',sans-serif")
MONO = ("ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,"
        "'Liberation Mono',monospace")

THEME = {
    "light": dict(bg="#ffffff", card="#f6f8fa", border="#d0d7de", text="#1f2328",
                  muted="#59636e", accent="#0969da", empty="#ebedf0",
                  l1="#9be9a8", l2="#40c463", l3="#30a14e", l4="#216e39"),
    "dark": dict(bg="#0d1117", card="#161b22", border="#30363d", text="#e6edf3",
                 muted="#9198a1", accent="#4493f8", empty="#161b22",
                 l1="#0e4429", l2="#006d32", l3="#26a641", l4="#39d353"),
}

LANG_COLOR = {
    "Java": "#b07219", "Kotlin": "#A97BFF", "C": "#555555", "C++": "#f34b7d",
    "Python": "#3572A5", "Shell": "#89e051", "Makefile": "#427819",
    "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "HTML": "#e34c26",
    "Groovy": "#4298b8", "Batchfile": "#C1F12E", "Dockerfile": "#384d54",
}


def token():
    for k in ("GH_TOKEN", "GITHUB_TOKEN"):
        if os.environ.get(k):
            return os.environ[k]
    try:
        return subprocess.check_output(["gh", "auth", "token"], text=True).strip()
    except Exception:
        sys.exit("缺少 token：设置 GH_TOKEN 或先 gh auth login")


TOKEN = token()


def api(path, graphql=None, variables=None):
    url = API + path if graphql is None else API + "/graphql"
    payload = None if graphql is None else {"query": graphql, "variables": variables or {}}
    body = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": "Bearer " + TOKEN,
        "Accept": "application/vnd.github+json",
        "User-Agent": "profile-cards",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.load(r)


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


QUERY = """
query($login:String!){
  user(login:$login){
    login name bio createdAt
    followers{totalCount} following{totalCount}
    contributionsCollection{
      totalCommitContributions totalIssueContributions
      totalPullRequestContributions totalRepositoryContributions
      contributionCalendar{ totalContributions
        weeks{ contributionDays{ date contributionCount } } } }
    repositories(first:50, ownerAffiliations:[OWNER], privacy:PUBLIC, isFork:false,
                 orderBy:{field:PUSHED_AT, direction:DESC}){
      totalCount nodes{ name description stargazerCount forkCount pushedAt
                        primaryLanguage{name} licenseInfo{spdxId} } } } }
"""


def fetch():
    d = api("", graphql=QUERY, variables={"login": USER})
    u = d["data"]["user"]
    langs = {}
    for r in u["repositories"]["nodes"]:
        try:
            for k, v in api(f"/repos/{u['login']}/{r['name']}/languages").items():
                langs[k] = langs.get(k, 0) + v
        except Exception:
            pass
    return u, langs


def lang_bar(langs, total_width):
    tot = sum(langs.values()) or 1
    items = sorted(langs.items(), key=lambda kv: -kv[1])
    out, x = [], 0.0
    for name, size in items:
        w = size / tot * total_width
        out.append((name, size / tot * 100, x, w))
        x += w
    return out


def stats_svg(u, langs, mode):
    t = THEME[mode]
    W, H, PAD = 740, 240, 24
    lang_total = sum(langs.values()) or 1
    bars = lang_bar(langs, W - PAD * 2)
    name = u.get("name") or u["login"]
    bio = u.get("bio") or "Android 逆向 / LSPosed 模块开发"
    since = datetime.strptime(u["createdAt"], "%Y-%m-%dT%H:%M:%SZ").year
    c = u["contributionsCollection"]
    stats = [
        ("仓库", str(u["repositories"]["totalCount"])),
        ("获得的 star", str(sum(r["stargazerCount"] for r in u["repositories"]["nodes"]))),
        ("关注者", str(u["followers"]["totalCount"])),
        ("近一年提交", str(c["contributionCalendar"]["totalContributions"])),
    ]
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" role="img" aria-label="{esc(name)} 的 GitHub 概览">',
         f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="{t["bg"]}" '
         f'stroke="{t["border"]}"/>',
         f'<text x="{PAD}" y="46" font-family="{FONT}" font-size="24" font-weight="600" '
         f'fill="{t["text"]}">{esc(name)}</text>',
         f'<text x="{PAD}" y="70" font-family="{MONO}" font-size="13" '
         f'fill="{t["muted"]}">@{esc(u["login"])}</text>',
         f'<text x="{PAD}" y="94" font-family="{FONT}" font-size="13" '
         f'fill="{t["muted"]}">{esc(bio)}</text>']

    # 统计块
    colw = (W - PAD * 2) / len(stats)
    for i, (label, val) in enumerate(stats):
        x = PAD + colw * i
        p.append(f'<rect x="{x}" y="112" width="{colw - 12}" height="56" rx="8" '
                 f'fill="{t["card"]}" stroke="{t["border"]}" stroke-width="1"/>')
        p.append(f'<text x="{x + 14}" y="137" font-family="{FONT}" font-size="19" '
                 f'font-weight="600" fill="{t["text"]}">{val}</text>')
        p.append(f'<text x="{x + 14}" y="157" font-family="{FONT}" font-size="11.5" '
                 f'fill="{t["muted"]}">{esc(label)}</text>')

    # 语言条
    y = 190
    p.append(f'<text x="{PAD}" y="{y}" font-family="{FONT}" font-size="11.5" '
             f'fill="{t["muted"]}">主要语言（公开仓库代码占比）</text>')
    bx, by, bw, bh = PAD, y + 8, W - PAD * 2, 8
    p.append(f'<clipPath id="lc{mode}"><rect x="{bx}" y="{by}" width="{bw}" '
             f'height="{bh}" rx="4"/></clipPath>')
    p.append(f'<g clip-path="url(#lc{mode})">')
    for nm, pct, off, w in bars:
        p.append(f'<rect x="{bx + off:.2f}" y="{by}" width="{max(w,0):.2f}" height="{bh}" '
                 f'fill="{LANG_COLOR.get(nm, "#8b949e")}"/>')
    p.append("</g>")
    lx = PAD
    for nm, pct, off, w in bars[:4]:
        if pct < 3:
            continue
        p.append(f'<circle cx="{lx + 5}" cy="{by + 22}" r="5" '
                 f'fill="{LANG_COLOR.get(nm, "#8b949e")}"/>')
        p.append(f'<text x="{lx + 16}" y="{by + 26}" font-family="{FONT}" font-size="11.5" '
                 f'fill="{t["muted"]}">{esc(nm)} {pct:.1f}%</text>')
        lx += 16 + 9 * len(f"{nm} {pct:.1f}%") + 22
    p.append(f'<text x="{W - PAD}" y="{by + 26}" text-anchor="end" font-family="{FONT}" '
             f'font-size="11" fill="{t["muted"]}">since {since}</text>')
    p.append("</svg>")
    return "\n".join(p)


def contrib_svg(u, mode):
    t = THEME[mode]
    cal = u["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    cell, gap, left, top = 10, 3, 34, 46
    W = left + len(weeks) * (cell + gap) + 17
    H = top + 7 * (cell + gap) + 28
    total = cal["totalContributions"]
    deltas = [w["contributionDays"] for w in weeks]
    mx = max((d["contributionCount"] for w in deltas for d in w), default=1) or 1

    def level(n):
        if n == 0:
            return 0
        r = n / mx
        return 1 if r <= 0.25 else 2 if r <= 0.5 else 3 if r <= 0.75 else 4

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="近一年 {total} 次贡献">',
         f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="{t["bg"]}" '
         f'stroke="{t["border"]}"/>',
         f'<text x="{left}" y="23" font-family="{FONT}" font-size="13" '
         f'fill="{t["text"]}">近一年 <tspan font-weight="600">{total}</tspan> 次贡献</text>']
    for r, label in enumerate(["", "Mon", "", "Wed", "", "Fri", ""]):
        if label:
            p.append(f'<text x="{left - 8}" y="{top + r * (cell + gap) + cell - 2}" '
                     f'text-anchor="end" font-family="{FONT}" font-size="9.5" '
                     f'fill="{t["muted"]}">{label}</text>')
    last_month = None
    for ci, week in enumerate(deltas):
        first = week[0]["date"] if week else None
        if first:
            m = int(first[5:7])
            if m != last_month:
                last_month = m
                p.append(f'<text x="{left + ci * (cell + gap)}" y="{top - 7}" '
                         f'font-family="{FONT}" font-size="9.5" fill="{t["muted"]}">'
                         f'{m}月</text>')
        for ri, day in enumerate(week):
            lv = level(day["contributionCount"])
            fill = t["empty"] if lv == 0 else t[f"l{lv}"]
            p.append(f'<rect x="{left + ci * (cell + gap)}" y="{top + ri * (cell + gap)}" '
                     f'width="{cell}" height="{cell}" rx="2.5" fill="{fill}"/>')
    # 图例
    lgx = W - 17 - 5 * (cell + gap)
    lgy = H - 12
    p.append(f'<text x="{lgx - 8}" y="{lgy + 8}" text-anchor="end" font-family="{FONT}" '
             f'font-size="9.5" fill="{t["muted"]}">少</text>')
    for i in range(5):
        fill = t["empty"] if i == 0 else t[f"l{i}"]
        p.append(f'<rect x="{lgx + i * (cell + gap)}" y="{lgy}" width="{cell}" '
                 f'height="{cell}" rx="2.5" fill="{fill}"/>')
    p.append(f'<text x="{lgx + 5 * (cell + gap) + 4}" y="{lgy + 8}" font-family="{FONT}" '
             f'font-size="9.5" fill="{t["muted"]}">多</text>')
    p.append(f'<text x="{left}" y="{lgy + 8}" font-family="{FONT}" font-size="9.5" '
             f'fill="{t["muted"]}">更新于 '
             f'{datetime.now(timezone.utc).strftime("%Y-%m-%d")}</text>')
    p.append("</svg>")
    return "\n".join(p)


def main():
    os.makedirs(OUT, exist_ok=True)
    u, langs = fetch()
    for mode in ("light", "dark"):
        open(os.path.join(OUT, f"stats-{mode}.svg"), "w").write(stats_svg(u, langs, mode))
        open(os.path.join(OUT, f"contrib-{mode}.svg"), "w").write(contrib_svg(u, mode))
    print("ok", u["login"], "langs:", {k: v for k, v in sorted(langs.items(), key=lambda x: -x[1])[:4]})


if __name__ == "__main__":
    main()
