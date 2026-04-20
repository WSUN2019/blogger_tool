import os
import re
from bs4 import BeautifulSoup

_FLOAT_RE = re.compile(r'\bfloat\s*:\s*\w+\s*;?\s*', re.IGNORECASE)
_MARGIN_FLOAT_RE = re.compile(r'\bmargin-(left|right)\s*:\s*[^;]+;?\s*', re.IGNORECASE)


def _strip_float_style(tag):
    """Remove float and float-related margin styles from a tag's style attribute in-place."""
    for el in [tag] + tag.find_all(True):
        style = el.get('style', '')
        if style:
            cleaned = _FLOAT_RE.sub('', style)
            cleaned = _MARGIN_FLOAT_RE.sub('', cleaned).strip().strip(';').strip()
            if cleaned:
                el['style'] = cleaned
            else:
                del el['style']


def clean_html_string(html: str) -> list[str]:
    """Extract <a><img></a> tags, stripping float styles. Returns a list of tag strings."""
    soup = BeautifulSoup(html, 'html.parser')
    tags = []
    for a in soup.find_all('a'):
        if a.find('img'):
            _strip_float_style(a)
            tags.append(str(a))
    return tags


def clean_tags(input_folder='html_input', input_file='dirty_html1.html',
               output_folder='html_output', output_file='cleaned_images.html'):
    """File-based CLI wrapper: read from html_input/, write to html_output/."""
    input_path = os.path.join(input_folder, input_file)
    output_path = os.path.join(output_folder, output_file)

    try:
        os.makedirs(output_folder, exist_ok=True)

        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tags = clean_html_string(content)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(tags))

        print('-' * 30)
        print('Success!')
        print(f'Input:  {input_path}')
        print(f'Output: {output_path}')
        print(f'Found {len(tags)} image links.')
        print('-' * 30)

    except FileNotFoundError:
        print(f"Error: Could not find '{input_file}' inside '{input_folder}'.")
        print(f'Current working directory: {os.getcwd()}')


if __name__ == '__main__':
    clean_tags()
