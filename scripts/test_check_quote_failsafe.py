from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from check_quote_failsafe import check_quote_failsafe


def _page(catch_body: str, gallery: str = "<p>Before and after photos on request.</p>") -> str:
    return f"""<!doctype html>
<html lang="en"><head><title>Seamless Patch</title></head>
<body>
<div id="gallery">{gallery}</div>
<form id="bidForm"></form>
<script>
  form.addEventListener('submit', async function(e) {{
    try {{
      const response = await fetch('/api/quote', {{ method: 'POST', body: data }});
    }} catch (error) {{
{catch_body}
    }} finally {{
      submitButton.disabled = false;
    }}
  }});
</script>
</body></html>
"""


GOOD_CATCH = """      success.innerHTML = '<a href="' + smsUrl + '">Tap here to text (602) 881-1676</a>'
        + '<a href="tel:6028811676">Tap here to call</a>'
        + '<strong>(602) 881-1676</strong>';"""


class QuoteFailsafeCheckTest(unittest.TestCase):
    def _run(self, html: str) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            index = Path(directory) / "index.html"
            index.write_text(html, encoding="utf-8")
            return check_quote_failsafe(index)

    def _failed(self, result: dict) -> set[str]:
        return {check["name"] for check in result["checks"] if not check["passed"]}

    def test_compliant_page_passes(self) -> None:
        result = self._run(_page(GOOD_CATCH))
        self.assertTrue(result["ok"], self._failed(result))

    def test_missing_index_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = check_quote_failsafe(Path(directory) / "index.html")
        self.assertFalse(result["ok"])
        self.assertIn("index_exists", self._failed(result))

    def test_navigating_away_on_failure_is_rejected(self) -> None:
        result = self._run(_page(GOOD_CATCH + "\n      window.location.href = smsUrl;"))
        self.assertFalse(result["ok"])
        self.assertIn("failure_does_not_navigate_away", self._failed(result))

    def test_location_replace_on_failure_is_rejected(self) -> None:
        result = self._run(_page(GOOD_CATCH + "\n      window.location.replace(smsUrl);"))
        self.assertFalse(result["ok"])
        self.assertIn("failure_does_not_navigate_away", self._failed(result))

    def test_clearing_the_form_on_failure_is_rejected(self) -> None:
        result = self._run(_page(GOOD_CATCH + "\n      form.reset();"))
        self.assertFalse(result["ok"])
        self.assertIn("failure_preserves_typed_answers", self._failed(result))

    def test_failure_without_call_link_is_rejected(self) -> None:
        catch = """      success.innerHTML = '<a href="' + smsUrl + '">Text (602) 881-1676</a>';"""
        result = self._run(_page(catch))
        self.assertFalse(result["ok"])
        self.assertIn("failure_offers_call_link", self._failed(result))

    def test_failure_without_text_link_is_rejected(self) -> None:
        catch = """      success.innerHTML = '<a href="tel:6028811676">Call (602) 881-1676</a>';"""
        result = self._run(_page(catch))
        self.assertFalse(result["ok"])
        self.assertIn("failure_offers_text_link", self._failed(result))

    def test_links_without_readable_number_are_rejected(self) -> None:
        catch = """      success.innerHTML = '<a href="' + smsUrl + '">Text us</a>'
        + '<a href="tel:6028811676">Call us</a>';"""
        result = self._run(_page(catch))
        self.assertFalse(result["ok"])
        self.assertIn("failure_shows_phone_as_text", self._failed(result))

    def test_internal_placeholder_copy_is_rejected(self) -> None:
        gallery = "<h3>Before &amp; After Gallery Coming Next</h3><p>Upload real job photos here as soon as he sends them.</p>"
        result = self._run(_page(GOOD_CATCH, gallery=gallery))
        self.assertFalse(result["ok"])
        self.assertIn("no_internal_placeholder_copy", self._failed(result))

    def test_missing_catch_block_is_rejected(self) -> None:
        html = "<!doctype html><html><body><script>const a = 1;</script></body></html>"
        result = self._run(html)
        self.assertFalse(result["ok"])
        self.assertIn("submit_catch_block_present", self._failed(result))


if __name__ == "__main__":
    unittest.main()
