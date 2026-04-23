from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Optional


CIRCLED = ["①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩",
           "⑪", "⑫", "⑬", "⑭", "⑮", "⑯", "⑰", "⑱", "⑲", "⑳"]
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
         "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX"]


@dataclass
class Section:
    label: str
    heading: str
    blocks: list


@dataclass
class Post:
    title: str = "Untitled Post"
    subtitle: Optional[str] = None
    eyebrow: str = "Feature"
    stats: list = None
    sections: list = None
    footer: Optional[str] = None

    def __post_init__(self):
        if self.stats is None:
            self.stats = []
        if self.sections is None:
            self.sections = []


def parse_input(text: str) -> Post:
    lines = text.splitlines()
    post = Post()

    meta_keys = {"TITLE", "SUBTITLE", "EYEBROW", "STATS", "FOOTER"}
    filtered: list[str] = []
    for line in lines:
        stripped = line.strip()
        m = re.match(r"^([A-Z]+)\s*:\s*(.*)$", stripped)
        if m and m.group(1) in meta_keys:
            key, val = m.group(1), m.group(2).strip()
            if key == "TITLE":
                post.title = val
            elif key == "SUBTITLE":
                post.subtitle = val
            elif key == "EYEBROW":
                post.eyebrow = val
            elif key == "STATS":
                post.stats = parse_stats(val)
            elif key == "FOOTER":
                post.footer = val
            continue
        filtered.append(line)

    body = filtered
    current_section: Optional[Section] = None
    current_label: Optional[str] = None
    buffer: list[str] = []
    section_count = 0

    def flush_buffer_into(section: Optional[Section]):
        if section is None or not buffer:
            buffer.clear()
            return
        section.blocks.extend(parse_blocks(buffer))
        buffer.clear()

    preamble_section = Section(label="", heading="", blocks=[])
    current_section = preamble_section

    idx = 0
    while idx < len(body):
        line = body[idx]
        stripped = line.strip()

        m_label = re.match(r"^LABEL\s*:\s*(.*)$", stripped)
        if m_label:
            current_label = m_label.group(1).strip()
            idx += 1
            continue

        if stripped.startswith("# ") and not stripped.startswith("## "):
            flush_buffer_into(current_section)
            if current_section is preamble_section and current_section.blocks:
                post.sections.append(current_section)
            elif current_section is not preamble_section:
                post.sections.append(current_section)

            section_count += 1
            heading = stripped[2:].strip()
            label = current_label or f"Section {ROMAN[min(section_count - 1, len(ROMAN) - 1)]}"
            current_label = None
            current_section = Section(label=label, heading=heading, blocks=[])
            idx += 1
            continue

        buffer.append(line)
        idx += 1

    flush_buffer_into(current_section)
    if current_section is preamble_section:
        if current_section.blocks:
            post.sections.append(current_section)
    else:
        post.sections.append(current_section)

    return post


def parse_stats(s: str) -> list:
    out = []
    for chunk in s.split("|"):
        chunk = chunk.strip()
        if not chunk:
            continue
        m = re.match(r"^(\S+)\s+(.+)$", chunk)
        if m:
            out.append((m.group(1).strip(), m.group(2).strip()))
        else:
            out.append((chunk, ""))
    return out


def parse_blocks(lines: list[str]) -> list:
    blocks = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("## "):
            blocks.append({"type": "subheading", "text": stripped[3:].strip()})
            i += 1
            continue

        if stripped.startswith(">"):
            chunks = []
            while i < n and lines[i].strip().startswith(">"):
                chunks.append(lines[i].strip().lstrip(">").strip())
                i += 1
            blocks.append({"type": "callout", "text": " ".join(c for c in chunks if c)})
            continue

        if stripped.startswith("|") and i + 1 < n and re.match(r"^\s*\|[\s\-:|]+\|\s*$", lines[i + 1]):
            headers = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                rows.append(row)
                i += 1
            blocks.append({"type": "table", "headers": headers, "rows": rows})
            continue

        if stripped.startswith("- ") or stripped.startswith("* "):
            items = []
            while i < n and (lines[i].strip().startswith("- ") or lines[i].strip().startswith("* ")):
                raw = lines[i].strip()[2:].strip()
                items.append(parse_list_item(raw))
                i += 1
            blocks.append({"type": "list", "items": items})
            continue

        if stripped.startswith("<") and stripped.endswith(">") and len(stripped) > 20:
            blocks.append({"type": "raw_html", "html": stripped})
            i += 1
            continue

        para_lines = [stripped]
        i += 1
        while i < n:
            nxt = lines[i].strip()
            if not nxt:
                break
            if (nxt.startswith("## ") or nxt.startswith("- ") or nxt.startswith("* ")
                    or nxt.startswith(">") or nxt.startswith("|")):
                break
            para_lines.append(nxt)
            i += 1
        blocks.append({"type": "paragraph", "text": " ".join(para_lines)})

    return blocks


def parse_list_item(raw: str) -> dict:
    m = re.match(r"^\*\*(.+?)\*\*\s*[—–\-:,]\s*(.+)$", raw)
    if m:
        return {"name": m.group(1).strip(), "desc": m.group(2).strip()}
    m = re.match(r"^\*\*(.+?)\*\*\s*(.*)$", raw)
    if m:
        return {"name": m.group(1).strip(), "desc": m.group(2).strip()}
    return {"name": None, "desc": raw}
