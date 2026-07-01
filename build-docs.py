#!/usr/bin/env python3
"""
Fabric Space Lab - Enhanced Markdown to HTML Builder
Converts lab markdown files to styled HTML storyline pages with proper structure.
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Tuple
import html

# Markdown to HTML module mapping
MODULE_MAP = {
    "00-prerequisites.md": "00-prerequisites.html",
    "01-capacity-and-workspace.md": "01-capacity.html",
    "02-governance-and-security.md": "02-governance.html",
    "03-data-ingestion.md": "03-ingestion.html",
    "04-data-contracts.md": "04-data-contracts.html",
    "05-medallion-lakehouse.md": "05-medallion.html",
    "06-semantic-model.md": "06-semantic-model.html",
    "07-power-bi-reports.md": "07-power-bi.html",
    "08-real-time-intelligence.md": "08-real-time.html",
    "09-data-science.md": "09-data-science.html",
    "10-ontology-knowledge-graph.md": "10-ontology.html",
    "11-ai-agents.md": "11-ai-agents.html",
    "12-ci-cd-deployment.md": "12-ci-cd.html",
    "13-monitoring-optimization.md": "13-monitoring.html",
    "14-fabric-apps.md": "14-fabric-apps.html",
}

# Module titles for navigation
MODULE_TITLES = {
    "00": "Module 00: Prerequisites",
    "01": "Module 01: Capacity & Workspace",
    "02": "Module 02: Governance & Security",
    "03": "Module 03: Data Ingestion",
    "04": "Module 04: Data Contracts",
    "05": "Module 05: Medallion Lakehouse",
    "06": "Module 06: Semantic Model",
    "07": "Module 07: Power BI Reports",
    "08": "Module 08: Real-Time Intelligence",
    "09": "Module 09: Data Science",
    "10": "Module 10: Ontology",
    "11": "Module 11: AI Agents",
    "12": "Module 12: CI/CD",
    "13": "Module 13: Monitoring",
    "14": "Module 14: Fabric Apps",
}


class MarkdownConverter:
    """Enhanced markdown to HTML converter with proper structure."""
    
    def __init__(self):
        self.toc = []
        self.current_section = 0
    
    def convert(self, md_content: str) -> Tuple[str, List[Dict]]:
        """Convert markdown to HTML and extract TOC."""
        lines = md_content.split('\n')
        html_lines = []
        in_code_block = False
        code_lang = ""
        code_buffer = []
        in_table = False
        table_buffer = []
        in_blockquote = False
        blockquote_buffer = []
        in_list = False
        list_buffer = []
        list_type = None
        
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Code blocks
            if stripped.startswith('```'):
                if in_code_block:
                    # End code block
                    code_html = html.escape('\n'.join(code_buffer))
                    lang_class = f'language-{code_lang}' if code_lang else 'language-plaintext'
                    html_lines.append(f'<pre><code class="{lang_class}">{code_html}</code></pre>')
                    in_code_block = False
                    code_buffer = []
                    code_lang = ""
                else:
                    # Start code block
                    code_lang = stripped[3:].strip()
                    in_code_block = True
                i += 1
                continue
            
            if in_code_block:
                code_buffer.append(line)
                i += 1
                continue
            
            # Tables
            if stripped.startswith('|') and '|' in stripped[1:]:
                if not in_table:
                    in_table = True
                    table_buffer = []
                table_buffer.append(stripped)
                i += 1
                continue
            elif in_table and not stripped.startswith('|'):
                # End table
                html_lines.append(self._convert_table(table_buffer))
                in_table = False
                table_buffer = []
                # Don't increment i, process this line
            
            # Horizontal rules
            if stripped in ['---', '***', '___']:
                html_lines.append('<hr>')
                i += 1
                continue
            
            # Blockquotes
            if stripped.startswith('>'):
                if not in_blockquote:
                    in_blockquote = True
                    blockquote_buffer = []
                blockquote_buffer.append(stripped[1:].strip())
                i += 1
                continue
            elif in_blockquote and not stripped.startswith('>'):
                # End blockquote
                blockquote_html = self._process_inline(' '.join(blockquote_buffer))
                html_lines.append(f'<blockquote>{blockquote_html}</blockquote>')
                in_blockquote = False
                blockquote_buffer = []
                # Don't increment i, process this line
            
            # Headers
            h_match = re.match(r'^(#{1,6})\s+(.+)$', stripped)
            if h_match:
                level = len(h_match.group(1))
                title = h_match.group(2)
                title_clean = re.sub(r'^[#\s\d🏗️📊🎯🥉🥈🥇🗒️🔍📐📡🚨❄️✅🔮—:-]+', '', title).strip()
                anchor = re.sub(r'[^\w\s-]', '', title_clean.lower()).replace(' ', '-')
                
                # Add to TOC if h2 or h3
                if level in [2, 3]:
                    self.toc.append({'level': level, 'title': title_clean, 'anchor': anchor})
                
                html_lines.append(f'<h{level} id="{anchor}">{self._process_inline(title)}</h{level}>')
                i += 1
                continue
            
            # Lists
            list_match = re.match(r'^(\d+\.|-|\*)\s+(.+)$', stripped)
            if list_match:
                marker = list_match.group(1)
                content = list_match.group(2)
                new_list_type = 'ol' if marker[0].isdigit() else 'ul'
                
                if not in_list:
                    in_list = True
                    list_type = new_list_type
                    list_buffer = []
                
                list_buffer.append(f'  <li>{self._process_inline(content)}</li>')
                i += 1
                continue
            elif in_list and not list_match:
                # End list
                html_lines.append(f'<{list_type}>')
                html_lines.extend(list_buffer)
                html_lines.append(f'</{list_type}>')
                in_list = False
                list_buffer = []
                list_type = None
                # Don't increment i, process this line
            
            # Empty lines
            if not stripped:
                i += 1
                continue
            
            # Paragraphs
            html_lines.append(f'<p>{self._process_inline(line)}</p>')
            i += 1
        
        # Close any open blocks
        if in_code_block:
            code_html = html.escape('\n'.join(code_buffer))
            lang_class = f'language-{code_lang}' if code_lang else 'language-plaintext'
            html_lines.append(f'<pre><code class="{lang_class}">{code_html}</code></pre>')
        
        if in_table:
            html_lines.append(self._convert_table(table_buffer))
        
        if in_blockquote:
            blockquote_html = self._process_inline(' '.join(blockquote_buffer))
            html_lines.append(f'<blockquote>{blockquote_html}</blockquote>')
        
        if in_list:
            html_lines.append(f'<{list_type}>')
            html_lines.extend(list_buffer)
            html_lines.append(f'</{list_type}>')
        
        return '\n'.join(html_lines), self.toc
    
    def _process_inline(self, text: str) -> str:
        """Process inline markdown (bold, italic, links, code)."""
        # Inline code
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        
        # Links
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        
        # Italic
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        
        return text
    
    def _convert_table(self, lines: List[str]) -> str:
        """Convert markdown table to HTML table."""
        if not lines:
            return ""
        
        # Parse header
        header_line = lines[0]
        headers = [cell.strip() for cell in header_line.split('|')[1:-1]]
        
        # Skip separator line (usually index 1)
        data_lines = lines[2:] if len(lines) > 2 else []
        
        # Build HTML
        html = ['<table class="data-table">']
        html.append('  <thead>')
        html.append('    <tr>')
        for h in headers:
            html.append(f'      <th>{self._process_inline(h)}</th>')
        html.append('    </tr>')
        html.append('  </thead>')
        html.append('  <tbody>')
        
        for line in data_lines:
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            html.append('    <tr>')
            for cell in cells:
                html.append(f'      <td>{self._process_inline(cell)}</td>')
            html.append('    </tr>')
        
        html.append('  </tbody>')
        html.append('</table>')
        
        return '\n'.join(html)


def extract_module_number(filename: str) -> str:
    """Extract module number from filename."""
    match = re.match(r'(\d+)-', filename)
    return match.group(1) if match else "00"


def build_toc_html(toc: List[Dict]) -> str:
    """Build mini-TOC HTML."""
    if not toc:
        return ""
    
    html = ['<nav class="mini-toc" aria-label="Table of contents">']
    html.append('  <div class="toc-title">Contents</div>')
    html.append('  <a href="#top"><span class="toc-dot"></span>Overview</a>')
    
    for item in toc:
        indent = '  ' if item['level'] == 3 else ''
        html.append(f'  {indent}<a href="#{item["anchor"]}"><span class="toc-dot"></span>{item["title"]}</a>')
    
    html.append('</nav>')
    return '\n'.join(html)


def build_html_page(md_file: Path, output_file: Path):
    """Build a single HTML page from markdown with enhanced structure."""
    print(f"Building {md_file.name} -> {output_file.name}")
    
    # Read markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Extract title from first # heading
    title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Lab Module"
    title_clean = re.sub(r'^[#\s\d🏗️📊🎯—:-]+', '', title).strip()
    
    # Module number
    module_num = extract_module_number(md_file.name)
    
    # Convert markdown to HTML
    converter = MarkdownConverter()
    content_html, toc = converter.convert(md_content)
    
    # Build TOC
    toc_html = build_toc_html(toc)
    
    # Build navigation
    module_int = int(module_num)
    prev_num = f"{module_int - 1:02d}" if module_int > 0 else None
    next_num = f"{module_int + 1:02d}" if module_int < 14 else None
    
    prev_link = ""
    next_link = ""
    
    if prev_num and prev_num in MODULE_TITLES:
        prev_files = [v for k, v in MODULE_MAP.items() if k.startswith(prev_num)]
        if prev_files:
            prev_file = prev_files[0]
            prev_link = f'''
        <a href="{prev_file}" class="prev">
          <span class="nav-label">← Previous</span>
          <span class="nav-title">{MODULE_TITLES[prev_num]}</span>
        </a>'''
    
    if next_num and next_num in MODULE_TITLES:
        next_files = [v for k, v in MODULE_MAP.items() if k.startswith(next_num)]
        if next_files:
            next_file = next_files[0]
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

  <!-- Mini TOC Sidebar -->
  {toc_html}

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
    <p>ZOSA Fabric Space Lab &copy; 2026 · <a href="https://github.com/Diaz506/fabric-space-lab">GitHub</a></p>
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
