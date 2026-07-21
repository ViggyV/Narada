"""Tests for the no-key ranking path.

These are the functions most likely to break silently: they have no output
anyone checks, and a threshold tweak can quietly collapse unrelated stories
or stop collapsing real duplicates.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from fetch_sources import LOOKBACK_HOURS, Item  # noqa: E402
from synthesize import (  # noqa: E402
    SHORTLIST_SIZE,
    _cluster,
    _fallback_digest,
    _recency,
    _same_story,
    _score,
    _tokens,
)

NOW = datetime(2026, 7, 20, 12, 0, tzinfo=timezone.utc)


def item(title: str, source: str = "Dev.to top", *, hours_ago: float | None = 1,
         track: str = "AI News") -> Item:
    published = None if hours_ago is None else NOW - timedelta(hours=hours_ago)
    return Item(track=track, source=source, title=title,
                link=f"https://example.com/{abs(hash(title))}", published=published)


class TestTokens:
    def test_drops_stopwords_and_short_words(self):
        assert _tokens("The Rise of AI in Production") == {"rise", "production"}

    def test_case_and_punctuation_insensitive(self):
        assert _tokens("Rise, Production!") == _tokens("rise production")

    def test_title_of_only_stopwords_is_empty(self):
        assert _tokens("the and of it") == frozenset()


class TestSameStory:
    def test_identical_titles_match(self):
        t = _tokens("Optimizing RAG at Scale with Bayesian Search")
        assert _same_story(t, t)

    def test_unrelated_titles_do_not_match(self):
        a = _tokens("Optimizing RAG at Scale with Bayesian Search")
        b = _tokens("Why Compressing an Image to Exactly 50KB Is Hard")
        assert not _same_story(a, b)

    @pytest.mark.parametrize("a,b", [
        ("Postgres 17 Released With Faster Joins", "Postgres 18 Released With Faster Joins"),
        ("Claude 4 Beats Every Benchmark", "Claude 5 Beats Every Benchmark"),
        ("Python 3.9 Reaches End of Life", "Python 3.8 Reaches End of Life"),
    ])
    def test_differing_version_numbers_are_different_stories(self, a, b):
        # Wording alone clears the threshold; the number is the only signal.
        assert not _same_story(_tokens(a), _tokens(b))

    def test_matching_version_numbers_still_cluster(self):
        assert _same_story(
            _tokens("Postgres 17 Released With Faster Joins"),
            _tokens("Postgres 17 Released, With Faster Joins!"),
        )

    def test_empty_token_set_never_matches(self):
        # Guards the ZeroDivisionError that a naive Jaccard would hit, and
        # stops every all-stopword title from collapsing into one cluster.
        assert not _same_story(frozenset(), _tokens("Real Title Here"))
        assert not _same_story(frozenset(), frozenset())


class TestCluster:
    def test_exact_reposts_collapse(self):
        title = "Optimizing RAG at Scale with Bayesian Search"
        clusters = _cluster([item(title), item(title), item(title)])
        assert len(clusters) == 1
        assert len(clusters[0]) == 3

    def test_distinct_stories_stay_separate(self):
        clusters = _cluster([
            item("Optimizing RAG at Scale with Bayesian Search"),
            item("Why Compressing an Image to Exactly 50KB Is Hard"),
            item("A Dependency Resolution Dataset for npm and PyPI"),
        ])
        assert len(clusters) == 3

    def test_every_item_lands_in_exactly_one_cluster(self):
        items = [item(f"Distinct Story Number {n} About Systems") for n in range(6)]
        clusters = _cluster(items)
        assert sum(len(c) for c in clusters) == len(items)

    def test_empty_input(self):
        assert _cluster([]) == []


class TestScore:
    def test_curated_source_outranks_aggregator(self):
        strong = _score([item("Some Story About Systems", "Martin Fowler")], NOW)
        weak = _score([item("Some Story About Systems", "Dev.to top")], NOW)
        assert strong > weak

    def test_cross_source_pickup_outweighs_a_single_curated_hit(self):
        # Two sources carrying one story is the signal the bonus exists for.
        picked_up = _score([
            item("Shared Story About Systems", "Dev.to top"),
            item("Shared Story About Systems", "Hacker News: AI"),
        ], NOW)
        single = _score([item("Solo Story About Systems", "Martin Fowler")], NOW)
        assert picked_up > single

    def test_same_source_repeats_earn_no_pickup_bonus(self):
        # Dev.to reposting itself must not look like independent corroboration.
        repost = _score([
            item("Shared Story About Systems", "Dev.to top"),
            item("Shared Story About Systems", "Dev.to top"),
        ], NOW)
        once = _score([item("Shared Story About Systems", "Dev.to top")], NOW)
        assert repost == pytest.approx(once)

    def test_recent_beats_stale(self):
        fresh = _score([item("Story About Systems", hours_ago=1)], NOW)
        old = _score([item("Story About Systems", hours_ago=LOOKBACK_HOURS - 1)], NOW)
        assert fresh > old

    def test_release_signal_adds_weight(self):
        announced = _score([item("Postgres 17 Released With Faster Joins")], NOW)
        plain = _score([item("Postgres Performance Notes From Practice")], NOW)
        assert announced > plain


class TestRecency:
    def test_undated_sits_between_fresh_and_stale(self):
        undated = _recency([item("X About Systems", hours_ago=None)], NOW)
        fresh = _recency([item("X About Systems", hours_ago=0)], NOW)
        stale = _recency([item("X About Systems", hours_ago=LOOKBACK_HOURS)], NOW)
        assert stale <= undated <= fresh

    def test_never_negative_past_the_window(self):
        assert _recency([item("X About Systems", hours_ago=LOOKBACK_HOURS * 5)], NOW) == 0.0

    def test_cluster_uses_its_newest_member(self):
        mixed = _recency([
            item("X About Systems", hours_ago=20),
            item("X About Systems", hours_ago=1),
        ], NOW)
        assert mixed == pytest.approx(_recency([item("X About Systems", hours_ago=1)], NOW))


class TestFallbackDigest:
    def test_repost_appears_once_in_the_listing(self):
        title = "Optimizing RAG at Scale with Bayesian Search"
        out = _fallback_digest([item(title) for _ in range(4)])
        listing = out.split("## Shortlist")[0]  # it may legitimately recur below
        assert listing.count(title) == 1

    def test_shortlist_heading_prefix_is_stable(self):
        # build_site.py finds the styled block by matching on "Shortlist".
        out = _fallback_digest([item("A Story About Distributed Systems")])
        assert "## Shortlist" in out

    def test_shortlist_is_capped(self):
        items = [item(f"Distinct Story Number {n} About Systems") for n in range(20)]
        out = _fallback_digest(items)
        shortlist = out.split("## Shortlist")[1]
        assert sum(shortlist.count(f"\n{n}. ") for n in range(1, 10)) == SHORTLIST_SIZE

    def test_says_it_was_not_llm_ranked(self):
        out = _fallback_digest([item("A Story About Distributed Systems")])
        assert "without LLM synthesis" in out
