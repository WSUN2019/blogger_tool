"""CLI: python -m blogformat"""
import argparse
import sys
from . import THEMES, parse_input, render


def main():
    ap = argparse.ArgumentParser(
        description="Format a blog post into Blogger-compatible inlined HTML.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("input", nargs="?", help="Input file (omit to read stdin)")
    ap.add_argument("-o", "--output", help="Output file (default: stdout)")
    ap.add_argument("-t", "--theme", default="navy_gold", choices=list(THEMES.keys()),
                    help="Color scheme (default: navy_gold)")
    ap.add_argument("--list-themes", action="store_true", help="Show available themes and exit")
    args = ap.parse_args()

    if args.list_themes:
        print("Available themes:")
        for key, theme in THEMES.items():
            print(f"  {key:<12}  {theme.name}")
            print(f"               primary={theme.primary}  accent={theme.accent}  bg={theme.bg}")
        return

    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        if sys.stdin.isatty():
            ap.error("No input file provided and stdin is empty.")
        text = sys.stdin.read()

    theme = THEMES[args.theme]
    post = parse_input(text)
    html_out = render(post, theme)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(html_out)
        print(f"Wrote {args.output} ({len(html_out):,} chars, theme: {args.theme})", file=sys.stderr)
    else:
        print(html_out)


if __name__ == "__main__":
    main()
