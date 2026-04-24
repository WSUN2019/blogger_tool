"""HTML → plain-text conversion helpers used by the formatter and bulk reformat."""
import re
from bs4 import BeautifulSoup


def _is_html(text: str) -> bool:
    return bool(re.search(r'<(div|p|header|section|span|ul|li|table|h[1-6])\b', text, re.I))


def _make_img_grid(img_links: list) -> str:
    parts = []
    for a in img_links:
        href = a.get('href', '#')
        img_tag = a.find('img')
        if not img_tag:
            continue
        src = img_tag.get('src', '')
        parts.append(
            f'<a href="{href}" style="display:block;flex-shrink:0;border-radius:5px;overflow:hidden;line-height:0;">'
            f'<img src="{src}" style="height:180px;width:auto;display:block;" /></a>'
        )
    if not parts:
        return ''
    return ('<div style="display:flex;flex-wrap:wrap;gap:10px;margin:24px 0;align-items:flex-start;">'
            + ''.join(parts) + '</div>')


def _mark(el, emitted: set):
    emitted.add(id(el))
    for d in el.descendants:
        emitted.add(id(d))


def _collect_img_group(children, start):
    group = []
    i = start
    while i < len(children):
        nc = children[i]
        if not hasattr(nc, 'name'):
            t = str(nc).strip().replace('\xa0', '')
            if not t:
                i += 1
                continue
            break
        if nc.name == 'a' and nc.find('img'):
            group.append(nc)
            i += 1
        elif nc.name in ('br', 'span') and not nc.get_text(strip=True):
            i += 1
        else:
            break
    return group, i


def _walk_children(el, lines, emitted):
    children = list(el.children)
    i = 0
    while i < len(children):
        child = children[i]
        if id(child) in emitted:
            i += 1
            continue
        if hasattr(child, 'name') and child.name == 'a' and child.find('img'):
            group, i = _collect_img_group(children, i)
            if group:
                grid = _make_img_grid(group)
                if grid:
                    lines.append(grid)
                for a in group:
                    _mark(a, emitted)
        else:
            _walk_el(child, lines, emitted)
            i += 1


def _walk_el(el, lines, emitted):
    if id(el) in emitted:
        return
    if not hasattr(el, 'name') or el.name is None:
        return
    tag = el.name.lower()

    if tag in ('script', 'style', 'link', 'head', 'meta', 'br', 'hr'):
        _mark(el, emitted)
        return
    if tag == 'header':
        _mark(el, emitted)
        return
    if tag == 'footer':
        text = el.get_text(' ', strip=True)
        if text:
            lines.append(f'FOOTER: {text}')
        _mark(el, emitted)
        return
    if tag == 'a' and el.find('img'):
        grid = _make_img_grid([el])
        if grid:
            lines.append(grid)
        _mark(el, emitted)
        return
    if tag in ('h1', 'h2'):
        text = el.get_text(' ', strip=True)
        if text:
            lines.append(f'# {text}')
        _mark(el, emitted)
        return
    if tag == 'h3':
        text = el.get_text(' ', strip=True)
        if text:
            lines.append(f'## {text}')
        _mark(el, emitted)
        return
    if tag == 'p':
        children = list(el.children)
        buf = []
        i = 0
        while i < len(children):
            child = children[i]
            if not hasattr(child, 'name') or child.name is None:
                t = str(child).strip()
                if t:
                    buf.append(t)
                i += 1
            elif child.name == 'a' and child.find('img'):
                if buf:
                    lines.append(' '.join(buf))
                    buf = []
                group, i = _collect_img_group(children, i)
                if group:
                    grid = _make_img_grid(group)
                    if grid:
                        lines.append(grid)
                    for a in group:
                        _mark(a, emitted)
            else:
                t = child.get_text(' ', strip=True)
                if t:
                    buf.append(t)
                i += 1
        if buf:
            lines.append(' '.join(buf))
        _mark(el, emitted)
        return
    if tag == 'li':
        text = el.get_text(' ', strip=True)
        if text:
            lines.append(f'- {text}')
        _mark(el, emitted)
        return
    if tag == 'blockquote':
        text = el.get_text(' ', strip=True)
        if text:
            lines.append(f'> {text}')
        _mark(el, emitted)
        return
    emitted.add(id(el))
    _walk_children(el, lines, emitted)


def _html_to_plain(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style', 'link']):
        tag.decompose()
    lines = []
    emitted = set()
    _walk_el(soup, lines, emitted)
    seen, out = set(), []
    for line in lines:
        key = line.strip()[:200]
        if key and key not in seen:
            out.append(line)
            seen.add(key)
    return '\n\n'.join(out)


def _place_images(html: str, img_tags: list) -> str:
    """Place first image after section I, remaining at end. Single image goes at end."""
    if not img_tags:
        return html
    if len(img_tags) == 1:
        return html + '\n' + img_tags[0]
    first_img, rest = img_tags[0], img_tags[1:]
    idx = html.find('</section>')
    if idx != -1:
        pos = idx + len('</section>')
        html = html[:pos] + '\n' + first_img + html[pos:]
    else:
        html = first_img + '\n' + html
    return html + '\n' + '\n'.join(rest)


def _auto_inject_title(text: str) -> str:
    """If no TITLE: line present, promote the first non-empty line as the title."""
    if re.search(r'^TITLE\s*:', text, re.MULTILINE | re.IGNORECASE):
        return text
    lines = text.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and not stripped.startswith('<'):
            rest = '\n'.join(lines[i + 1:]).lstrip('\n')
            return f'TITLE: {stripped}\n\n{rest}'
    return text
