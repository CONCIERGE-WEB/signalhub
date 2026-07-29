"""PHASE 3.1 — Discovery Engine (Dorking) adapter & certification tests."""
from __future__ import annotations

import unittest

from dork_signals.adapter import post_to_raw_hit, posts_to_raw_hits
from dork_signals.certification import certification_scorecard
from dork_signals.provider import DorkSignalsProvider


class TestDiscoveryEngineAdapter(unittest.TestCase):
    def test_maps_engine_post_to_raw_hit_signal_only(self):
        post = {
            "autor": "user1",
            "texto": "Preciso de ajuda com cobrança indevida no banco",
            "link": "https://www.reddit.com/r/brasil/comments/abc123/x/",
            "fonte": "varredura:web",
            "dork_id": "pt_v2_001",
            "canal": "reddit_portugal",
            "grupo": "pt_banco",
        }
        hit = post_to_raw_hit(post)
        self.assertIsNotNone(hit)
        assert hit is not None
        self.assertEqual(hit.url, post["link"])
        self.assertIn("cobrança", hit.snippet.lower() + hit.title.lower())
        self.assertEqual(hit.source, "reddit_portugal")
        self.assertEqual(hit.provenance.provider_id, "dorking")
        self.assertEqual(hit.provenance.extras.get("collected_via"), "discovery_engine_dorking")

    def test_normalize_produces_signal_not_lead(self):
        posts = [
            {
                "texto": "Reclamação Reclame Aqui",
                "link": "https://www.reclameaqui.com.br/empresa/x/123/",
                "fonte": "varredura:web",
                "canal": "reclame_aqui",
            }
        ]
        hits = posts_to_raw_hits(posts, limit=5)
        self.assertEqual(len(hits), 1)
        provider = DorkSignalsProvider()
        signals = provider.normalize(hits)
        self.assertEqual(len(signals), 1)
        sig = signals[0]
        self.assertEqual(sig.provider, "dorking")
        self.assertTrue(sig.url)
        self.assertEqual(sig.contract_version, "1.0.0")
        # Must not be a Lead object
        self.assertFalse(hasattr(sig, "lead_status") and type(sig).__name__ == "Lead")

    def test_search_empty_when_live_off(self):
        import os

        os.environ.pop("SIGNALHUB_DORKING_LIVE", None)
        provider = DorkSignalsProvider()
        from signalhub.core.contracts.provider import ProviderQuery

        hits = provider.search(ProviderQuery(capability_id="discover_signals", terms=["test"]))
        self.assertEqual(list(hits), [])

    def test_health_certified_level_1(self):
        h = DorkSignalsProvider().healthcheck()
        self.assertTrue(h.ok)
        self.assertIn("Certified Level 1", h.detail)

    def test_certification_scorecard(self):
        card = certification_scorecard(live=False, config_ok=True, adapter_ok=True)
        self.assertEqual(card["status"], "certified")
        self.assertEqual(card["level"], 1)
        self.assertEqual(card["engine"], "Discovery Engine")
        self.assertIn("reddit", card["sources_covered"])


if __name__ == "__main__":
    unittest.main()
