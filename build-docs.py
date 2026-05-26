#!/usr/bin/env python3
"""
Fabric Space Lab - Markdown to HTML Builder
Converts lab markdown files to styled HTML storyline pages.
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Tuple

# Markdown to HTML module mapping
MODULE_MAP = {
    "00-prerequisites.md": "00-prerequisites.html",
    "01-capacity-workspace.md": "01-capacity.html",
    "02-governance-and-security.md": "02-governance.html",
    "03-data-ingestion.md": "03-ingestion.html",
    "04-medallion-lakehouse.md": "04-medallion.html",
    "05-semantic-model.md": "05-semantic-model.html",
    "06-power-bi-reports.md": "06-power-bi.html",
    "07-real-time-intelligence.md": "07-real-time.html",
    "08-data-science.md": "08-data-science.html",
    "09-ontology.md": "09-ontology.html",
    "10-ai-agents.md": "10-ai-agents.html",
    "11-ci-cd.md": "11-ci-cd.html",
    "12-monitoring.md": "12-monitoring.html",
}

# Module titles for navigation
MODULE_TITLES = {
    "00": "Module 00: Prerequisites",
    "01": "Module 01: Capacity & Workspace",
    "02": "Module 02: Governance & Security",
    "03": "Module 03: Data Ingestion",
    "04": "Module 04: Medallion Lakehouse",
    "05": "Module 05: Semantic Model",
    "06": "Module 06: Power BI Reports",
    "07": "Module 07: Real-Time Intelligence",
    "08": "Module 08: Data Science",
    "09": "Module 09: Ontology",
    "10": "Module 10: AI Agents",
    "11": "Module 11: CI/CD",
    "12": "Module 12: Monitoring",
}


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def convert_markdown_to_html(md_content: str) -> str:
    """Convert markdown content to HTML with custom styling."""
    html = md_content
    
    # Code blocks with language
    def replace_code_block(match):
        lang = match.group(1) or ""
        code = match.group(2)
        escaped_code = escape_html(code)
        lang_class = f"language-{lang}" if lang else "language-plaintext"
        return f'<pre><code class="{lang_class}">{escaped_code}</code></pre>'
    
    html = re.sub(r'```(\w+)?\n(.*?)```', replace_code_block, html, flags=re.DOTALL)
    
    # Inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # Headers
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    
    # Blockquotes (narrative sections)
    html = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)
    
    # Bold and italic
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    
    # Links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
    
    # Lists
    html = re.sub(r'^\- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    
    # Wrap consecutive <li> in <ul>
    html = re.sub(r'(<li>.*?</li>)\n(?!<li>)', r'<ul>\1</ul>\n', html, flags=re.DOTALL)
    html = re.sub(r'(<li>.*?</li>)', r'<ul>\1</ul>', html)
    
    # Paragraphs
    lines = html.split('\n')
    in_block = False
    result = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        # Check if line is already wrapped
        if stripped.startswith(('<h', '<pre', '<ul', '<ol', '<blockquote', '<table', '<div')):
            in_block = True
            result.append(line)
        elif stripped.startswith(('</pre', '</ul', '</ol', '</blockquote', '</table', '</div')):
            in_block = False
            result.append(line)
        elif not in_block and not stripped.startswith('<'):
            result.append(f'<p>{line}</p>')
        else:
            result.append(line)
    
    return '\n'.join(result)


def extract_module_number(filename: str) -> str:
    """Extract module number from filename."""
    match = re.match(r'(\d+)-', filename)
    return match.group(1) if match else "00"


def build_html_page(md_file: Path, output_file: Path):
    """Build a single HTML page from markdown."""
    print(f"Building {md_file.name} -> {output_file.name}")
    
    # Read markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Extract title from first # heading
    title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Lab Module"
    title_clean = re.sub(r'^[#\s\d—:-]+', '', title).strip()
    
    # Module number
    module_num = extract_module_number(md_file.name)
    
    # Convert markdown to HTML
    content_html = convert_markdown_to_html(md_content)
    
    # Build navigation
    module_int = int(module_num)
    prev_num = f"{module_int - 1:02d}" if module_int > 0 else None
    next_num = f"{module_int + 1:02d}" if module_int < 12 else None
    
    prev_link = ""
    next_link = ""
    
    if prev_num and prev_num in MODULE_TITLES:
        prev_file = [v for k, v in MODULE_MAP.items() if k.startswith(prev_num)][0]
        prev_link = f'''
        <a href="{prev_file}" class="prev">
          <span class="nav-label">← Previous</span>
          <span class="nav-title">{MODULE_TITLES[prev_num]}</span>
        </a>'''
    
    if next_num and next_num in MODULE_TITLES:
        next_file = [v for k, v in MODULE_MAP.items() if k.startswith(next_num)][0]
        next_link = f'''
        <a href="{next_file}" class="next">
          <span class="nav-label">Next →</span>
          <span class="nav-title">{MODULE_TITLES[next_num]}</span>
        </a>'''
    
    # HTML template
    html_output = f'''<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Module {module_num} — {title_clean} · Fabric Space Lab</title>
  <script>(function(){{var t=localStorage.getItem('zosa-theme');if(t)document.documentElement.setAttribute('data-theme',t)}})();</script>
  <link rel="icon" type="image/svg+xml" href="../favicon.svg">
  <link rel="stylesheet" href="../css/theme.css">
  <link rel="stylesheet" href="../css/storyboard.css">
  <link rel="stylesheet" href="../css/components.css">
  <link rel="stylesheet" href="../assets/vendor/prism-tomorrow.min.css">
</head>
<body>
  <div class="progress-bar"></div>

  <!-- Header -->
  <header class="site-header">
    <div class="header-inner">
      <a href="../index.html" class="header-logo">
        <img src="../assets/svg/logo.svg" alt="" width="32" height="32">
        <div>
          <div class="logo-text">ZOSA</div>
          <div class="logo-sub">Fabric Space Lab</div>
        </div>
      </a>
      <nav class="header-nav">
        <a href="../index.html">Modules</a>
        <a href="https://github.com/Diaz506/fabric-space-lab" target="_blank" rel="noopener">GitHub</a>
        <button class="theme-toggle" aria-label="Toggle theme">🌙</button>
      </nav>
    </div>
  </header>

  <!-- Main Content -->
  <main class="storyboard-content">
    <section class="hero" id="top">
      <div class="hero-overline">Module {module_num}</div>
      <h1>{title_clean}</h1>
    </section>

    <section class="chapter">
      {content_html}
    </section>

    <!-- Navigation -->
    <nav class="module-nav">
      {prev_link}
      {next_link}
    </nav>
  </main>

  <footer class="site-footer">
    <p>ZOSA Fabric Space Lab &copy; 2025 · <a href="https://github.com/Diaz506/fabric-space-lab">GitHub</a></p>
  </footer>

  <!-- Scripts -->
  <script src="../assets/vendor/prism.min.js"></script>
  <script src="../assets/vendor/prism-python.min.js"></script>
  <script src="../assets/vendor/prism-sql.min.js"></script>
  <script src="../assets/vendor/prism-powershell.min.js"></script>
  <script src="../assets/vendor/prism-bash.min.js"></script>
  <script src="../assets/vendor/prism-kusto.min.js"></script>
  <script src="../js/nav.js"></script>
  <script src="../js/storyboard.js"></script>
  <script src="../js/code-blocks.js"></script>
</body>
</html>'''
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_output)
    
    print(f"  DONE: Generated {output_file}")


def main():
    """Main build process."""
    # Set UTF-8 encoding for Windows console
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    root = Path(__file__).parent
    labs_dir = root / "labs"
    docs_dir = root / "docs" / "modules"
    
    if not labs_dir.exists():
        print(f"ERROR: Labs directory not found: {labs_dir}")
        return
    
    if not docs_dir.exists():
        print(f"ERROR: Docs/modules directory not found: {docs_dir}")
        return
    
    print("Building HTML documentation from markdown labs...")
    print()
    
    built_count = 0
    for md_file_name, html_file_name in MODULE_MAP.items():
        md_path = labs_dir / md_file_name
        html_path = docs_dir / html_file_name
        
        if not md_path.exists():
            print(f"WARNING: Skipping {md_file_name} (not found)")
            continue
        
        build_html_page(md_path, html_path)
        built_count += 1
    
    print()
    print(f"SUCCESS: Built {built_count} HTML pages")
    print()
    print("Output: docs/modules/")


if __name__ == "__main__":
    main()
