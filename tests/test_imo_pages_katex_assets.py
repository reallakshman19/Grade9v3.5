"""Source-safe regression for the PR240 research Pages KaTeX asset contract.

Extract only the real generator's path helpers; never execute the research bank
builder or import original question records during this test.
"""
import ast
import os
import tempfile
import unittest
from pathlib import Path

from Shared.tools import build_pages_site


REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "Mathematics/research/build_full_master_suite.py"
ASSETS = ("katex.min.css", "katex.min.js", "contrib/auto-render.min.js")


def _actual_generator_helpers():
    tree = ast.parse(BUILDER.read_text(encoding="utf-8"), filename=str(BUILDER))
    names = {"suite_output_targets", "render_output_katex"}
    selected = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in names
    ]
    if {node.name for node in selected} != names:
        raise AssertionError("required real generator helper missing")
    module = ast.Module(body=selected, type_ignores=[])
    namespace = {"Path": Path, "os": os}
    exec(compile(module, str(BUILDER), "exec"), namespace)
    return namespace["suite_output_targets"], namespace["render_output_katex"]


class ResearchPagesKatexTests(unittest.TestCase):
    def setUp(self):
        self.outputs, self.rewrite = _actual_generator_helpers()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.template = (
            '<!doctype html><html><head>'
            '<link rel="stylesheet" href="vendor/katex/0.16.8/katex.min.css">'
            '<script src="vendor/katex/0.16.8/katex.min.js"></script>'
            '<script src="vendor/katex/0.16.8/contrib/auto-render.min.js"></script>'
            '</head><body>authored synthetic page</body></html>'
        )
        for _out, vendor in self.outputs():
            for asset in ASSETS:
                file = self.root / vendor / "katex" / "0.16.8" / asset
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text("synthetic fixture", encoding="utf-8")

    def _output(self, page, vendor, template=None):
        return self.rewrite(
            self.template if template is None else template,
            self.root / page,
            self.root / vendor,
        )

    def test_four_owned_output_locations_are_explicit(self):
        self.assertEqual(
            {str(page): str(vendor) for page, vendor in self.outputs()},
            {
                "standalone/mathematics-imo-grade9-master-suite.html": "standalone/vendor",
                "public/standalone/mathematics-imo-grade9-master-suite.html": "public/vendor",
                "public/test/imo-grade9/core2.html": "public/vendor",
                "docs/test/imo-grade9/core2.html": "docs/vendor",
            },
        )

    def test_all_three_assets_resolve_at_every_actual_output_depth(self):
        expected = {
            "standalone/mathematics-imo-grade9-master-suite.html": "vendor",
            "public/standalone/mathematics-imo-grade9-master-suite.html": "../vendor",
            "public/test/imo-grade9/core2.html": "../../vendor",
            "docs/test/imo-grade9/core2.html": "../../vendor",
        }
        for page, vendor in self.outputs():
            with self.subTest(page=page):
                rendered = self._output(page, vendor)
                prefix = expected[str(page)] + "/katex/0.16.8/"
                self.assertNotIn('"vendor/katex/', rendered) if prefix != "vendor/katex/0.16.8/" else None
                for asset in ASSETS:
                    self.assertIn('"' + prefix + asset + '"', rendered)
                    resolved = (self.root / page.parent / prefix / asset).resolve()
                    self.assertEqual(resolved, (self.root / vendor / "katex" / "0.16.8" / asset).resolve())
                    self.assertTrue(resolved.is_file())

    def test_declared_vendor_asset_missing_fails_closed(self):
        page, vendor = self.outputs()[2]
        (self.root / vendor / "katex" / "0.16.8" / "katex.min.js").unlink()
        with self.assertRaisesRegex(FileNotFoundError, "KATEX_VENDOR_ASSET_MISSING"):
            self._output(page, vendor)

    def test_missing_source_link_fails_closed(self):
        page, vendor = self.outputs()[1]
        corrupt = self.template.replace('vendor/katex/0.16.8/katex.min.css', 'missing/katex.min.css')
        with self.assertRaisesRegex(ValueError, "KATEX_SOURCE_REFERENCE_INVALID"):
            self._output(page, vendor, corrupt)

    def test_duplicate_source_link_fails_closed(self):
        page, vendor = self.outputs()[2]
        corrupt = self.template.replace('</head>', '<link href="vendor/katex/0.16.8/katex.min.css"></head>')
        with self.assertRaisesRegex(ValueError, "KATEX_SOURCE_REFERENCE_INVALID"):
            self._output(page, vendor, corrupt)

    def test_non_katex_markup_and_authored_text_preserved(self):
        for page, vendor in self.outputs():
            with self.subTest(page=page):
                rendered = self._output(page, vendor)
                self.assertIn("authored synthetic page", rendered)
                self.assertIn("<!doctype html>", rendered)
                self.assertEqual(rendered.count("/katex/0.16.8/"), 3)

    def test_pages_link_checker_accepts_depth_correct_research_outputs(self):
        # Mirrors under docs/ are sourced from public/ and use the same depth.
        outputs = self.outputs()
        files = {
            "standalone/mathematics-imo-grade9-master-suite.html":
                ("synthetic", self._output(*outputs[1]).encode("utf-8")),
            "test/imo-grade9/core2.html":
                ("synthetic", self._output(*outputs[2]).encode("utf-8")),
        }
        for asset in ASSETS:
            files["vendor/katex/0.16.8/" + asset] = ("synthetic", b"asset")
        self.assertEqual(build_pages_site.link_findings(files, repo=self.root), [])

    def test_pages_link_checker_rejects_old_wrong_depth(self):
        files = {
            "test/imo-grade9/core2.html": ("synthetic", self.template.encode("utf-8")),
        }
        for asset in ASSETS:
            files["vendor/katex/0.16.8/" + asset] = ("synthetic", b"asset")
        findings = build_pages_site.link_findings(files, repo=self.root)
        self.assertEqual(len(findings), 3)
        self.assertTrue(all("generated target missing" in finding for finding in findings))

    def test_pages_mirror_vendor_rewrite_preserves_fixed_local_path(self):
        page, vendor = self.outputs()[2]
        authored = self._output(page, vendor)
        authored = authored.replace(
            "</head>",
            '<script onerror="this.src=\'https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js\'"></script></head>',
        )
        mirrored = build_pages_site._public_payload(
            "test/imo-grade9/core2.html", authored.encode("utf-8")
        ).decode("utf-8")
        self.assertIn('../../vendor/katex/0.16.8/katex.min.css', mirrored)
        self.assertIn('../../vendor/katex/0.16.8/katex.min.js', mirrored)
        self.assertNotIn("cdn.jsdelivr.net", mirrored)


if __name__ == "__main__":
    unittest.main()
