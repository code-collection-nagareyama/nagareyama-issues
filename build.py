#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""data/issues.json から docs/ の静的サイトを生成する。

    python build.py

生成物は docs/ 以下。GitHub Pages は main ブランチの /docs を公開する設定を想定。
"""

import html
import json
import os
import shutil
from urllib.parse import quote, urlencode

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data", "issues.json")
OUT = os.path.join(ROOT, "docs")

SITE_TITLE = "Nagareyama Issues"
SITE_BRAND = "Nagareyama Issues"
SITE_TAGLINE = "データをもとに描きだした課題"
GITHUB_REPO = "code-collection-nagareyama/nagareyama-issues"
ISSUE_TEMPLATE = "card-feedback.yml"

# テーマごとのアクセント色。カード・図・チップで共通に使う。
THEME_COLOR = {
    "移動・交通": "#2563eb",
    "暮らし・商業": "#b45309",
    "安全・道路": "#dc2626",
    "防災": "#ea580c",
    "防災 × 福祉": "#7c3aed",
    "子育て": "#db2777",
    "施設・行政": "#0e7490",
    "財政": "#4d7c0f",
    "健康・救急": "#e11d48",
    "環境": "#047857",
}

# ---------------------------------------------------------------- icons
# 48x48 のグリッドに線で描く。fill は none、stroke は currentColor。
# シーン図とカードで共通に使うため <symbol> として1回だけ吐く。
ICONS = {
    "elder": """<circle cx="17" cy="11" r="5.5"/><path d="M17 17v12M9.5 21h15M17 29l-4.5 13M17 29l4.5 13"/><path d="M33 20v23M28.5 21h4.5"/>""",
    "parentchild": """<circle cx="15" cy="10" r="5"/><path d="M15 15v11M8 20h14M15 26l-4 13M15 26l4 13"/><circle cx="33" cy="21" r="4"/><path d="M33 25v7M28 28h10M33 32l-2.5 8M33 32l2.5 8"/><path d="M22 28h6"/>""",
    "people": """<circle cx="12" cy="14" r="4.5"/><path d="M5 34c0-5 3-9 7-9s7 4 7 9"/><circle cx="36" cy="14" r="4.5"/><path d="M29 34c0-5 3-9 7-9s7 4 7 9"/><circle cx="24" cy="20" r="5.5"/><path d="M15 42c0-6 4-11 9-11s9 5 9 11"/>""",
    "bus": """<rect x="6" y="10" width="36" height="23" rx="4"/><path d="M6 21h36M15 15v6M24 15v6M33 15v6"/><circle cx="14" cy="37" r="3.5"/><circle cx="34" cy="37" r="3.5"/>""",
    "busstop": """<rect x="11" y="5" width="26" height="14" rx="3"/><path d="M24 19v25M16 44h16"/><path d="M17 12h14"/>""",
    "basket": """<path d="M9 17h30l-3.5 22a2 2 0 0 1-2 2h-19a2 2 0 0 1-2-2z"/><path d="M17 17l4-10M31 17l-4-10"/><path d="M19 24v10M29 24v10"/>""",
    "shop": """<path d="M7 18h34v21a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2z"/><path d="M6 18l4-9h28l4 9"/><path d="M19 41V28h10v13"/>""",
    "home": """<path d="M7 23L24 9l17 14"/><path d="M12 22v18h24V22"/><path d="M20 40V29h8v11"/>""",
    "building": """<rect x="11" y="6" width="26" height="36" rx="2"/><path d="M17 14h4M27 14h4M17 22h4M27 22h4M17 30h4M27 30h4"/><path d="M20 42v-6h8v6"/>""",
    "school": """<path d="M8 21L24 11l16 10"/><path d="M11 21v20h26V21"/><path d="M24 11V4h8v5h-8"/><path d="M20 41V30h8v11"/>""",
    "hospital": """<rect x="8" y="13" width="32" height="29" rx="3"/><path d="M24 20v15M16.5 27.5h15"/><path d="M17 13V7h14v6"/>""",
    "heart": """<path d="M24 41C10 31 7 22 13 16.5c4.6-4.2 9.7-.8 11 3 1.3-3.8 6.4-7.2 11-3C41 22 38 31 24 41z"/><path d="M25 19l-4.5 8h6l-3.5 8"/>""",
    "flood": """<path d="M13 25l11-10 11 10"/><path d="M17 25v8M31 25v8"/><path d="M5 34c4-4 8-4 12 0s8 4 12 0 8-4 12 0"/><path d="M5 42c4-4 8-4 12 0s8 4 12 0 8-4 12 0"/>""",
    "shelter": """<path d="M8 20L24 8l16 12"/><path d="M12 20v20h24V20"/><path d="M24 40V25"/><path d="M18 31l6-6 6 6"/>""",
    "trash": """<path d="M11 15h26l-2.2 25a2 2 0 0 1-2 1.8H15.2a2 2 0 0 1-2-1.8z"/><path d="M7 15h34"/><path d="M18 15v-4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v4"/><path d="M20 22v12M28 22v12"/>""",
    "calendar": """<rect x="7" y="11" width="34" height="31" rx="3"/><path d="M7 21h34M16 6v9M32 6v9"/><circle cx="17" cy="29" r="1.8"/><circle cx="24" cy="29" r="1.8"/><circle cx="31" cy="29" r="1.8"/><circle cx="17" cy="36" r="1.8"/>""",
    "clock": """<circle cx="24" cy="24" r="17"/><path d="M24 12v12l8 6"/>""",
    "map": """<path d="M6 14l12-5 12 5 12-5v25l-12 5-12-5-12 5z"/><path d="M18 9v25M30 14v25"/>""",
    "coin": """<circle cx="24" cy="24" r="16"/><path d="M17 15l7 9 7-9"/><path d="M24 24v13M18 27h12M18 32h12"/>""",
    "doc": """<path d="M12 5h16l9 9v29a2 2 0 0 1-2 2H12a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2z"/><path d="M28 5v10h9"/><path d="M17 24h14M17 31h14M17 38h8"/>""",
    "phone": """<rect x="14" y="4" width="20" height="40" rx="4"/><path d="M20 9h8"/><circle cx="24" cy="38" r="2"/>""",
    "search": """<circle cx="21" cy="21" r="13"/><path d="M30.5 30.5L42 42"/>""",
    "question": """<circle cx="24" cy="24" r="17"/><path d="M19 19a5 5 0 1 1 6.5 4.8c-1 .4-1.5 1.2-1.5 2.2v2"/><circle cx="24" cy="34" r="1.8"/>""",
    "alert": """<path d="M24 7l19 33H5z"/><path d="M24 19v11"/><circle cx="24" cy="35" r="1.8"/>""",
    "wall": """<rect x="6" y="11" width="36" height="26" rx="2"/><path d="M6 20h36M6 28h36"/><path d="M18 11v9M30 11v9M13 20v8M25 20v8M37 20v8M18 28v9M30 28v9"/>""",
    "chart": """<path d="M9 7v33h33"/><rect x="14" y="26" width="6" height="14"/><rect x="24" y="18" width="6" height="22"/><rect x="34" y="11" width="6" height="29"/>""",
    "park": """<path d="M24 42V26"/><circle cx="24" cy="18" r="11"/><path d="M24 30l-7-6M24 33l7-6"/>""",
    "bicycle": """<circle cx="12" cy="33" r="8"/><circle cx="36" cy="33" r="8"/><path d="M12 33l8-14h9M20 19l10 14M27 19h7"/>""",
    "car": """<path d="M9 29l4-11a3 3 0 0 1 3-2h16a3 3 0 0 1 3 2l4 11"/><rect x="6" y="29" width="36" height="9" rx="3"/><circle cx="15" cy="40" r="2.5"/><circle cx="33" cy="40" r="2.5"/>""",
}

ICON_LABEL = {
    "elder": "高齢者",
    "parentchild": "親子",
    "people": "人びと",
    "bus": "バス",
    "busstop": "バス停",
    "basket": "買い物",
    "shop": "店舗",
    "home": "住まい",
    "building": "施設",
    "school": "学校",
    "hospital": "病院",
    "heart": "救急",
    "flood": "浸水",
    "shelter": "避難所",
    "trash": "ごみ",
    "calendar": "日程",
    "clock": "時間",
    "map": "地図",
    "coin": "財政",
    "doc": "書類",
    "phone": "スマホ",
    "search": "検索",
    "question": "わからない",
    "alert": "注意",
    "wall": "壁",
    "chart": "グラフ",
    "park": "緑地",
    "bicycle": "自転車",
    "car": "車",
}

STAGES = [("いま", "now"), ("ぶつかる壁", "wall"), ("こうしたい", "wish")]


def esc(s):
    return html.escape(str(s), quote=True)


# 行頭に置かない文字（禁則処理）。前の行にぶら下げる。
NO_LINE_START = "、。，．・：；）］｝」』〉》ー！？!?,.）】"


def wrap_jp(text, per_line=15, max_lines=4):
    """句読点の直後を優先して折り返す。無いときだけ字数で切る。"""
    prefer = "。、．，!？"
    chunks, buf = [], ""
    for ch in text:
        buf += ch
        if ch in prefer:
            chunks.append(buf)
            buf = ""
    if buf:
        chunks.append(buf)

    lines, cur = [], ""
    for chunk in chunks:
        if cur and len(cur) + len(chunk) > per_line + 2:
            lines.append(cur)
            cur = ""
        cur += chunk
        while len(cur) > per_line + 4:
            cut = per_line
            while cut < len(cur) and cur[cut] in NO_LINE_START:
                cut += 1
            if cut >= len(cur):
                break
            lines.append(cur[:cut])
            cur = cur[cut:]
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        last = lines[max_lines - 1]
        lines = lines[: max_lines - 1] + [last[: max(1, per_line - 1)] + "…"]
    return lines


def icon_defs():
    parts = []
    for name, body in ICONS.items():
        parts.append(
            f'<symbol id="i-{name}" viewBox="0 0 48 48" fill="none" stroke="currentColor" '
            f'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">{body}</symbol>'
        )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" '
        'style="position:absolute" aria-hidden="true"><defs>' + "".join(parts) + "</defs></svg>"
    )


def use_icon(name, size=24, cls=""):
    if name not in ICONS:
        name = "question"
    c = f' class="{cls}"' if cls else ""
    return (
        f'<svg{c} width="{size}" height="{size}" viewBox="0 0 48 48" aria-hidden="true">'
        f'<use href="#i-{name}"/></svg>'
    )


def scene_svg(panels, accent):
    """困っているシーンの3コマ図。全カード同じ骨格で、アイコンと文だけが変わる。"""
    W, H = 780, 244
    pw, ph = 240, 232
    xs = [0, 270, 540]
    out = [
        f'<svg class="scene" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="困っている場面の3コマ図" xmlns="http://www.w3.org/2000/svg">'
    ]
    for i, p in enumerate(panels[:3]):
        x = xs[i]
        label, kind = STAGES[i]
        out.append(f'<g class="pnl pnl-{kind}" transform="translate({x},6)">')
        out.append(f'<rect class="pnl-bg" x="0" y="0" width="{pw}" height="{ph}" rx="14"/>')
        out.append(f'<rect class="pnl-tab" x="14" y="14" width="{len(label)*13+18}" height="24" rx="12"/>')
        out.append(f'<text class="pnl-tablabel" x="{14+ (len(label)*13+18)/2}" y="30" text-anchor="middle">{esc(label)}</text>')
        out.append(f'<g class="pnl-icon" transform="translate({pw/2-30},52)">')
        out.append(f'<svg x="0" y="0" width="60" height="60" viewBox="0 0 48 48"><use href="#i-{p["icon"] if p["icon"] in ICONS else "question"}"/></svg>')
        out.append("</g>")
        lines = wrap_jp(p["text"], per_line=14, max_lines=4)
        y0 = 138
        for j, ln in enumerate(lines):
            out.append(
                f'<text class="pnl-text" x="{pw/2}" y="{y0 + j*21}" text-anchor="middle">{esc(ln)}</text>'
            )
        out.append("</g>")
        if i < 2:
            ax = xs[i] + pw + 6
            out.append(
                f'<g class="arrow"><path d="M{ax} 122h14"/>'
                f'<path d="M{ax+9} 117l5 5-5 5"/></g>'
            )
    out.append("</svg>")
    return "".join(out)


def card_label(it):
    return f"{it['id']} {it['title']}"


def github_issue_url(it):
    """カード詳細から、対象カードが入った Issue テンプレートを開く。"""
    params = urlencode(
        {
            "template": ISSUE_TEMPLATE,
            "card": card_label(it),
            "title": f"[{it['id']}] ",
        },
        quote_via=quote,
        safe="",
    )
    return f"https://github.com/{GITHUB_REPO}/issues/new?{params}"


def report_button(it, extra_class=""):
    cls = "gh-issue" + (f" {extra_class}" if extra_class else "")
    return (
        f'<a class="{cls}" href="{esc(github_issue_url(it))}" '
        f'target="_blank" rel="noopener noreferrer">'
        f"このカードへの気づきを起票する</a>"
    )


def meter(value, maximum=5, label=""):
    dots = "".join(
        f'<span class="dot{" on" if i < value else ""}"></span>' for i in range(maximum)
    )
    return f'<span class="meter" title="{esc(label)}: {value}/{maximum}">{dots}</span>'


# ---------------------------------------------------------------- layout
def nav_link(label, href, current, name):
    cls = "nav-link active" if current == name else "nav-link"
    return f'<a class="{cls}" href="{href}">{label}</a>'


def page(title, body, css_depth=0, desc="", nav="index"):
    up = "../" * css_depth
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@400;500;700&family=Zen+Old+Mincho:wght@600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{up}assets/site.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E%F0%9F%97%BE%3C/text%3E%3C/svg%3E">
</head>
<body>
{icon_defs()}
<header class="header">
  <a class="brand" href="{up}index.html">{SITE_BRAND}<small>{SITE_TAGLINE}</small></a>
  <nav class="nav" aria-label="メインメニュー">
    {nav_link("課題一覧", up + "index.html", nav, "index")}
    {nav_link("テンプレート", up + "template.html", nav, "template")}
    {nav_link("データ出典", up + "sources.html", nav, "sources")}
  </nav>
</header>
<main>
{body}
</main>
<footer class="foot">
  <p>出典: <a href="https://www.city.nagareyama.chiba.jp/opendata/1042063/1042065.html">流山市オープンデータカタログサイト</a>（259データセット）、流山市議会 会議録（2018〜2026年）、ながれやままちづくり達成度アンケート自由記述（13,561件）。</p>
  <p>本サイトの課題整理・活用アイデアは有志によるもので、流山市の見解ではありません。会議録の要約は機械処理を含みます。引用は原典を確認してください。</p>
</footer>
<script src="{up}assets/site.js"></script>
</body>
</html>
"""


def render_index(d):
    m = d["meta"]
    ctx = "".join(
        f'<div class="stat"><div class="stat-v">{esc(c["value"])}</div>'
        f'<div class="stat-l">{esc(c["label"])}</div>'
        f'<div class="stat-n">{esc(c["note"])}</div></div>'
        for c in m["context"]
    )
    themes = sorted({i["theme"] for i in d["issues"]}, key=lambda t: list(THEME_COLOR).index(t))
    chips = "".join(
        f'<button class="chip" data-theme="{esc(t)}" style="--c:{THEME_COLOR[t]}">{esc(t)}</button>'
        for t in themes
    )
    cards = []
    for it in d["issues"]:
        c = THEME_COLOR.get(it["theme"], "#555")
        f = it["feasibility"]
        cards.append(f"""
<a class="card" href="issues/{esc(it['slug'])}.html" style="--c:{c}" data-theme="{esc(it['theme'])}" data-data="{f['data']}" data-diff="{f['difficulty']}">
  <div class="card-head">
    <span class="card-id">{esc(it['id'])}</span>
    <span class="card-theme">{esc(it['theme'])}</span>
  </div>
  <div class="card-body">
    <span class="card-ico">{use_icon(it['persona'].get('icon','question'), 34)}</span>
    <div>
      <h3>{esc(it['title'])}</h3>
      <p class="card-catch">{esc(it['catch'])}</p>
    </div>
  </div>
  <div class="card-foot">
    <span class="badges">
      <span class="badge">OD {len(it['evidence']['opendata'])}</span>
      <span class="badge">議会 {len(it['evidence']['council'])}</span>
      <span class="badge">声 {len(it['evidence'].get('voice', []))}</span>
    </span>
    <span class="meters">
      <span class="meter-lbl">データ</span>{meter(f['data'], label='データ充足度')}
      <span class="meter-lbl">難易度</span>{meter(f['difficulty'], label='実装難易度')}
    </span>
  </div>
</a>""")

    backlog = "".join(
        f'<li><strong>{esc(b["title"])}</strong><span>{esc(b["note"])}</span></li>'
        for b in d.get("backlog", [])
    )

    body = f"""
<section class="hero">
  <p class="kicker">流山市 オープンデータ × 市議会の議論</p>
  <h1>{esc(m['subtitle'])}</h1>
  <p class="lede">
    市が公開している{m['counts']['datasets']}データセット（{m['counts']['files']}ファイル・{esc(m['counts']['bytes_label'])}）と、
    {esc(m['counts']['minutes_years'])}年の市議会会議録、まちづくり達成度アンケートの自由記述{m['counts']['survey_comments']:,}件を突き合わせて、
    想定される社会課題を10枚のカードに描きました。
    すべてのカードは<a href="template.html">同じスキーム</a>に沿っています。
    読んで気づいたことは、各カードのページから GitHub Issue に起票できます。
  </p>
  <div class="stats">{ctx}</div>
</section>

<section class="filters" aria-label="絞り込み">
  <div class="filter-row">
    <span class="filter-lbl">テーマ</span>
    <div class="chips">{chips}</div>
  </div>
  <div class="filter-row">
    <span class="filter-lbl">並び替え</span>
    <div class="chips">
      <button class="chip sort on" data-sort="id">番号順</button>
      <button class="chip sort" data-sort="data">データが揃っている順</button>
      <button class="chip sort" data-sort="easy">作りやすい順</button>
    </div>
  </div>
  <p class="filter-count"><span id="count">{len(d['issues'])}</span> 件</p>
</section>

<section class="grid" id="grid">{''.join(cards)}</section>

<section class="backlog">
  <h2>次に整理したい候補</h2>
  <p class="sub">同じスキームで書ける材料はあるが、今回の10枚には入れなかったもの。</p>
  <ul class="backlog-list">{backlog}</ul>
</section>
"""
    return page(f"{SITE_TITLE} — {m['subtitle']}", body, 0, m["subtitle"], nav="index")


def render_issue(it, prev_it, next_it):
    c = THEME_COLOR.get(it["theme"], "#555")
    f = it["feasibility"]
    p = it["persona"]
    pain = it["pain"]

    stories = "".join(
        f"""<li class="story">
  <span class="story-part"><span class="story-k">だれとして</span>{esc(s['as'])}</span>
  <span class="story-part"><span class="story-k">何がしたい</span>{esc(s['want'])}</span>
  <span class="story-part"><span class="story-k">なぜなら</span>{esc(s['so'])}</span>
</li>"""
        for s in it["stories"]
    )

    od = "".join(
        f'<li><div class="ev-name">{esc(e["name"])}</div>'
        f'<div class="ev-cat">{esc(e["cat"])}</div>'
        f'<div class="ev-fact">{esc(e["fact"])}</div></li>'
        for e in it["evidence"]["opendata"]
    )
    council = "".join(
        f'<li><div class="ev-name">{esc(e["topic"])} <span class="ev-yr">{esc(e["years"])}</span></div>'
        f'<div class="ev-fact">{esc(e["gist"])}</div></li>'
        for e in it["evidence"]["council"]
    )
    voices = "".join(
        f'<li><blockquote>{esc(v["quote"])}</blockquote>'
        f'<cite>{esc(v["year"])}年・{esc(v["area"])}</cite></li>'
        for v in it["evidence"].get("voice", [])
    )
    voice_block = (
        f'<div class="ev-col"><h3><span class="ev-tag t-voice">市民の声</span>まちづくり達成度アンケート 自由記述</h3><ul class="voices">{voices}</ul></div>'
        if voices
        else ""
    )

    what = "".join(f"<li>{esc(w)}</li>" for w in it["solution"]["what"])
    kpi = "".join(f"<li>{esc(k)}</li>" for k in it["kpi"])
    missing = "".join(f"<li>{esc(x)}</li>" for x in f["missing"])

    flow_ds = "".join(
        f'<span class="flow-chip">{esc(e["name"])}</span>' for e in it["evidence"]["opendata"]
    )

    nav = []
    if prev_it:
        nav.append(f'<a class="pn prev" href="{esc(prev_it["slug"])}.html"><span>← {esc(prev_it["id"])}</span>{esc(prev_it["title"])}</a>')
    else:
        nav.append("<span></span>")
    if next_it:
        nav.append(f'<a class="pn next" href="{esc(next_it["slug"])}.html"><span>{esc(next_it["id"])} →</span>{esc(next_it["title"])}</a>')
    else:
        nav.append("<span></span>")

    body = f"""
<article class="issue" style="--c:{c}">
  <nav class="crumbs"><a href="../index.html">課題一覧</a> <span>/</span> {esc(it['id'])}</nav>

  <header class="issue-head">
    <span class="card-theme big">{esc(it['theme'])}</span>
    <h1>{esc(it['title'])}</h1>
    <p class="issue-catch">{esc(it['catch'])}</p>
    <p class="issue-actions">{report_button(it)}</p>
  </header>

  <section class="block persona-block">
    <h2><span class="n">1</span>だれの、どの場面か</h2>
    <div class="persona">
      <span class="persona-ico">{use_icon(p.get('icon','question'), 44)}</span>
      <div>
        <div class="persona-label">{esc(p['label'])}</div>
        <p>{esc(p['situation'])}</p>
      </div>
    </div>
    <dl class="pain">
      <div><dt>いつ</dt><dd>{esc(pain['when'])}</dd></div>
      <div><dt>どこで</dt><dd>{esc(pain['where'])}</dd></div>
      <div><dt>何に困るか</dt><dd>{esc(pain['what'])}</dd></div>
      <div><dt>今はどうしているか</dt><dd>{esc(pain['now'])}</dd></div>
    </dl>
  </section>

  <section class="block">
    <h2><span class="n">2</span>困っている場面</h2>
    <div class="scene-wrap">{scene_svg(it['scene']['panels'], c)}</div>
  </section>

  <section class="block">
    <h2><span class="n">3</span>ユーザーストーリー</h2>
    <ul class="stories">{stories}</ul>
  </section>

  <section class="block">
    <h2><span class="n">4</span>根拠</h2>
    <div class="evidence">
      <div class="ev-col">
        <h3><span class="ev-tag t-od">オープンデータ</span>使えるデータセット</h3>
        <ul class="ev-list">{od}</ul>
      </div>
      <div class="ev-col">
        <h3><span class="ev-tag t-council">議会</span>会議録から読み取れる論点</h3>
        <ul class="ev-list">{council}</ul>
      </div>
      {voice_block}
    </div>
  </section>

  <section class="block">
    <h2><span class="n">5</span>オープンデータ活用のかたち</h2>
    <div class="flow">
      <div class="flow-step">
        <div class="flow-lbl">使うデータ</div>
        <div class="flow-chips">{flow_ds}</div>
      </div>
      <div class="flow-arrow">→</div>
      <div class="flow-step">
        <div class="flow-lbl">つくるもの</div>
        <div class="flow-form">{esc(it['solution']['form'])}</div>
      </div>
      <div class="flow-arrow">→</div>
      <div class="flow-step">
        <div class="flow-lbl">届く人</div>
        <div class="flow-who">{esc(it['solution']['who'])}</div>
      </div>
    </div>
    <ul class="features">{what}</ul>
  </section>

  <section class="block two">
    <div>
      <h2><span class="n">6</span>どう測るか</h2>
      <ul class="kpi">{kpi}</ul>
    </div>
    <div>
      <h2><span class="n">7</span>実現度と、足りないデータ</h2>
      <div class="feas">
        <div class="feas-row"><span>データ充足度</span>{meter(f['data'], label='データ充足度')}<em>{f['data']}/5</em></div>
        <div class="feas-row"><span>実装難易度</span>{meter(f['difficulty'], label='実装難易度')}<em>{f['difficulty']}/5</em></div>
      </div>
      <h4>足りないデータ（公開要望のたたき台）</h4>
      <ul class="missing">{missing}</ul>
    </div>
  </section>

  <section class="block report">
    <h2>気づいたことがあれば</h2>
    <p class="sub">事実の誤り、足りない視点、書きぶりの改善など。GitHub の Issue テンプレートに沿って書き込めます。アカウントが必要です。</p>
    {report_button(it)}
  </section>

  <nav class="prevnext">{''.join(nav)}</nav>
</article>
"""
    return page(f"{it['id']} {it['title']} — {SITE_TITLE}", body, 1, it["catch"], nav="index")


def render_template_page(d):
    sample = d["issues"][0]
    fields = [
        ("1", "だれの、どの場面か",
         "困りごとを「いつ・どこで・何に・今はどうしているか」の4点に分け、想像で埋めず、根拠のある範囲だけを書きました。"),
        ("2", "困っている場面",
         "いま → ぶつかる壁 → こうしたい、の3コマにそろえました。カードごとに絵を描き起こすのではなく、共通のアイコンと一文で、同じ骨格の上に置いています。"),
        ("3", "ユーザーストーリー",
         "〈だれとして / 何がしたい / なぜなら〉で書きました。当事者だけでなく、行政側の担当者を主語にした視点も入れています。"),
        ("4", "根拠",
         "オープンデータ、議会、市民の声の3系統に分けました。性質の違うものを同じ重さに見せないためです。オープンデータは中身を読み、議会は会議録の論点、市民の声は自由記述を原文のまま載せています。"),
        ("5", "オープンデータ活用のかたち",
         "「使うデータ → つくるもの → 届く人」の3段で、データが現場に届く形まで書きました。"),
        ("6", "どう測るか",
         "オープンデータで測れる指標を優先し、測れないものはそのことを書きました。"),
        ("7", "実現度と足りないデータ",
         "データ充足度と実装難易度を5段階で置き、足りないデータを列挙しました。公開されているものと、されていないものの差が、ここから見えます。"),
    ]
    rows = "".join(
        f'<tr><td class="tn">{n}</td><td class="tname">{esc(name)}</td><td>{esc(desc)}</td></tr>'
        for n, name, desc in fields
    )
    body = f"""
<section class="hero narrow">
  <p class="kicker">このサイトの枠組み</p>
  <h1>社会課題を、一定のスキームで描き出す</h1>
  <p class="lede">
    わたしたちは、オープンデータと市議会の議論、市民の声を突き合わせたうえで、
    想定される社会課題を同じ7つのブロックで書き出しました。
    並べることで、<strong>根拠の厚み</strong>（オープンデータ／議会／市民の声が揃っているか）と
    <strong>実現度</strong>（データ充足度・実装難易度）を横並びに見られるようにしています。
  </p>
</section>

<section class="block">
  <h2>7つのブロック</h2>
  <table class="tpl">
    <thead><tr><th></th><th>ブロック</th><th>わたしたちが書いたこと</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</section>

<section class="block">
  <h2>3コマ図について</h2>
  <p class="sub">困っている場面は、すべて同じ3幕でそろえています。1コマ目で当事者のいまを出し、2コマ目で壁を一つに絞り、3コマ目でデータが効く形を示しました。絵は都度描き起こさず、共通のシンボルから選んでいます。</p>
  <div class="scene-wrap" style="--c:{THEME_COLOR[sample['theme']]}">{scene_svg(sample['scene']['panels'], THEME_COLOR[sample['theme']])}</div>
  <p class="sub">上は「{esc(sample['title'])}」のカードです。10枚すべてが、この骨格で書かれています。下は、3コマに使った共通のシンボルです。</p>
  <div class="iconset">
    {''.join(f'<span class="ic"><span>{use_icon(k, 28)}</span><span class="lbl">{esc(ICON_LABEL[k])}</span></span>' for k in ICONS)}
  </div>
</section>
"""
    return page(f"テンプレート — {SITE_TITLE}", body, 0, "社会課題を一定のスキームで描き出した考え方", nav="template")


def render_sources(d):
    cats = [
        ("c_01", "まちづくり・都市計画・公園緑地", 6, 19),
        ("c_02", "公共下水・配水・出水・河川", 6, 6),
        ("c_03", "道路・交通", 2, 2),
        ("c_04", "環境・リサイクル", 9, 12),
        ("c_05", "防災・防犯・安心安全", 13, 13),
        ("c_07", "教育・生涯学習", 5, 7),
        ("c_08", "芸術・文化", 2, 3),
        ("c_09", "保育・子育て", 3, 5),
        ("c_10", "高齢者・介護", 19, 23),
        ("c_11", "健康増進、医療・検診", 6, 14),
        ("c_13", "観光・商工・企業誘致・シティセールス等", 9, 49),
        ("c_15", "広報・広聴、議会", 1, 2),
        ("c_16", "財政", 68, 68),
        ("c_17", "統計データ", 17, 68),
        ("c_18", "その他の情報", 105, 232),
    ]
    used = {}
    for it in d["issues"]:
        for e in it["evidence"]["opendata"]:
            used.setdefault(e["name"], []).append(it)
    rows = "".join(
        f'<tr><td><code>{c}</code></td><td>{esc(n)}</td><td class="num">{a}</td><td class="num">{b}</td></tr>'
        for c, n, a, b in cats
    )
    ulist = "".join(
        f'<li><span class="ds">{esc(name)}</span>'
        + "".join(f'<a class="pill" href="issues/{esc(i["slug"])}.html" title="{esc(i["title"])}">{esc(i["id"])}</a>' for i in items)
        + "</li>"
        for name, items in sorted(used.items())
    )
    body = f"""
<section class="hero narrow">
  <p class="kicker">出典と、その扱い方</p>
  <h1>何を読んで、何を読んでいないか</h1>
  <p class="lede">
    このサイトの根拠は3系統です。それぞれ性質が違うので、混ぜずに分けて記載しています。
  </p>
</section>

<section class="block">
  <h2>1. 流山市オープンデータ</h2>
  <p class="sub">
    <a href="https://www.city.nagareyama.chiba.jp/opendata/1042063/1042065.html">流山市オープンデータカタログサイト</a>から取得した259データセット・523ファイル・544.9MB。
    ライセンスは CC BY（op_cc_1）または CC BY-NC-ND（op_cc_6）で、データセットごとに異なります。
    カードに書いた件数・列名は、Excel/CSV の中身を実際に読んで確認したものです。
  </p>
  <table class="tpl">
    <thead><tr><th>コード</th><th>カテゴリ</th><th class="num">データセット</th><th class="num">ファイル</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <p class="sub">配布元のカテゴリ一覧には18分類が掲示されていますが、コミュニティ・消費生活（c_06）／福祉サービス（c_12）／農業（c_14）は登録データが0件です。</p>
</section>

<section class="block">
  <h2>2. 流山市議会 会議録（2018〜2026年）</h2>
  <p class="sub">
    定例会・委員会の会議録テキストを全件取得し、テーマ別に整理したものを参照しています。
    カードの「議会」欄は<strong>会議録から読み取れる論点の要約</strong>であり、市や議会の公式見解ではありません。
    要約の生成には機械処理が含まれます。引用・意思決定に使う場合は必ず原典の会議録を確認してください。
    議案（提出日・議決日・結果）の一覧も併せて参照しています。
  </p>
</section>

<section class="block">
  <h2>3. ながれやままちづくり達成度アンケート 自由記述</h2>
  <p class="sub">
    令和2〜7年度の自由記述 13,561件。カードの引用は原文のまま、年度と地区・最寄駅を添えています。
    抽出は「その課題に言及しているか」で選んでおり、statistically representative な標本ではありません。
    件数（例: 道路への言及747件）は全13,561件に対するキーワード一致数です。
  </p>
</section>

<section class="block">
  <h2>データセットと課題カードの対応</h2>
  <ul class="usedlist">{ulist}</ul>
</section>

<section class="block">
  <h2>お断り</h2>
  <ul class="sub notes">
    <li>本サイトの課題設定・活用アイデア・実現度の評価は有志によるもので、流山市の見解ではありません。</li>
    <li>個人が特定されうるデータは扱っていません。要支援者名簿など非公開が適切なデータについては、公開を求めるのではなく集計単位での代理指標を設計する方針をとっています（N-05）。</li>
    <li>数値は取得時点（2026年8月）のものです。</li>
  </ul>
</section>
"""
    return page(f"データ出典 — {SITE_TITLE}", body, 0, "根拠に使ったデータと、その扱い方", nav="sources")


CSS = """
:root{
  --ink:#1f2a24; --ink-soft:#55645b; --dim:#78857d;
  --paper:#f5f5f0; --panel:#ffffff; --line:#dcded6;
  --green:#2c6e49; --green-deep:#1d4f34; --green-pale:#eef4ea;
  --font-sans:'Zen Kaku Gothic New','Hiragino Kaku Gothic ProN','Yu Gothic',sans-serif;
  --font-serif:'Zen Old Mincho','Hiragino Mincho ProN',serif;
  --bg:var(--paper); --ink2:var(--ink-soft); --ink3:var(--dim);
  --line2:#eceee6; --accent:var(--green); --code:#eef4ea;
  --shadow:0 1px 2px rgba(31,42,36,.05), 0 8px 24px -16px rgba(31,42,36,.22);
  --maxw:1120px;
}

*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0; background:var(--paper); color:var(--ink);
  font-family:var(--font-sans);
  font-size:15px; line-height:1.75;
  overflow-wrap:break-word; word-break:normal; line-break:auto;
}
a{color:var(--green)}
main{max-width:var(--maxw); margin:0 auto; padding:24px 20px 56px}
h1,h2,h3,h4{line-height:1.45; letter-spacing:.005em}

/* header — 流山データアトラス / 流山マップと同じ帯 */
.header{
  display:flex; align-items:center; gap:16px 24px; flex-wrap:wrap;
  padding:12px 24px; padding-top:max(12px, env(safe-area-inset-top));
  background:var(--green-deep); color:#f2f5ee;
}
.brand{
  font-family:var(--font-serif); font-size:clamp(16px,2.2vw,20px); font-weight:700;
  letter-spacing:.03em; color:#f2f5ee; text-decoration:none; flex:1 1 auto;
  min-width:0; overflow-wrap:normal; word-break:keep-all;
}
.brand small{
  display:block; font-family:var(--font-sans); font-size:10.5px; font-weight:400;
  letter-spacing:.18em; opacity:.78;
}
.nav{display:flex; gap:6px}
.nav-link{
  color:#dfe8dc; text-decoration:none; padding:6px 12px; border-radius:7px; font-size:13.5px;
}
.nav-link:hover{background:rgba(255,255,255,.12)}
.nav-link.active{background:rgba(255,255,255,.16); color:#fff; font-weight:700}

/* hero */
.hero{padding:56px 0 32px; max-width:900px}
.hero.narrow{max-width:760px}
.kicker{margin:0 0 12px; font-size:13px; letter-spacing:.14em; color:var(--green-deep); font-weight:700}
.hero h1{margin:0 0 20px; font-size:clamp(26px,4vw,36px); font-weight:700; letter-spacing:.02em;
  font-family:var(--font-serif); color:var(--green-deep)}
.lede{margin:0; color:var(--ink2); font-size:16px; max-width:42em}
.lede a{color:var(--accent)}

.stats{display:grid; grid-template-columns:repeat(auto-fit,minmax(min(180px,100%),1fr)); gap:1px; margin-top:36px;
  background:var(--line); border:1px solid var(--line); border-radius:12px; overflow:hidden}
.stat{background:var(--panel); padding:16px 18px}
.stat-v{font-size:19px; font-weight:700; letter-spacing:-.01em}
.stat-l{font-size:13px; color:var(--ink2); margin-top:2px}
.stat-n{font-size:11.5px; color:var(--ink3); line-height:1.6; margin-top:6px}

/* filters */
.filters{display:flex; flex-wrap:wrap; align-items:center; gap:12px 24px; padding:18px 0 22px;
  border-top:1px solid var(--line); border-bottom:1px solid var(--line); margin-top:8px}
.filter-row{display:flex; align-items:center; gap:10px; flex-wrap:wrap}
.filter-lbl{font-size:12px; color:var(--ink3); letter-spacing:.08em}
.chips{display:flex; flex-wrap:wrap; gap:6px}
.chip{font:inherit; font-size:12.5px; line-height:1.4; padding:4px 11px; border-radius:999px; cursor:pointer;
  border:1px solid var(--line); background:var(--panel); color:var(--ink2)}
.chip:hover{border-color:var(--ink3)}
.chip.on{background:var(--c,var(--accent)); border-color:var(--c,var(--accent)); color:#fff}
.filter-count{margin:0 0 0 auto; font-size:12.5px; color:var(--ink3)}

/* grid */
.grid{display:grid; grid-template-columns:repeat(auto-fill,minmax(min(330px,100%),1fr)); gap:14px; padding:28px 0}
.card{display:flex; flex-direction:column; background:var(--panel); border:1px solid var(--line);
  border-radius:14px; text-decoration:none; overflow:hidden; box-shadow:var(--shadow);
  transition:transform .14s ease, border-color .14s ease}
.card:hover{transform:translateY(-2px); border-color:var(--c)}
.card-head{display:flex; align-items:center; gap:10px; padding:12px 16px 0}
.card-id{font-size:11.5px; font-weight:700; letter-spacing:.1em; color:var(--c)}
.card-theme{font-size:11.5px; padding:2px 9px; border-radius:999px; color:var(--c);
  background:color-mix(in srgb, var(--c) 12%, transparent); border:1px solid color-mix(in srgb, var(--c) 30%, transparent)}
.card-theme.big{font-size:12.5px; padding:3px 12px; display:inline-block}
.card-body{display:flex; gap:14px; padding:12px 16px 14px; flex:1}
.card-ico{color:var(--c); flex:0 0 auto; opacity:.9}
.card h3{margin:0 0 8px; font-size:16.5px; font-weight:700; line-height:1.55}
.card-catch{margin:0; font-size:13px; color:var(--ink2); line-height:1.75}
.card-foot{display:flex; align-items:center; justify-content:space-between; gap:10px; flex-wrap:wrap;
  padding:10px 16px; border-top:1px solid var(--line2); background:color-mix(in srgb,var(--c) 4%, transparent)}
.badges{display:flex; gap:5px}
.badge{font-size:10.5px; color:var(--ink3); border:1px solid var(--line); border-radius:4px; padding:1px 6px}
.meters{display:flex; align-items:center; gap:6px}
.meter-lbl{font-size:10.5px; color:var(--ink3)}
.meter{display:inline-flex; gap:2.5px; align-items:center; margin-right:4px}
.meter .dot{width:6px; height:6px; border-radius:50%; background:var(--line); display:block}
.meter .dot.on{background:var(--c,var(--accent))}

/* backlog */
.backlog{padding-top:20px; border-top:1px solid var(--line)}
.backlog h2{font-size:18px; margin:24px 0 4px}
.sub{color:var(--ink2); font-size:13.5px; margin:0 0 16px; max-width:76ch}
.sub a{color:var(--accent)}
.backlog-list{list-style:none; padding:0; margin:0; display:grid; grid-template-columns:repeat(auto-fill,minmax(min(300px,100%),1fr)); gap:1px;
  background:var(--line); border:1px solid var(--line); border-radius:12px; overflow:hidden}
.backlog-list li{background:var(--panel); padding:14px 16px; display:flex; flex-direction:column; gap:5px}
.backlog-list strong{font-size:14px}
.backlog-list span{font-size:12.5px; color:var(--ink2); line-height:1.7}

/* issue page */
.crumbs{font-size:12.5px; color:var(--ink3); padding:24px 0 0}
.crumbs a{color:var(--ink2); text-decoration:none}
.crumbs a:hover{color:var(--accent)}
.crumbs span{margin:0 6px}
.issue{max-width:900px; margin:0 auto}
.issue-head{padding:18px 0 30px; border-bottom:1px solid var(--line)}
.issue-head h1{margin:14px 0 14px; font-size:clamp(22px,3.6vw,32px); font-weight:700; letter-spacing:.02em;
  font-family:var(--font-serif); color:var(--green-deep)}
.issue-catch{margin:0; font-size:15.5px; color:var(--ink2); max-width:40em;
  border-left:3px solid var(--c); padding-left:14px}
.issue-actions{margin:18px 0 0}
.gh-issue{
  display:inline-flex; align-items:center; justify-content:center;
  background:var(--green-deep); color:#f2f5ee; text-decoration:none;
  font-size:14px; font-weight:700; padding:10px 16px; border-radius:8px;
  line-height:1.4;
}
.gh-issue:hover{background:var(--green); color:#fff}
.block.report .sub{margin-bottom:14px}
.block{padding:38px 0; border-bottom:1px solid var(--line2)}
.block:last-of-type{border-bottom:none}
.block h2{display:flex; align-items:center; gap:10px; margin:0 0 18px; font-size:18px; font-weight:700}
.block h2 .n{display:inline-flex; align-items:center; justify-content:center; width:24px; height:24px;
  border-radius:6px; background:var(--c,var(--accent)); color:#fff; font-size:12px; font-weight:700; flex:0 0 auto}
.block h4{margin:22px 0 8px; font-size:13.5px; color:var(--ink2)}
.block.two{display:grid; grid-template-columns:1fr 1fr; gap:40px}
@media(max-width:760px){.block.two{grid-template-columns:1fr; gap:8px}}

.persona{display:flex; gap:16px; align-items:flex-start; background:var(--panel);
  border:1px solid var(--line); border-radius:12px; padding:18px 20px}
.persona-ico{color:var(--c); flex:0 0 auto}
.persona-label{font-weight:700; font-size:14.5px; margin-bottom:4px}
.persona p{margin:0; font-size:14px; color:var(--ink2)}
.pain{display:grid; grid-template-columns:1fr 1fr; gap:1px; margin:14px 0 0;
  background:var(--line); border:1px solid var(--line); border-radius:12px; overflow:hidden}
.pain>div{background:var(--panel); padding:14px 16px; min-width:0}
.pain dt{font-size:11.5px; letter-spacing:.08em; color:var(--c); font-weight:700; margin-bottom:4px}
.pain dd{margin:0; font-size:13.5px; color:var(--ink2); line-height:1.8}
@media(max-width:700px){.pain{grid-template-columns:1fr}}

/* scene svg */
.scene-wrap{background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:16px; overflow-x:auto; -webkit-overflow-scrolling:touch}
.scene{width:100%; min-width:640px; height:auto; display:block}
.scene{--sc:var(--c,var(--accent))}
.scene .pnl-bg{fill:color-mix(in srgb, var(--sc) 5%, var(--panel)); stroke:var(--line)}
.scene .pnl-wall .pnl-bg{fill:color-mix(in srgb, var(--sc) 10%, var(--panel)); stroke:color-mix(in srgb,var(--sc) 35%,transparent); stroke-dasharray:5 4}
.scene .pnl-tab{fill:var(--sc); opacity:.92}
.scene .pnl-tablabel{fill:#fff; font-size:12.5px; font-weight:700;
  font-family:"Hiragino Kaku Gothic ProN","Noto Sans JP",system-ui,sans-serif}
.scene .pnl-icon{color:var(--sc)}
.scene .pnl-icon use{stroke:currentColor; fill:none}
.scene .pnl-text{fill:var(--ink2); font-size:13.5px;
  font-family:"Hiragino Kaku Gothic ProN","Noto Sans JP",system-ui,sans-serif}
.scene .arrow path{stroke:var(--ink3); stroke-width:2; fill:none; stroke-linecap:round; stroke-linejoin:round}

/* stories */
.stories{list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:10px}
.story{display:grid; grid-template-columns:1fr 1fr 1fr; gap:1px; background:var(--line);
  border:1px solid var(--line); border-radius:12px; overflow:hidden}
@media(max-width:760px){.story{grid-template-columns:1fr}}
.story-part{background:var(--panel); padding:13px 16px; font-size:13.5px; color:var(--ink); line-height:1.75}
.story-k{display:block; font-size:11px; letter-spacing:.09em; color:var(--c); font-weight:700; margin-bottom:3px}

/* evidence */
.evidence{display:grid; grid-template-columns:repeat(auto-fit,minmax(min(280px,100%),1fr)); gap:18px}
.ev-col h3{display:flex; align-items:center; gap:8px; margin:0 0 10px; font-size:13.5px; font-weight:700; color:var(--ink2)}
.ev-tag{font-size:10.5px; padding:2px 8px; border-radius:999px; color:#fff; letter-spacing:.04em}
.t-od{background:#0e7490}.t-council{background:#7c3aed}.t-voice{background:#b45309}
.ev-list{list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:8px}
.ev-list li{background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:11px 13px}
.ev-name{font-size:13px; font-weight:700; line-height:1.6}
.ev-yr{font-weight:400; font-size:11.5px; color:var(--ink3); margin-left:4px}
.ev-cat{font-size:11px; color:var(--ink3); margin-top:2px}
.ev-fact{font-size:12.5px; color:var(--ink2); margin-top:6px; line-height:1.75}
.voices{list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:8px}
.voices li{background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:11px 13px}
.voices blockquote{margin:0; font-size:12.5px; line-height:1.8; color:var(--ink); position:relative; padding-left:12px;
  border-left:2px solid color-mix(in srgb,var(--c) 45%, transparent)}
.voices cite{display:block; margin-top:6px; font-size:11px; color:var(--ink3); font-style:normal}

/* flow */
.flow{display:flex; align-items:stretch; gap:10px; flex-wrap:wrap}
.flow-step{flex:1 1 220px; background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:13px 15px}
.flow-lbl{font-size:11px; letter-spacing:.09em; color:var(--c); font-weight:700; margin-bottom:8px}
.flow-chips{display:flex; flex-wrap:wrap; gap:5px}
.flow-chip{font-size:11.5px; border:1px solid var(--line); border-radius:5px; padding:2px 7px; color:var(--ink2); line-height:1.6}
.flow-form{font-size:14px; font-weight:700}
.flow-who{font-size:12.5px; color:var(--ink2); line-height:1.75}
.flow-arrow{display:flex; align-items:center; color:var(--ink3); font-size:18px}
@media(max-width:760px){.flow-arrow{transform:rotate(90deg); justify-content:center; width:100%}}
.features{margin:18px 0 0; padding-left:20px; font-size:13.5px; color:var(--ink2)}
.features li{margin:6px 0; line-height:1.8}

.kpi,.missing{margin:0; padding-left:20px; font-size:13.5px; color:var(--ink2)}
.kpi li,.missing li{margin:7px 0; line-height:1.8}
.feas{display:flex; flex-direction:column; gap:8px; background:var(--panel); border:1px solid var(--line);
  border-radius:10px; padding:13px 15px}
.feas-row{display:flex; align-items:center; gap:10px; font-size:13px}
.feas-row>span:first-child{width:88px; color:var(--ink2); font-size:12.5px}
.feas-row em{font-style:normal; color:var(--ink3); font-size:12px}
.feas-row .meter .dot{width:9px; height:9px}

.prevnext{display:grid; grid-template-columns:1fr 1fr; gap:12px; padding:32px 0 0; border-top:1px solid var(--line)}
.pn{display:block; text-decoration:none; background:var(--panel); border:1px solid var(--line);
  border-radius:12px; padding:13px 16px; font-size:13.5px; line-height:1.6}
.pn:hover{border-color:var(--accent)}
.pn span{display:block; font-size:11px; color:var(--ink3); letter-spacing:.08em; margin-bottom:3px}
.pn.next{text-align:right}
@media(max-width:600px){.prevnext{grid-template-columns:1fr}.pn.next{text-align:left}}

/* tables & misc */
.tpl{width:100%; border-collapse:collapse; font-size:13.5px; background:var(--panel);
  border:1px solid var(--line); border-radius:12px; overflow:hidden; display:table}
.tpl th,.tpl td{text-align:left; padding:11px 14px; border-bottom:1px solid var(--line2); vertical-align:top}
.tpl thead th{font-size:11.5px; letter-spacing:.07em; color:var(--ink3); background:color-mix(in srgb,var(--accent) 5%,transparent)}
.tpl tbody tr:last-child td{border-bottom:none}
.tpl td.num,.tpl th.num{text-align:right; font-variant-numeric:tabular-nums}
.tn{color:var(--accent); font-weight:700; width:28px}
.tname{font-weight:700; white-space:nowrap}
.tkey code{font-size:11.5px}
code{background:var(--code); border-radius:4px; padding:1px 5px; font-size:12.5px;
  font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.code{background:var(--code); border:1px solid var(--line); border-radius:10px; padding:14px 16px;
  overflow-x:auto; font-size:12px; line-height:1.7; color:var(--ink2);
  font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.iconset{display:flex; flex-wrap:wrap; gap:6px; margin-top:18px}
.ic{display:inline-flex; align-items:center; gap:6px; border:1px solid var(--line); border-radius:8px;
  padding:5px 9px; background:var(--panel); color:var(--accent)}
.ic .lbl{color:var(--ink3); font-size:11.5px; padding:0; white-space:nowrap}
.usedlist{list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:1px;
  background:var(--line); border:1px solid var(--line); border-radius:12px; overflow:hidden}
.usedlist li{background:var(--panel); padding:10px 14px; display:flex; align-items:center; gap:8px; flex-wrap:wrap; font-size:13px}
.ds{flex:1 1 auto}
.pill{font-size:11px; text-decoration:none; border:1px solid var(--line); border-radius:999px;
  padding:1px 9px; color:var(--ink2)}
.pill:hover{border-color:var(--accent); color:var(--accent)}
.notes{list-style:disc; padding-left:20px}
.notes li{margin:6px 0}

.foot{
  border-top:1px solid var(--line);
  padding:16px 20px calc(16px + env(safe-area-inset-bottom));
  color:var(--dim); font-size:12px; line-height:1.85; text-align:center;
}
.foot p{margin:0 0 6px}
.foot a{color:var(--green)}
@media(max-width:700px){
  .header{padding:10px 14px; padding-top:max(10px, env(safe-area-inset-top)); gap:8px 12px}
  .brand{font-size:16px; flex-basis:100%; letter-spacing:.02em}
  .brand small{letter-spacing:.08em; font-size:10px}
  .nav{flex:1 1 auto; flex-wrap:wrap; width:100%}
  .nav-link{padding:8px 10px; font-size:12.5px}
  main{padding:18px 14px 44px}
  .hero{padding:28px 0 20px}
  .hero h1,.issue-head h1{font-size:1.45rem; letter-spacing:.01em}
  .lede,.issue-catch,.sub{max-width:none; font-size:15px}
  .pain{grid-template-columns:1fr}
  .story{grid-template-columns:1fr}
  .block.two{grid-template-columns:1fr; gap:8px}
  .tname{white-space:normal}
  .tpl th,.tpl td{padding:10px}
  .feas-row{flex-wrap:wrap}
  .feas-row>span:first-child{width:auto}
  .scene-wrap{margin-inline:-14px; padding:12px 14px; border-radius:0; border-left:none; border-right:none}
  .card-foot{align-items:flex-start}
  .gh-issue{width:100%; box-sizing:border-box}
  .filter-count{margin-left:0}
}
"""

JS = """
(function(){
  var grid = document.getElementById('grid');
  if(!grid) return;
  var cards = Array.prototype.slice.call(grid.querySelectorAll('.card'));
  var count = document.getElementById('count');
  var active = new Set();
  var sort = 'id';

  function apply(){
    var shown = 0;
    cards.forEach(function(c){
      var ok = active.size === 0 || active.has(c.dataset.theme);
      c.style.display = ok ? '' : 'none';
      if(ok) shown++;
    });
    if(count) count.textContent = shown;
    var key = {
      id:   function(c){ return parseInt(c.querySelector('.card-id').textContent.replace('N-',''),10); },
      data: function(c){ return -parseInt(c.dataset.data,10); },
      easy: function(c){ return parseInt(c.dataset.diff,10); }
    }[sort];
    cards.slice().sort(function(a,b){
      var d = key(a) - key(b);
      return d !== 0 ? d : a.querySelector('.card-id').textContent.localeCompare(b.querySelector('.card-id').textContent);
    }).forEach(function(c){ grid.appendChild(c); });
  }

  document.querySelectorAll('.chip[data-theme]').forEach(function(b){
    b.addEventListener('click', function(){
      var t = b.dataset.theme;
      if(active.has(t)){ active.delete(t); b.classList.remove('on'); }
      else { active.add(t); b.classList.add('on'); }
      apply();
    });
  });
  document.querySelectorAll('.chip.sort').forEach(function(b){
    b.addEventListener('click', function(){
      document.querySelectorAll('.chip.sort').forEach(function(x){ x.classList.remove('on'); });
      b.classList.add('on');
      sort = b.dataset.sort;
      apply();
    });
  });
  apply();
})();
"""


def main():
    with open(DATA, encoding="utf-8") as fh:
        d = json.load(fh)

    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "assets"))
    os.makedirs(os.path.join(OUT, "issues"))

    with open(os.path.join(OUT, ".nojekyll"), "w", encoding="utf-8") as fh:
        fh.write("")
    with open(os.path.join(OUT, "assets", "site.css"), "w", encoding="utf-8") as fh:
        fh.write(CSS)
    with open(os.path.join(OUT, "assets", "site.js"), "w", encoding="utf-8") as fh:
        fh.write(JS)

    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(render_index(d))
    with open(os.path.join(OUT, "template.html"), "w", encoding="utf-8") as fh:
        fh.write(render_template_page(d))
    with open(os.path.join(OUT, "sources.html"), "w", encoding="utf-8") as fh:
        fh.write(render_sources(d))

    issues = d["issues"]
    for i, it in enumerate(issues):
        prev_it = issues[i - 1] if i > 0 else None
        next_it = issues[i + 1] if i < len(issues) - 1 else None
        with open(os.path.join(OUT, "issues", it["slug"] + ".html"), "w", encoding="utf-8") as fh:
            fh.write(render_issue(it, prev_it, next_it))

    # 課題データそのものも配信する（他の人が再利用できるように）
    shutil.copy(DATA, os.path.join(OUT, "issues.json"))
    shutil.copy(os.path.join(ROOT, "schema", "issue.schema.json"), os.path.join(OUT, "issue.schema.json"))

    print("built %d issue pages + 3 pages -> docs/" % len(issues))


if __name__ == "__main__":
    main()
