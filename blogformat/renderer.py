from __future__ import annotations
import html as html_lib
import re
from .themes import Theme
from .parser import Post, Section, CIRCLED


def inline_format(text: str, theme: Theme) -> str:
    s = html_lib.escape(text, quote=False)
    s = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{m.group(2)}" style="color:{theme.primary};text-decoration:underline;">{m.group(1)}</a>',
        s,
    )
    s = re.sub(
        r"\*\*(.+?)\*\*",
        lambda m: f'<strong style="color:{theme.primary};font-weight:700;">{m.group(1)}</strong>',
        s,
    )
    s = re.sub(
        r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)",
        lambda m: f'<em>{m.group(1)}</em>',
        s,
    )
    s = re.sub(
        r"`([^`]+)`",
        lambda m: (
            f'<code style="background:{theme.warm};padding:1px 6px;border-radius:3px;'
            f'font-family:ui-monospace,Menlo,Consolas,monospace;font-size:0.85em;">{m.group(1)}</code>'
        ),
        s,
    )
    return s


def render(post: Post, theme: Theme) -> str:
    out = [f'<!-- bt:{theme.key} -->']
    out.append(render_header(post, theme))

    body_open = (
        f'<div style="max-width:820px;margin:0 auto;padding:0 24px 80px;'
        f'background:{theme.bg};'
        f'font-family:\'Lato\',sans-serif;font-weight:300;font-size:16px;'
        f'line-height:1.75;color:{theme.body_text};">'
    )
    out.append(body_open)

    named_sections = [s for s in post.sections if s.heading]
    if len(named_sections) >= 3:
        out.append(render_toc(named_sections, theme))

    for section in post.sections:
        out.append(render_section(section, theme))

    out.append("</div>")
    out.append(render_footer(post, theme))
    return "\n".join(out)


def render_header(post: Post, theme: Theme) -> str:
    parts = [
        f'<header style="background:{theme.primary};text-align:center;'
        f'padding:64px 24px 56px;color:#ffffff;">'
    ]
    parts.append(
        f'<div style="color:{theme.accent};font-family:\'Lato\',sans-serif;'
        f'font-weight:700;font-size:0.75rem;letter-spacing:0.25em;'
        f'text-transform:uppercase;margin-bottom:18px;">'
        f'{html_lib.escape(post.eyebrow)}</div>'
    )
    parts.append(
        f'<h1 style="font-family:\'Playfair Display\',serif;font-weight:700;'
        f'font-size:2.8rem;line-height:1.15;color:#ffffff;margin:0 0 14px 0;">'
        f'{html_lib.escape(post.title)}</h1>'
    )
    if post.subtitle:
        parts.append(
            f'<h2 style="font-family:\'Playfair Display\',serif;font-weight:400;'
            f'font-style:italic;font-size:1.25rem;color:{theme.accent_light};'
            f'margin:0;line-height:1.4;">'
            f'{html_lib.escape(post.subtitle)}</h2>'
        )
    if post.stats:
        parts.append(
            f'<div style="width:60px;height:1px;background:{theme.accent};'
            f'margin:36px auto 28px;"></div>'
        )
        parts.append(
            '<div style="display:flex;flex-wrap:wrap;justify-content:center;'
            'gap:48px;margin-top:8px;">'
        )
        for number, label in post.stats:
            parts.append(
                '<div style="text-align:center;">'
                f'<div style="font-family:\'Playfair Display\',serif;font-weight:700;'
                f'font-size:1.75rem;color:{theme.accent};line-height:1;">'
                f'{html_lib.escape(number)}</div>'
                f'<div style="font-family:\'Lato\',sans-serif;font-weight:700;'
                f'font-size:0.68rem;letter-spacing:0.2em;text-transform:uppercase;'
                f'color:{theme.accent_light};margin-top:8px;">'
                f'{html_lib.escape(label)}</div>'
                '</div>'
            )
        parts.append('</div>')
    parts.append('</header>')
    return "".join(parts)


def render_toc(sections: list[Section], theme: Theme) -> str:
    parts = [
        f'<nav style="background:{theme.primary};border-radius:4px;'
        f'padding:36px 40px;margin:48px 0 56px;">'
    ]
    parts.append(
        f'<div style="color:{theme.accent};font-family:\'Lato\',sans-serif;'
        f'font-weight:700;font-size:0.72rem;letter-spacing:0.25em;'
        f'text-transform:uppercase;margin-bottom:20px;">Table of Contents</div>'
    )
    parts.append(
        '<ul style="list-style:none;padding:0;margin:0;display:grid;'
        'grid-template-columns:repeat(auto-fill, minmax(220px, 1fr));'
        'gap:10px 24px;">'
    )
    for idx, sec in enumerate(sections):
        marker = CIRCLED[idx] if idx < len(CIRCLED) else f"{idx+1}."
        parts.append(
            '<li style="color:rgba(255,255,255,0.8);font-family:\'Lato\',sans-serif;'
            'font-weight:300;font-size:0.95rem;line-height:1.5;">'
            f'<span style="color:{theme.accent};margin-right:10px;font-weight:700;">{marker}</span>'
            f'{html_lib.escape(sec.heading)}'
            '</li>'
        )
    parts.append('</ul></nav>')
    return "".join(parts)


def render_section(section: Section, theme: Theme) -> str:
    parts = ['<section style="margin:48px 0;">']
    if section.heading:
        if section.label:
            parts.append(
                f'<div style="color:{theme.accent};font-family:\'Lato\',sans-serif;'
                f'font-weight:700;font-size:0.72rem;letter-spacing:0.25em;'
                f'text-transform:uppercase;margin-bottom:10px;">'
                f'{html_lib.escape(section.label)}</div>'
            )
        parts.append(
            f'<h2 style="font-family:\'Playfair Display\',serif;font-weight:700;'
            f'font-size:1.75rem;color:{theme.primary};margin:0 0 24px 0;'
            f'padding-bottom:14px;border-bottom:1px solid {theme.border};'
            f'line-height:1.25;">'
            f'{html_lib.escape(section.heading)}</h2>'
        )
    for block in section.blocks:
        parts.append(render_block(block, theme))
    parts.append('</section>')
    return "".join(parts)


def render_block(block: dict, theme: Theme) -> str:
    btype = block["type"]

    if btype == "subheading":
        return (
            f'<div style="font-family:\'Lato\',sans-serif;font-weight:700;'
            f'font-size:0.7rem;letter-spacing:0.2em;text-transform:uppercase;'
            f'color:{theme.muted};margin:28px 0 6px 0;">'
            f'{html_lib.escape(block["text"])}</div>'
        )
    if btype == "paragraph":
        return (
            f'<p style="font-family:\'Lato\',sans-serif;font-weight:300;'
            f'font-size:0.97rem;color:{theme.body_text};line-height:1.75;'
            f'margin:0 0 16px 0;">'
            f'{inline_format(block["text"], theme)}</p>'
        )
    if btype == "callout":
        return (
            f'<div style="background:{theme.warm};'
            f'border-left:3px solid {theme.accent};'
            f'padding:14px 20px;margin:20px 0;border-radius:0 4px 4px 0;'
            f'font-family:\'Lato\',sans-serif;font-weight:400;font-style:italic;'
            f'font-size:0.88rem;color:{theme.muted};line-height:1.65;">'
            f'{inline_format(block["text"], theme)}</div>'
        )
    if btype == "list":
        return render_list(block["items"], theme)
    if btype == "table":
        return render_table(block["headers"], block["rows"], theme)
    if btype == "raw_html":
        return block["html"]
    return ""


def render_list(items: list, theme: Theme) -> str:
    parts = [
        '<ul style="list-style:none;padding:0;margin:20px 0;'
        f'border-top:1px solid {theme.border};">'
    ]
    last = len(items) - 1
    for idx, item in enumerate(items):
        border = f"border-bottom:1px solid {theme.border};" if idx != last else ""
        name_html = ""
        if item["name"]:
            name_html = (
                f'<strong style="color:{theme.primary};font-weight:700;'
                f'font-family:\'Lato\',sans-serif;">'
                f'{inline_format(item["name"], theme).replace("<strong", "<span").replace("</strong>", "</span>")}'
                f'</strong>'
                + (" — " if item["desc"] else "")
            )
        desc_html = inline_format(item["desc"], theme) if item["desc"] else ""
        parts.append(
            f'<li style="display:flex;gap:14px;padding:9px 0;{border}'
            f'font-family:\'Lato\',sans-serif;font-weight:300;'
            f'font-size:0.97rem;color:{theme.body_text};line-height:1.65;">'
            f'<span style="color:{theme.accent};font-weight:700;flex-shrink:0;">→</span>'
            f'<span>{name_html}{desc_html}</span>'
            '</li>'
        )
    parts.append('</ul>')
    return "".join(parts)


def render_table(headers: list, rows: list, theme: Theme) -> str:
    parts = [
        f'<div style="overflow-x:auto;border:1px solid {theme.border};'
        f'border-radius:6px;margin:24px 0;">'
        '<table style="width:100%;border-collapse:collapse;'
        'font-family:\'Lato\',sans-serif;font-size:0.95rem;">'
    ]
    parts.append(f'<thead><tr style="background:{theme.primary};">')
    for h in headers:
        parts.append(
            '<th style="color:#ffffff;font-family:\'Lato\',sans-serif;'
            'font-weight:700;font-size:0.7rem;letter-spacing:0.15em;'
            'text-transform:uppercase;text-align:left;padding:13px 18px;'
            f'vertical-align:top;">{inline_format(h, theme)}</th>'
        )
    parts.append('</tr></thead><tbody>')
    last_row = len(rows) - 1
    for r_idx, row in enumerate(rows):
        bg = "#ffffff" if r_idx % 2 == 0 else theme.warm
        border = f"border-bottom:1px solid {theme.border};" if r_idx != last_row else ""
        parts.append(f'<tr style="background:{bg};">')
        for c_idx, cell in enumerate(row):
            style = f"padding:13px 18px;vertical-align:top;line-height:1.5;{border}color:{theme.body_text};"
            if c_idx == 0:
                style += f"font-weight:700;color:{theme.primary};font-family:'Lato',sans-serif;"
            parts.append(f'<td style="{style}">{inline_format(cell, theme)}</td>')
        parts.append('</tr>')
    parts.append('</tbody></table></div>')
    return "".join(parts)


def render_footer(post: Post, theme: Theme) -> str:
    text = post.footer or "Thanks for reading — more posts at Blogname.com"
    return (
        f'<footer style="border-top:1px solid {theme.border};text-align:center;'
        f'padding:32px 24px 48px;font-family:\'Lato\',sans-serif;'
        f'font-weight:400;font-size:0.8rem;color:{theme.muted};'
        f'background:{theme.bg};">'
        f'{html_lib.escape(text)}</footer>'
    )
