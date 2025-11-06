# md2html.py
import sys, pathlib, html
from markdown import markdown


TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{title}</title><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root {{ color-scheme: light dark; }}
body {{
  margin: 2rem auto;
  max-width: 860px;
  padding: 0 1rem;
  font: 16px/1.6 system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,"Helvetica Neue",Arial,"Noto Sans","Apple Color Emoji","Segoe UI Emoji";
}}
h1,h2,h3 {{ line-height: 1.25; }}
h1 {{ font-size: 1.9rem; margin-top: 0; }}
h2 {{ font-size: 1.5rem; margin-top: 2.2rem; }}
h3 {{ font-size: 1.2rem; margin-top: 1.6rem; }}
code, pre {{
  font-family: ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;
  font-size: .95em;
}}
pre {{
  background: rgba(127,127,127,.1);
  border: 1px solid rgba(127,127,127,.3);
  border-radius: 8px;
  padding: 1rem;
  overflow: auto;
}}
blockquote {{
  margin: 1rem 0;
  padding: .5rem 1rem;
  border-left: 4px solid #888;
  background: rgba(127,127,127,.08);
  border-radius: 6px;
}}

/* --- improved list indentation for mixed list types --- */
:root {{
  --indent-1: 2.25rem;
  --indent-2: 4.25rem;
  --indent-3: 6.25rem;
  --indent-4: 8.25rem;
}}

ol, ul {{
  margin: 0.4em 0;
  padding-left: var(--indent-1);
  list-style-position: outside;
}}

li > ol, li > ul {{
  margin-top: 0.3em;
  margin-bottom: 0.3em;
  padding-left: var(--indent-2);
}}

li li > ol, li li > ul {{
  padding-left: var(--indent-3);
}}

li li li > ol, li li li > ul {{
  padding-left: var(--indent-4);
}}

/* special case: unordered inside ordered (like #3. followed by bullets) */
ol > li > ul {{
  margin-top: 0.4em;
  padding-left: calc(var(--indent-2) + 1rem);
}}

ul > li > ol {{
  padding-left: calc(var(--indent-2) + 1rem);
}}

hr {{
  border: none;
  border-top: 1px solid rgba(127,127,127,.3);
  margin: 2rem 0;
}}
</style>
<script>
  window.MathJax = {{
    tex: {{
      inlineMath: [['$','$'], ['\\\\(','\\\\)']],
      displayMath: [['$$','$$'], ['\\\\[','\\\\]']]
    }},
    options: {{
      skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
    }}
  }};
</script>
<script async id="MathJax-script"
  src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
</head><body>
{body}
</body></html>"""



def main(inp, outp):
    md = pathlib.Path(inp).read_text(encoding="utf-8")
    html_body = markdown(md, extensions=["fenced_code", "codehilite", "tables", "toc",  "sane_lists"])
    title = html.escape(pathlib.Path(inp).stem)
    pathlib.Path(outp).write_text(TEMPLATE.format(title=title, body=html_body), encoding="utf-8")
    print(f"Wrote {outp}")

if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else "README.md"
    outp = sys.argv[2] if len(sys.argv) > 2 else (pathlib.Path(inp).with_suffix(".html"))
    main(inp, outp)

