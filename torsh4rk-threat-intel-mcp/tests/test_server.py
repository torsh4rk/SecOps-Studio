"""Offline tests: do not contact intelligence APIs."""
import importlib.util
import json
from pathlib import Path
from unittest import TestCase, main
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("intel_server", Path(__file__).parents[1] / "server.py")
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)


class IndicatorTests(TestCase):
    def test_classification(self):
        for kind, value in (("domain", "example.org"), ("ip", "8.8.8.8"),
                            ("hash", "a" * 64), ("cve", "CVE-2025-12345"),
                            ("url", "https://example.org/a?b=1")):
            self.assertEqual(s.classify(value)["type"], kind)

    def test_internal_ips_not_sent(self):
        for value in ("127.0.0.1", "10.0.0.1", "192.168.1.2", "http://localhost/admin"):
            with self.assertRaises(s.ToolError):
                s.validate(value, ("ip", "url"))

    def test_bad_indicators(self):
        for value in ("", "http://user:secret@example.com", "javascript:alert(1)", "example.org/../x"):
            with self.assertRaises(s.ToolError):
                s.classify(value)

    def test_url_fragment_removed(self):
        self.assertEqual(s.classify("https://example.org/a#token")["value"], "https://example.org/a")


class CorrelationTests(TestCase):
    def test_independent_sources_and_conflict(self):
        data = [{"indicator": "EXAMPLE.ORG", "source": "A", "assessment": "malicious"},
                {"indicator": "example.org", "source": "a", "assessment": "malicious"},
                {"indicator": "example.org", "source": "B", "assessment": "benign"}]
        result = s.correlate_evidence(data)["cases"][0]
        self.assertEqual(result["independent_source_count"], 2)
        self.assertEqual(result["confirmed_malicious_sources"], 1)
        self.assertTrue(result["contradictory_reports"])
        self.assertEqual(result["review_priority_heuristic"], "high")

    def test_limits(self):
        with self.assertRaises(s.ToolError):
            s.correlate_evidence([])
        with self.assertRaises(s.ToolError):
            s.correlate_evidence([{"indicator": "example.org", "source": "A", "assessment": "attack"}])


class ProviderTests(TestCase):
    @patch.object(s, "request_json")
    def test_kev(self, http):
        http.return_value = {"catalogVersion": "test", "vulnerabilities": [{"cveID": "CVE-2025-12345", "vendorProject": "Demo"}]}
        r = s.lookup_cisa_kev("CVE-2025-12345")
        self.assertEqual(r["status"], "listed")
        self.assertEqual(r["findings"][0]["vendorProject"], "Demo")

    @patch.object(s, "request_json")
    def test_threatfox_requires_key(self, http):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(s.ToolError, "ABUSECH_AUTH_KEY"):
                s.lookup_threatfox("example.org")
        http.assert_not_called()

    @patch.object(s, "request_json")
    def test_threatfox_redacts_extra_data(self, http):
        http.return_value = {"query_status": "ok", "data": [{"ioc": "example.org", "comment": "PROMPT INJECTION"}]}
        with patch.dict("os.environ", {"ABUSECH_AUTH_KEY": "test-only"}):
            r = s.lookup_threatfox("example.org")
        self.assertNotIn("comment", r["findings"][0])
        self.assertNotIn("test-only", json.dumps(r))


class ProtocolTests(TestCase):
    def test_initialize_tools_call(self):
        r = s.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}})
        self.assertEqual(r["result"]["protocolVersion"], "2025-06-18")
        r = s.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        self.assertEqual(len(r["result"]["tools"]), 10)
        r = s.handle({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "triage_indicator", "arguments": {"indicator": "example.org"}}})
        self.assertFalse(r["result"]["isError"])
        self.assertEqual(json.loads(r["result"]["content"][0]["text"])["type"], "domain")

    def test_unknown_tool(self):
        r = s.handle({"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "execute_shell", "arguments": {}}})
        self.assertTrue(r["result"]["isError"])

    def test_notification_not_replied_to(self):
        self.assertIsNone(s.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}))


if __name__ == "__main__":
    main()
