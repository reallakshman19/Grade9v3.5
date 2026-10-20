#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Static DOM Pre-Rendering Engine for Olympiad & IMO Applications.
Compiles raw mathematical delimiters ($$, $, \\[, \\() into static KaTeX DOM nodes
at build time, guaranteeing zero-JS instant typography across any browser, webview, or iframe.
"""

import sys
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
KATEX_JS = REPO_ROOT / "standalone" / "vendor" / "katex" / "0.16.8" / "katex.min.js"

NODE_SCRIPT = """
const fs = require('fs');
const katex = require(process.argv[2]);

const inputFile = process.argv[3];
const outputFile = process.argv[4];

let html = fs.readFileSync(inputFile, 'utf8');

// Preserve sensitive blocks: <script>, <style>, <svg>
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
html = html.replace(/\\\\\\((.+?)\\\\\\)/g, (match, inner) => {
    try {
        return katex.renderToString(inner.trim(), {displayMode: false, throwOnError: false});
    } catch (e) {
        return match;
    }
});

// Restore preserved blocks
html = html.replace(/___SVG_BLOCK_(\\d+)___/g, (m, idx) => svgBlocks[parseInt(idx)]);
html = html.replace(/___STYLE_BLOCK_(\\d+)___/g, (m, idx) => styleBlocks[parseInt(idx)]);
html = html.replace(/___SCRIPT_BLOCK_(\\d+)___/g, (m, idx) => scriptBlocks[parseInt(idx)]);

fs.writeFileSync(outputFile, html, 'utf8');
console.log("Static DOM pre-rendering successfully completed.");
"""

def prerender_html_file(input_path: Path, output_path: Path = None):
    if output_path is None:
        output_path = input_path
    
    runner_js = input_path.parent / "_temp_prerender_runner.js"
    runner_js.write_text(NODE_SCRIPT, encoding="utf-8")
    
    try:
        res = subprocess.run(["node", str(runner_js), str(KATEX_JS), str(input_path), str(output_path)],
                             capture_output=True, text=True, cwd=str(REPO_ROOT))
        if res.returncode != 0:
            raise RuntimeError(f"Pre-rendering failed: {res.stderr}")
        print(f"Pre-rendered {input_path.name} -> {output_path.name} cleanly.")
    finally:
        if runner_js.exists():
            runner_js.unlink()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prerender_engine.py <target_html_path>")
        sys.exit(1)
    prerender_html_file(Path(sys.argv[1]))
