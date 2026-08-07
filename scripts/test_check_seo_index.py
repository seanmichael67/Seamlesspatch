from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from check_seo_index import CANONICAL_HOME, CANONICAL_SITEMAP, check_site


VALID_INDEX = f"""<!doctype html>
<html lang=\"en\"><head>
<title>Seamless Patch</title>
<meta name=\"description\" content=\"Phoenix drywall repair and texture matching from Seamless Patch.\">
<meta property=\"og:url\" content=\"{CANONICAL_HOME}\">
<link rel=\"canonical\" href=\"{CANONICAL_HOME}\">
</head><body><h1>Drywall repair</h1></body></html>
"""
VALID_SITEMAP = f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\"><url><loc>{CANONICAL_HOME}</loc></url></urlset>
"""


class SeoIndexCheckTest(unittest.TestCase):
    def _fixture(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / "index.html").write_text(VALID_INDEX, encoding="utf-8")
        (root / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {CANONICAL_SITEMAP}\n", encoding="utf-8")
        (root / "sitemap.xml").write_text(VALID_SITEMAP, encoding="utf-8")
        return root

    def test_valid_canonical_contract_passes(self) -> None:
        report = check_site(self._fixture())
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["summary"]["failed"], 0)

    def test_misspelled_sitemap_host_fails_closed(self) -> None:
        root = self._fixture()
        (root / "robots.txt").write_text(
            "User-agent: *\nAllow: /\n\nSitemap: https://www.seaslessjpatch.com/sitemap.xml\n",
            encoding="utf-8",
        )
        report = check_site(root)
        self.assertEqual(report["status"], "FAIL")
        failed_names = {check["name"] for check in report["checks"] if not check["passed"]}
        self.assertIn("robots:canonical-sitemap", failed_names)
        self.assertIn("site:no-known-bad-host", failed_names)


if __name__ == "__main__":
    unittest.main()
