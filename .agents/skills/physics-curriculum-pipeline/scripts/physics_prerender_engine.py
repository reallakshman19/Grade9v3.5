import re
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
KATEX_JS = REPO_ROOT / "standalone" / "vendor" / "katex" / "0.16.8" / "katex.min.js"

NODE_SCRIPT = """
const fs = require('fs');
const katex = require(process.argv[2]);

const inputFile = process.argv[3];
const outputFile = process.argv[4];

let html = fs.readFileSync(inputFile, 'utf8');

// Do not touch content inside <style>, <script>, or svg
const scriptBlocks = [];
html = html.replace(/<script[\\s\\S]*?<\\/script>/gi, (m) => {
    scriptBlocks.push(m);
    return `___SCRIPT_BLOCK_${scriptBlocks.length - 1}___`;
});

const styleBlocks = [];
html = html.replace(/<style[\\s\\S]*?<\\/style>/gi, (m) => {
    styleBlocks.push(m);
    return `___STYLE_BLOCK_${styleBlocks.length - 1}___`;
});

const svgBlocks = [];
html = html.replace(/<svg[\\s\\S]*?<\\/svg>/gi, (m) => {
    svgBlocks.push(m);
    return `___SVG_BLOCK_${svgBlocks.length - 1}___`;
});

// 1. Display math $$ ... $$
html = html.replace(/\\$\\$([\\s\\S]+?)\\$\\$/g, (match, inner) => {
    try {
        return katex.renderToString(inner.trim(), {displayMode: true, throwOnError: false});
    } catch (e) {
        return match;
    }
});

// 2. Display math \\[ ... \\]
html = html.replace(/\\\\\\[([\\s\\S]+?)\\\\\\]/g, (match, inner) => {
    try {
        return katex.renderToString(inner.trim(), {displayMode: true, throwOnError: false});
    } catch (e) {
        return match;
    }
});

// 3. Inline math $ ... $
html = html.replace(/\\$((?:(?!\\$)[^\\n\\r])+?)\\$/g, (match, inner) => {
    try {
        return katex.renderToString(inner.trim(), {displayMode: false, throwOnError: false});
    } catch (e) {
        return match;
    }
});

// 4. Inline math \\( ... \\)
html = html.replace(/\\\\\\(([\\s\\S]+?)\\\\\\)/g, (match, inner) => {
    try {
        return katex.renderToString(inner.trim(), {displayMode: false, throwOnError: false});
    } catch (e) {
        return match;
    }
});

// Restore blocks
html = html.replace(/___SVG_BLOCK_(\\d+)___/g, (_, idx) => svgBlocks[parseInt(idx, 10)]);
html = html.replace(/___STYLE_BLOCK_(\\d+)___/g, (_, idx) => styleBlocks[parseInt(idx, 10)]);
html = html.replace(/___SCRIPT_BLOCK_(\\d+)___/g, (_, idx) => scriptBlocks[parseInt(idx, 10)]);

fs.writeFileSync(outputFile, html, 'utf8');
console.log('Pre-rendered static DOM KaTeX written to ' + outputFile);
"""

def prerender_html(input_file: str, output_file: str):
    node_script_path = REPO_ROOT / "scratch" / "_temp_physics_prerender.js"
    with open(node_script_path, "w", encoding="utf-8") as f:
        f.write(NODE_SCRIPT)
    
    cmd = [
        "node",
        str(node_script_path),
        str(KATEX_JS),
        str(input_file),
        str(output_file)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    print(res.stdout)
    if node_script_path.exists():
        node_script_path.unlink()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        prerender_html(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python physics_prerender_engine.py <input.html> <output.html>")
