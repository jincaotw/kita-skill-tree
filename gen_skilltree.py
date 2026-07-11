#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_skilltree.py — 把 catalog.json 產成一個「可嵌 Notion 的互動 HTML 技能樹」。

搭配 scan_skills.py 使用：
  scan_skills.py 掃 ~/.claude/skills 對照 catalog.json 抓漂移 → 人工補進 catalog.json
  gen_skilltree.py 把 catalog.json → index.html（自含 CSS/JS，可託管 GitHub Pages、可嵌 Notion）

用法：
  python3 gen_skilltree.py                 # 讀同目錄 catalog.json → 寫 index.html
  python3 gen_skilltree.py --catalog X.json --out Y.html

catalog.json 格式：
  { "_meta": {"title": str, "categories": {catKey: {"zh": str, "emoji": str}}},
    "skills": [ {"slug": str, "cat": catKey, "name": str, "desc": str}, ... ] }
"""
import json, os, sys, html, argparse, datetime

HERE = os.path.dirname(os.path.abspath(__file__))

def esc(s): return html.escape(str(s or ""))

def hex_rgb(h):
    """#rrggbb -> (r,g,b)；壞值回傳 None。"""
    h = (h or "").lstrip("#")
    if len(h) != 6:
        return None
    try:
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        return None

def build_html(cat):
    meta = cat.get("_meta", {})
    title = meta.get("title", "技能樹")
    cats = meta.get("categories", {})
    skills = cat.get("skills", [])
    # 依 catalog 裡 categories 的順序分組
    order = list(cats.keys())
    groups = {k: [] for k in order}
    for s in skills:
        groups.setdefault(s.get("cat", "其他"), []).append(s)

    today = datetime.date.today().isoformat()
    cards_html = []
    for k in order:
        items = groups.get(k, [])
        if not items:
            continue
        c = cats.get(k, {})
        emoji = c.get("emoji", "•"); zh = c.get("zh", k); color = c.get("color", "")
        rgb = hex_rgb(color)
        h2style = f' style="color:{esc(color)};border-bottom-color:{esc(color)}"' if color else ""
        # 每張卡：依所屬分類的顏色淡淡上底色＋邊框＋左側色條
        if rgb:
            r, g, b = rgb
            cardstyle = (f' style="background:rgba({r},{g},{b},0.08);'
                         f'border-color:rgba({r},{g},{b},0.35);'
                         f'border-left:3px solid rgba({r},{g},{b},0.85)"')
            cmdstyle = f' style="color:rgba({r},{g},{b},1)"'
        else:
            cardstyle = cmdstyle = ""
        cards_html.append(f'<section class="grp"><h2{h2style}>{esc(emoji)} {esc(zh)} '
                          f'<span class="cnt">{len(items)}</span></h2><div class="cards">')
        for s in items:
            slug = esc(s.get("slug", "")); name = esc(s.get("name", "")); desc = esc(s.get("desc", ""))
            search = esc((s.get("slug","")+" "+s.get("name","")+" "+s.get("desc","")).lower())
            cards_html.append(
                f'<div class="card" data-s="{search}"{cardstyle}>'
                f'<div class="cmd"{cmdstyle}>/{slug}</div><div class="nm">{name}</div>'
                f'<div class="ds">{desc}</div></div>')
        cards_html.append('</div></section>')

    return f"""<!doctype html>
<html lang="zh-Hant"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{esc(title)}</title>
<style>
:root{{--bg:#0f1115;--card:#1a1d24;--bd:#2a2f3a;--tx:#e6e8ee;--sub:#98a0b0;--ac:#5b8cff;--cmd:#7dd3fc}}
@media(prefers-color-scheme:light){{:root{{--bg:#f6f7f9;--card:#fff;--bd:#e3e6ea;--tx:#1a1d24;--sub:#6b7280;--ac:#2563eb;--cmd:#0369a1}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--tx);
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans","PingFang TC","Noto Sans TC",sans-serif;padding:20px}}
.hd{{max-width:1000px;margin:0 auto 16px}}.hd h1{{font-size:22px;margin:0 0 10px}}
#q{{width:100%;max-width:1000px;display:block;margin:0 auto 20px;padding:10px 14px;border-radius:10px;
border:1px solid var(--bd);background:var(--card);color:var(--tx);font-size:15px}}
.wrap{{max-width:1000px;margin:0 auto}}
.grp{{margin:0 0 22px}}.grp h2{{font-size:15px;color:var(--sub);border-bottom:1px solid var(--bd);
padding-bottom:6px;margin:0 0 12px;font-weight:600}}.cnt{{font-size:12px;opacity:.6}}
.cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px}}
.card{{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:12px 14px}}
.cmd{{font-family:ui-monospace,Menlo,monospace;font-size:12px;color:var(--cmd);margin-bottom:4px}}
.nm{{font-weight:600;font-size:14px;margin-bottom:4px}}.ds{{font-size:12.5px;color:var(--sub);line-height:1.5}}
.ft{{max-width:1000px;margin:24px auto 0;color:var(--sub);font-size:12px;text-align:center}}
.hide{{display:none}}
</style></head><body>
<div class="hd"><h1>{esc(title)}</h1></div>
<input id="q" placeholder="🔍 Tìm skill / 搜尋技能…（gõ tên hoặc mô tả）">
<div class="wrap">{''.join(cards_html)}</div>
<div class="ft">Cập nhật / 更新：{today}　·　{len(skills)} skills</div>
<script>
const q=document.getElementById('q');
q.addEventListener('input',()=>{{const v=q.value.trim().toLowerCase();
document.querySelectorAll('.card').forEach(c=>{{c.classList.toggle('hide',v&&!c.dataset.s.includes(v))}});
document.querySelectorAll('.grp').forEach(g=>{{const any=[...g.querySelectorAll('.card')].some(c=>!c.classList.contains('hide'));g.classList.toggle('hide',!any)}});
}});
</script></body></html>"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", default=os.path.join(HERE, "catalog.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "index.html"))
    a = ap.parse_args()
    cat = json.load(open(a.catalog, encoding="utf-8"))
    out = build_html(cat)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"✅ 產出 {a.out}（{len(cat.get('skills',[]))} skills, {len(out)} bytes）")

if __name__ == "__main__":
    main()
