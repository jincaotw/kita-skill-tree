# 🌳 kita-skill-tree

Cây kỹ năng AI (Claude Code skills) của Kita — danh mục các skill cá nhân, có màu theo nhóm, tìm kiếm nhanh.

**Xem online:** https://jincaotw.github.io/kita-skill-tree/

## File
- `catalog.json` — danh mục skill (tên + mô tả tiếng Việt, phân nhóm + màu)
- `gen_skilltree.py` — sinh `index.html` từ `catalog.json`
- `scan_skills.py` — quét `~/.claude/skills`, đối chiếu với catalog, báo skill mới/bị xoá
- `index.html` — cây kỹ năng tương tác (tự chứa, nhúng Notion / GitHub Pages được)

## Cập nhật
```bash
python3 scan_skills.py      # xem skill nào lệch với catalog
# sửa tay catalog.json cho khớp
python3 gen_skilltree.py    # sinh lại index.html
```
