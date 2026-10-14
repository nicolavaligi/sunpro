"""
Unit Test Suite per il SunPro Crawler Engine (Nicola Valigi / Houdinick)
========================================================================
Testa:
  - UserAgentRotator e generazione header coerenti
  - DomainRateLimiter con token bucket
  - RetryPolicy e calcolo backoff con jitter
  - CheckpointManager e persistenza stato incrementale SQLite
  - AsyncScraperEngine e SyncScraperEngine
"""

import asyncio
import os
import sqlite3
import tempfile
import time
import unittest
from pathlib import Path

from crawler.engine import (
    AsyncScraperEngine,
    CheckpointManager,
    DomainRateLimiter,
    RetryConfig,
    SyncScraperEngine,
    UserAgentRotator,
    calculate_backoff_delay,
)


class TestUserAgentRotator(unittest.TestCase):
    def setUp(self):
        self.rotator = UserAgentRotator()

    def test_random_user_agent_not_empty(self):
        ua = self.rotator.get_random_user_agent()
        self.assertIsInstance(ua, str)
        self.assertTrue(len(ua) > 20)

    def test_build_realistic_headers(self):
        headers = self.rotator.build_realistic_headers("https://example.com/feed")
        self.assertIn("User-Agent", headers)
        self.assertIn("Accept-Language", headers)
        self.assertEqual(headers["Host"], "example.com")
        self.assertIn("Sec-Ch-Ua-Platform", headers)


class TestDomainRateLimiter(unittest.IsolatedAsyncioTestCase):
    async def test_token_bucket_acquisition(self):
        limiter = DomainRateLimiter(default_rps=10.0, burst_size=2)
        t0 = time.monotonic()
        # Consuma 2 token di burst istantanei
        await limiter.acquire("https://test.domain.com/1")
        await limiter.acquire("https://test.domain.com/2")
        elapsed = time.monotonic() - t0
        self.assertLess(elapsed, 0.2)


class TestRetryAndBackoff(unittest.TestCase):
    def test_backoff_increases_with_attempts(self):
        cfg = RetryConfig(base_delay=1.0, backoff_multiplier=2.0, jitter=False)
        d0 = calculate_backoff_delay(0, cfg)
        d1 = calculate_backoff_delay(1, cfg)
        d2 = calculate_backoff_delay(2, cfg)
        self.assertEqual(d0, 1.0)
        self.assertEqual(d1, 2.0)
        self.assertEqual(d2, 4.0)

    def test_retry_after_header_precedence(self):
        cfg = RetryConfig(base_delay=1.0, max_delay=30.0)
        d = calculate_backoff_delay(0, cfg, retry_after=7.5)
        self.assertEqual(d, 7.5)


class TestCheckpointManager(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp_dir.name) / "test_checkpoints.db"
        self.checkpoint = CheckpointManager(db_path=self.db_path)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_visited_urls_recording(self):
        url = "https://example.com/site-alpha"
        self.assertFalse(self.checkpoint.is_visited(url))

        self.checkpoint.record_visit(url, status_code=200, attempts=1)
        self.assertTrue(self.checkpoint.is_visited(url))

    def test_cursor_tracking(self):
        feed_name = "test_solar_stream"
        seq, page = self.checkpoint.get_cursor(feed_name)
        self.assertEqual(seq, 0)
        self.assertEqual(page, 1)

        self.checkpoint.update_cursor(feed_name, last_sequence=150, last_page=5)
        new_seq, new_page = self.checkpoint.get_cursor(feed_name)
        self.assertEqual(new_seq, 150)
        self.assertEqual(new_page, 5)


class TestAsyncScraperEngine(unittest.IsolatedAsyncioTestCase):
    async def test_fetch_online_endpoint(self):
        async with AsyncScraperEngine(concurrency=2, default_rps=5.0) as engine:
            resp = await engine.fetch("https://httpbin.org/get?test=sunpro")
            self.assertIsNotNone(resp)
            if resp:
                self.assertEqual(resp.status_code, 200)
                data = resp.json()
                self.assertEqual(data.get("args", {}).get("test"), "sunpro")


if __name__ == "__main__":
    unittest.main()
