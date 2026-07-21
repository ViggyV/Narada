"""Tests for the HTML post-processing in build_site.py.

Both functions under test are regex rewrites over markdown-rendered HTML, and
both fail *quietly*: if the pattern stops matching, the page still builds and
still looks broadly right — the shortlist just loses its styling, or links
silently start navigating away in the same tab. Nothing errors, so nothing
tells you. These tests are the alarm.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from build_site import _open_offsite, _shortlist_markup  # noqa: E402


class TestShortlistMarkup:
    def test_wraps_from_the_heading_to_the_end(self):
        html = "<h2>AI News</h2><ul><li>a</li></ul><h2>Shortlist: What's Worth a Look</h2><ol><li>x</li></ol>"
        out = _shortlist_markup(html)
        assert out.startswith("<h2>AI News</h2>")
        assert '<section class="shortlist"><h2>Shortlist' in out
        assert out.endswith("</section>")

    @pytest.mark.parametrize("heading", [
        "Shortlist: What's Worth a Look",       # heuristic path
        "Shortlist: What's Worth Implementing",  # Claude-written path
        "Shortlist",                             # bare
    ])
    def test_matches_every_shortlist_title_we_emit(self, heading):
        # synthesize.py emits different titles depending on whether Claude ran.
        # The match is on the "Shortlist" prefix — changing that breaks styling
        # with no error, so both spellings are pinned here.
        out = _shortlist_markup(f"<h2>Track</h2><h2>{heading}</h2><p>x</p>")
        assert '<section class="shortlist">' in out

    def test_tolerates_heading_attributes(self):
        out = _shortlist_markup('<h2 id="shortlist">Shortlist: Things</h2><p>x</p>')
        assert '<section class="shortlist">' in out

    def test_no_shortlist_is_left_untouched(self):
        html = "<h2>AI News</h2><ul><li>a</li></ul>"
        assert _shortlist_markup(html) == html

    def test_does_not_double_wrap(self):
        once = _shortlist_markup("<h2>Shortlist: X</h2><p>y</p>")
        assert once.count('<section class="shortlist">') == 1


class TestOpenOffsite:
    def test_external_links_get_target_and_rel(self):
        out = _open_offsite('<a href="https://example.com/a">x</a>')
        assert 'target="_blank"' in out
        assert 'rel="noopener noreferrer"' in out

    def test_http_and_https_both_rewritten(self):
        assert _open_offsite('<a href="http://example.com">x</a>').count('target="_blank"') == 1
        assert _open_offsite('<a href="https://example.com">x</a>').count('target="_blank"') == 1

    @pytest.mark.parametrize("href", [
        "../index.html",        # breadcrumb back to the archive
        "index.html",           # masthead wordmark
        "style.css",
        "loop-engineering/",    # cross-link to the sibling site
        "#section",
    ])
    def test_internal_links_are_left_alone(self, href):
        # In-site navigation must stay in the same tab; a new tab per click
        # would be hostile, and `..` paths are not offsite.
        out = _open_offsite(f'<a href="{href}">x</a>')
        assert "target=" not in out

    def test_rewrites_every_link_not_just_the_first(self):
        html = "".join(f'<a href="https://e{n}.com">{n}</a>' for n in range(5))
        assert _open_offsite(html).count('target="_blank"') == 5

    def test_preserves_href_and_link_text(self):
        out = _open_offsite('<a href="https://example.com/deep/path?q=1">Title Here</a>')
        assert 'href="https://example.com/deep/path?q=1"' in out
        assert ">Title Here</a>" in out

    def test_is_idempotent(self):
        # build_site may be re-run over already-built output; a second pass
        # must not stack duplicate attributes.
        once = _open_offsite('<a href="https://example.com">x</a>')
        assert _open_offsite(once).count('target="_blank"') == 1
