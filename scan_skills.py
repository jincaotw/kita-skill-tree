#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能樹掃描器 —— 對照本機實際安裝的 skill 與 catalog.json，抓出漂移。

用法:
  python3 scan_skills.py           # 印出對照摘要（新增 / 移除 / 一致）
  python3 scan_skills.py --md      # 依分類印出 Markdown（可貼進 Notion）
  python3 scan_skills.py --json    # 印出 catalog 的 flat JSON

設計：catalog.json 是「顯示用」的策展目錄（中文名稱＋說明），
      本掃描器負責偵測 ~/.claude/skills 裡有沒有 catalog 沒收錄的新 skill、
      或 catalog 有但已被移除的 skill。發現漂移時，人工補進 catalog.json 再重生技能樹。
"""
import json, os, sys, glob

HOME = os.path.expanduser("~")
SKILLS_DIR = os.path.join(HOME, ".claude", "skills")
HERE = os.path.dirname(os.path.abspath(__file__))
CATALOG = os.path.join(HERE, "catalog.json")

# 不是真正 skill 的資料夾/檔案（掃描時略過）
IGNORE = {"README.md", ".DS_Store"}


def parse_frontmatter(path):
    """從 SKILL.md 取出 name 與 description（簡易 YAML，夠用）。"""
    name = desc = ""
    try:
        with open(path, encoding="utf-8") as f:
            txt = f.read()
    except OSError:
        return name, desc
    if not txt.startswith("---"):
        return name, desc
    fm = txt.split("---", 2)
    if len(fm) < 3:
        return name, desc
    body = fm[1]
    key = None
    buf = []
    for line in body.splitlines():
        if line.startswith("name:"):
            name = line.split(":", 1)[1].strip().strip("'\"")
            key = None
        elif line.startswith("description:"):
            val = line.split(":", 1)[1].strip()
            key = "desc"; buf = [val]
        elif key == "desc" and (line.startswith("  ") or line.strip() == ""):
            buf.append(line.strip())
        else:
            key = None
    if buf:
        desc = " ".join(x for x in buf if x).strip().strip("'\"")
    return name, desc


def installed_slugs():
    slugs = []
    for p in sorted(glob.glob(os.path.join(SKILLS_DIR, "*"))):
        base = os.path.basename(p)
        if base in IGNORE:
            continue
        if os.path.isdir(p) and os.path.exists(os.path.join(p, "SKILL.md")):
            slugs.append(base)
    return slugs


def load_catalog():
    with open(CATALOG, encoding="utf-8") as f:
        return json.load(f)


def main():
    cat = load_catalog()
    cat_slugs = [s["slug"] for s in cat["skills"]]
    inst = installed_slugs()
    cat_set, inst_set = set(cat_slugs), set(inst)

    new = sorted(inst_set - cat_set)       # 裝了但 catalog 沒收
    gone = sorted(cat_set - inst_set)      # catalog 有但已移除

    arg = sys.argv[1] if len(sys.argv) > 1 else ""

    if arg == "--json":
        print(json.dumps(cat["skills"], ensure_ascii=False, indent=2))
        return

    if arg == "--md":
        cats = cat["_meta"]["categories"]
        by = {}
        for s in cat["skills"]:
            by.setdefault(s["cat"], []).append(s)
        print(f"# {cat['_meta']['title']}\n")
        for cid, meta in cats.items():
            items = by.get(cid, [])
            if not items:
                continue
            print(f"## {meta['emoji']} {meta['zh']}（{len(items)}）\n")
            for s in items:
                print(f"- **`/{s['slug']}`** — {s['name']}：{s['desc']}")
            print()
        return

    # 預設：對照摘要
    print(f"📁 已安裝個人 skill：{len(inst)}")
    print(f"📗 catalog 收錄：{len(cat_slugs)}")
    print("-" * 44)
    if not new and not gone:
        print("✅ 完全一致，技能樹是最新的。")
    if new:
        print(f"🆕 裝了但 catalog 沒收（{len(new)}）—— 補進 catalog.json：")
        for slug in new:
            nm, ds = parse_frontmatter(os.path.join(SKILLS_DIR, slug, "SKILL.md"))
            print(f"   + /{slug}  «{nm or slug}»")
            if ds:
                print(f"       {ds[:80]}{'…' if len(ds) > 80 else ''}")
    if gone:
        print(f"🗑  catalog 有但已移除（{len(gone)}）—— 從 catalog.json 刪掉：")
        for slug in gone:
            print(f"   - /{slug}")


if __name__ == "__main__":
    main()
