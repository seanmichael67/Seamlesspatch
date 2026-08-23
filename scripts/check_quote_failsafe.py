#!/usr/bin/env python3
"""Fail-closed, no-network check that a failed quote submit never loses the lead.

The quote form posts to /api/quote. When that call fails the visitor must still
be handed a way to reach the business, and must not be navigated away from the
page or have their typed answers cleared. This check asserts those specific
guarantees against index.html, plus that no internal-facing placeholder copy is
shipped to visitors.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

BUSINESS_PHONE_DIGITS = "6028811676"

# Copy that was written for the site owner, not for visitors. Shipping it live
# tells homeowners the gallery is unfinished and reveals it is stock imagery.
INTERNAL_ONLY_PHRASES = (
    "Upload real job photos here",
    "will outperform stock photos",
    "Gallery Coming Next",
)


def _record(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": passed, "detail": detail})


def _catch_block(html: str) -> str | None:
    """Return the submit handler's catch block, or None if it is not found."""
    match = re.search(r"\}\s*catch\s*\(\s*error\s*\)\s*\{(.*?)\}\s*finally\s*\{", html, re.S)
    return match.group(1) if match else None


def check_quote_failsafe(index_path: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    if not index_path.is_file():
        _record(checks, "index_exists", False, f"missing file: {index_path}")
        return {"ok": False, "checks": checks}
    _record(checks, "index_exists", True, str(index_path))

    html = index_path.read_text(encoding="utf-8")

    leaked = [phrase for phrase in INTERNAL_ONLY_PHRASES if phrase in html]
    _record(
        checks,
        "no_internal_placeholder_copy",
        not leaked,
        "clean" if not leaked else f"internal copy shipped to visitors: {leaked}",
    )

    catch = _catch_block(html)
    if catch is None:
        _record(checks, "submit_catch_block_present", False, "no catch(error){...}finally{ in submit handler")
        return {"ok": False, "checks": checks}
    _record(checks, "submit_catch_block_present", True, f"{len(catch)} chars")

    # Navigating away on failure discards everything the visitor typed, and on
    # desktop an sms: navigation usually does nothing at all.
    navigates_away = re.search(r"(location\s*\.\s*href\s*=|location\s*\.\s*(assign|replace)\s*\()", catch)
    _record(
        checks,
        "failure_does_not_navigate_away",
        not navigates_away,
        "stays on page" if not navigates_away else f"navigates away: {navigates_away.group(0)}",
    )

    resets_form = re.search(r"\.reset\s*\(\s*\)", catch)
    _record(
        checks,
        "failure_preserves_typed_answers",
        not resets_form,
        "form kept" if not resets_form else "form.reset() runs on the failure path",
    )

    has_sms = f"sms:{BUSINESS_PHONE_DIGITS}" in catch or "smsUrl" in catch
    _record(checks, "failure_offers_text_link", has_sms, "sms path present" if has_sms else "no sms link on failure")

    has_tel = f"tel:{BUSINESS_PHONE_DIGITS}" in catch
    _record(checks, "failure_offers_call_link", has_tel, "tel: link present" if has_tel else "no tel: link on failure")

    # A tappable link is not enough: desktop visitors need the digits as text.
    readable_phone = re.search(r"\(602\)\s*881-1676", catch)
    _record(
        checks,
        "failure_shows_phone_as_text",
        bool(readable_phone),
        "phone readable" if readable_phone else "phone number never rendered as plain text",
    )

    return {"ok": all(check["passed"] for check in checks), "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repository root containing index.html")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args()

    result = check_quote_failsafe(Path(args.root) / "index.html")

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for check in result["checks"]:
            print(f"[{'PASS' if check['passed'] else 'FAIL'}] {check['name']}: {check['detail']}")
        passed = sum(1 for check in result["checks"] if check["passed"])
        print(f"\n{passed}/{len(result['checks'])} checks passed")

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
