#!/usr/bin/env python3
"""Fail-closed, no-network SEO index check for the Seamless Patch static site."""

from __future__ import annotations

import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from xml.etree import ElementTree

CANONICAL_ORIGIN = "https://www.seamlesspatch.com"
CANONICAL_HOME = f"{CANONICAL_ORIGIN}/"
CANONICAL_SITEMAP = f"{CANONICAL_ORIGIN}/sitemap.xml"
KNOWN_BAD_HOST = "seaslessjpatch.com"


class _SeoHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title_count = 0
        self.h1_count = 0
        self.meta_descriptions: list[str] = []
        self.canonicals: list[str] = []
        self.og_urls: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        lowered_tag = tag.lower()
        if lowered_tag == "title":
            self.title_count += 1
        elif lowered_tag == "h1":
            self.h1_count += 1
        elif lowered_tag == "meta" and values.get("name", "").lower() == "description":
            self.meta_descriptions.append(values.get("content", "").strip())
        elif lowered_tag == "meta" and values.get("property", "").lower() == "og:url":
            self.og_urls.append(values.get("content", "").strip())
        elif lowered_tag == "link" and "canonical" in values.get("rel", "").lower().split():
            self.canonicals.append(values.get("href", "").strip())


def _record(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": passed, "detail": detail})


def check_site(root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    index_path = root / "index.html"
    robots_path = root / "robots.txt"
    sitemap_path = root / "sitemap.xml"

    for path in (index_path, robots_path, sitemap_path):
        _record(checks, f"file:{path.name}", path.is_file(), str(path))

    if not all(path.is_file() for path in (index_path, robots_path, sitemap_path)):
        return {"status": "FAIL", "root": str(root), "checks": checks}

    index_text = index_path.read_text(encoding="utf-8")
    robots_text = robots_path.read_text(encoding="utf-8")
    sitemap_text = sitemap_path.read_text(encoding="utf-8")

    parser = _SeoHtmlParser()
    parser.feed(index_text)
    _record(checks, "html:one-title", parser.title_count == 1, f"count={parser.title_count}")
    _record(checks, "html:one-h1", parser.h1_count == 1, f"count={parser.h1_count}")
    _record(
        checks,
        "html:meta-description",
        len(parser.meta_descriptions) == 1 and 1 <= len(parser.meta_descriptions[0]) <= 160,
        f"count={len(parser.meta_descriptions)} length={len(parser.meta_descriptions[0]) if parser.meta_descriptions else 0}",
    )
    _record(checks, "html:canonical", parser.canonicals == [CANONICAL_HOME], repr(parser.canonicals))
    _record(checks, "html:og-url", parser.og_urls == [CANONICAL_HOME], repr(parser.og_urls))

    sitemap_lines = [line.strip() for line in robots_text.splitlines() if line.strip().lower().startswith("sitemap:")]
    _record(checks, "robots:canonical-sitemap", sitemap_lines == [f"Sitemap: {CANONICAL_SITEMAP}"], repr(sitemap_lines))

    try:
        root_element = ElementTree.fromstring(sitemap_text)
        locations = [
            (element.text or "").strip()
            for element in root_element.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        ]
        sitemap_error = ""
    except ElementTree.ParseError as error:
        locations = []
        sitemap_error = str(error)
    _record(checks, "sitemap:valid-xml", not sitemap_error, sitemap_error or "parsed")
    _record(checks, "sitemap:canonical-home", CANONICAL_HOME in locations, repr(locations))
    foreign_hosts = sorted({urlparse(location).netloc for location in locations if urlparse(location).netloc != "www.seamlesspatch.com"})
    _record(checks, "sitemap:canonical-host-only", not foreign_hosts, repr(foreign_hosts))

    combined = "\n".join((index_text, robots_text, sitemap_text)).lower()
    _record(checks, "site:no-known-bad-host", KNOWN_BAD_HOST not in combined, KNOWN_BAD_HOST)

    passed = sum(1 for check in checks if check["passed"])
    failed = len(checks) - passed
    return {
        "status": "PASS" if failed == 0 else "FAIL",
        "root": str(root),
        "summary": {"passed": passed, "failed": failed, "total": len(checks)},
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    report = check_site(args.root.resolve())
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
