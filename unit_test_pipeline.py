import unittest
from unittest.mock import patch, MagicMock
import pipeline

class TestPipeline(unittest.TestCase):

    def setUp(self):
        # Prepare mock raw text mimicking an arXiv HTML text conversion
        self.sample_raw_text = (
            "Report GitHub Issue\n"
            "Back to arXiv\n"
            "Some stray title or authors here\n"
            "Abstract\n"
            "This is a cool abstract about AI.\n"
            "1. Introduction\n"
            "This is the beginning of the real paper content.\n"
            "It has multiple sentences and paragraph blocks.\n"
            "2. Methodology\n"
            "Here is how we built the system.\n"
            "References\n"
            "1. Author A, et al. 2026.\n"
            "2. Author B, et al. 2025."
        )

    # -------------------------------------------------------------------------
    # 1. Tests for fetch_html_body_content (I/O & Mocking)
    # -------------------------------------------------------------------------
    @patch("pipeline.requests.get")
    def test_fetch_html_body_content_success(self, mock_get):
        # Simulate a successful HTTP response containing a <body> tag
        mock_response = MagicMock()
        # Explicitly separate strings using tags to ensure predictable .stripped_strings behavior
        mock_response.text = "<html><body><div>  Hello  </div><div>  World  </div></body></html>"
        mock_get.return_value = mock_response

        text, status = pipeline.fetch_html_body_content("http://fakeurl.com")
        
        self.assertEqual(status, "html_success")
        self.assertEqual(text, "Hello\nWorld")

    @patch("pipeline.requests.get")
    def test_fetch_html_body_content_no_body(self, mock_get):
        # Simulate a response missing the <body> tag
        mock_response = MagicMock()
        mock_response.text = "<html><head></head></html>"
        mock_get.return_value = mock_response

        text, status = pipeline.fetch_html_body_content("http://fakeurl.com")
        
        self.assertIsNone(text)
        self.assertEqual(status, "no_body")

    @patch("pipeline.requests.get")
    def test_fetch_html_body_content_fail(self, mock_get):
        # Simulate an HTTP request exception (e.g., timeout)
        mock_get.side_effect = Exception("Connection timeout")

        text, status = pipeline.fetch_html_body_content("http://fakeurl.com")
        
        self.assertIsNone(text)
        self.assertEqual(status, "html_fetch_failed")

    # -------------------------------------------------------------------------
    # 2. Tests for Internal Cleaning Utilities
    # -------------------------------------------------------------------------
    def test_strip_boilerplate(self):
        lines = [
            "Report GitHub Issue",  # Should be filtered (exact/substring)
            "1",                    # Bare number, should be filtered
            "This is a long sentence that should act as the body start phase detection because it has lowercase letters.",
            "Back to arXiv",        # Substring boilerplate, should be filtered
            "Real Content Line",
            "2.1"                   # Bare section number, should be filtered
        ]
        cleaned = pipeline._strip_boilerplate(lines)
        
        # Verify boilerplate and bare section components are correctly dropped
        self.assertIn("Real Content Line", cleaned)
        self.assertNotIn("Report GitHub Issue", cleaned)
        self.assertNotIn("Back to arXiv", cleaned)
        self.assertNotIn("1", cleaned)
        self.assertNotIn("2.1", cleaned)

    def test_strip_front_matter(self):
        lines = [
            "Title of Paper",
            "Authors",
            "Abstract text...",
            "1 Introduction",  # Target intro heading
            "Body paragraph 1"
        ]
        cleaned = pipeline._strip_front_matter(lines)
        # Should truncate everything before "1 Introduction"
        self.assertEqual(cleaned[0], "1 Introduction")
        self.assertEqual(len(cleaned), 2)

    def test_trim_end_matter_safezone(self):
        # Create 10 lines. 30% safe zone = index 0, 1, and 2.
        # Placing "References" at index 1 means it is strictly inside the safe zone.
        lines = [
            "1. Introduction",
            "References",      # Index 1 (< 3 safe_zone_limit)
            "Line 2",
            "Line 3",
            "Line 4",
            "Line 5",
            "Line 6",
            "Line 7",
            "Line 8",
            "Line 9",
        ]
        cleaned = pipeline._trim_end_matter(lines)
        # Safe zone guard should prevent truncation completely
        self.assertEqual(len(cleaned), len(lines))

    def test_trim_end_matter_cut(self):
        # Create a document long enough so "References" falls outside the safe zone
        lines = ["Line"] * 50 + ["References", "Citation 1", "Citation 2"]
        cleaned = pipeline._trim_end_matter(lines)
        # Truncation should occur right before "References"
        self.assertEqual(len(cleaned), 50)
        self.assertNotIn("References", cleaned)

    # -------------------------------------------------------------------------
    # 3. Tests for Public Endpoints
    # -------------------------------------------------------------------------
    def test_get_article_snippet_without_abstract(self):
        # Should clean boilerplate, front matter (including Abstract), and end-matter
        snippet = pipeline.get_article_snippet_without_abstract(self.sample_raw_text)
        
        self.assertIn("1. Introduction", snippet)
        self.assertIn("2. Methodology", snippet)
        self.assertNotIn("Abstract", snippet)
        self.assertNotIn("References", snippet)
        self.assertNotIn("Report GitHub Issue", snippet)

    def test_get_article_snippet_with_abstract(self):
        # Should clean boilerplate and end-matter, but preserve front matter/Abstract
        snippet = pipeline.get_article_snippet_with_abstract(self.sample_raw_text)
        
        self.assertIn("Abstract", snippet)
        self.assertIn("1. Introduction", snippet)
        self.assertNotIn("References", snippet)
        self.assertNotIn("Report GitHub Issue", snippet)

    def test_empty_input(self):
        # Guard against empty or None edge cases
        self.assertEqual(pipeline.get_article_snippet_without_abstract(""), "")
        self.assertEqual(pipeline.get_article_snippet_with_abstract(None), "")


if __name__ == "__main__":
    unittest.main()