"""Tests for google_scholar_tool.scholar module.

Tests the query building functionality and dataclasses for Google Scholar
integration. Network-dependent tests are marked for optional execution.

Note: This code was generated with assistance from AI coding tools
and has been reviewed and tested by a human.
"""

import json
from unittest.mock import MagicMock, patch

from google_scholar_tool.scholar import (
    Author,
    Publication,
    build_query,
    search_authors,
    search_publications,
)


class TestBuildQuery:
    """Tests for the build_query function."""

    def test_single_term(self) -> None:
        """Test query with a single search term."""
        result = build_query(terms=["machine learning"])
        assert result == "machine learning"

    def test_multiple_terms_with_or(self) -> None:
        """Test query with multiple terms combined with OR."""
        result = build_query(terms=["HRM", "human resource management"])
        assert result == "(HRM OR human resource management)"

    def test_exact_phrase(self) -> None:
        """Test query with exact phrase matching."""
        result = build_query(terms=["HRM"], exact_phrases=["job satisfaction"])
        assert result == 'HRM AND "job satisfaction"'

    def test_multiple_exact_phrases(self) -> None:
        """Test query with multiple exact phrases."""
        result = build_query(
            terms=["AI"],
            exact_phrases=["machine learning", "deep learning"],
        )
        assert result == 'AI AND "machine learning" AND "deep learning"'

    def test_intitle_filter(self) -> None:
        """Test query with intitle filter."""
        result = build_query(
            terms=["HRM"],
            exact_phrases=["job satisfaction"],
            intitle="the Netherlands",
        )
        assert result == 'HRM AND "job satisfaction" intitle:"the Netherlands"'

    def test_exclude_terms(self) -> None:
        """Test query with excluded terms."""
        result = build_query(
            terms=["machine learning"],
            exclude_terms=["education"],
        )
        assert result == "machine learning -education"

    def test_multiple_exclude_terms(self) -> None:
        """Test query with multiple excluded terms."""
        result = build_query(
            terms=["AI"],
            exclude_terms=["education", "healthcare"],
        )
        assert result == "AI -education -healthcare"

    def test_complex_query(self) -> None:
        """Test complex query with all features combined."""
        result = build_query(
            terms=["HRM", "human resource management"],
            exact_phrases=["job satisfaction"],
            intitle="the Netherlands",
            exclude_terms=["education"],
        )
        expected = (
            '(HRM OR human resource management) AND "job satisfaction" '
            'intitle:"the Netherlands" -education'
        )
        assert result == expected

    def test_hrm_job_satisfaction_example(self) -> None:
        """Test the HRM and job satisfaction example from course material."""
        result = build_query(
            terms=["human resource management", "HRM"],
            exact_phrases=["job satisfaction"],
        )
        assert '"job satisfaction"' in result
        assert "OR" in result


class TestPublication:
    """Tests for the Publication dataclass."""

    def test_publication_creation(self) -> None:
        """Test creating a Publication instance."""
        pub = Publication(
            title="Test Paper",
            authors=["Author One", "Author Two"],
            year="2024",
            abstract="This is a test abstract.",
            citations=100,
            url="https://example.com/paper.pdf",
            pub_url="https://example.com/paper",
        )
        assert pub.title == "Test Paper"
        assert len(pub.authors) == 2
        assert pub.citations == 100

    def test_publication_to_dict(self) -> None:
        """Test converting Publication to dictionary."""
        pub = Publication(
            title="Test Paper",
            authors=["Author One"],
            year="2024",
            abstract=None,
            citations=50,
            url=None,
            pub_url=None,
        )
        result = pub.to_dict()
        assert result["title"] == "Test Paper"
        assert result["authors"] == ["Author One"]
        assert result["citations"] == 50
        assert result["abstract"] is None

    def test_publication_to_json(self) -> None:
        """Test converting Publication to JSON."""
        pub = Publication(
            title="Test Paper",
            authors=["Author One"],
            year="2024",
            abstract="Test",
            citations=10,
            url=None,
            pub_url=None,
        )
        result = pub.to_json()
        parsed = json.loads(result)
        assert parsed["title"] == "Test Paper"


class TestAuthor:
    """Tests for the Author dataclass."""

    def test_author_creation(self) -> None:
        """Test creating an Author instance."""
        author = Author(
            name="John Doe",
            affiliation="Test University",
            email_domain="test.edu",
            citations=1000,
            h_index=20,
            i10_index=50,
            interests=["AI", "ML"],
            scholar_id="ABC123",
        )
        assert author.name == "John Doe"
        assert author.h_index == 20
        assert len(author.interests) == 2

    def test_author_to_dict(self) -> None:
        """Test converting Author to dictionary."""
        author = Author(
            name="Jane Doe",
            affiliation=None,
            email_domain=None,
            citations=500,
            h_index=15,
            i10_index=30,
            interests=[],
            scholar_id=None,
        )
        result = author.to_dict()
        assert result["name"] == "Jane Doe"
        assert result["affiliation"] is None
        assert result["citations"] == 500

    def test_author_to_json(self) -> None:
        """Test converting Author to JSON."""
        author = Author(
            name="Test Author",
            affiliation="University",
            email_domain="uni.edu",
            citations=100,
            h_index=5,
            i10_index=10,
            interests=["Research"],
            scholar_id="XYZ789",
        )
        result = author.to_json()
        parsed = json.loads(result)
        assert parsed["name"] == "Test Author"
        assert parsed["h_index"] == 5


class TestSearchPublications:
    """Tests for the search_publications function with mocked scholarly."""

    @patch("google_scholar_tool.scholar.scholarly")
    def test_search_publications_basic(self, mock_scholarly: MagicMock) -> None:
        """Test basic publication search with mocked results."""
        mock_result = {
            "bib": {
                "title": "Test Paper",
                "author": ["Author One"],
                "pub_year": "2024",
                "abstract": "Test abstract",
            },
            "num_citations": 100,
            "eprint_url": "https://example.com/paper.pdf",
            "pub_url": "https://example.com/paper",
        }
        mock_scholarly.search_pubs.return_value = iter([mock_result])

        results = list(search_publications("test query", limit=1))

        assert len(results) == 1
        assert results[0].title == "Test Paper"
        assert results[0].citations == 100

    @patch("google_scholar_tool.scholar.scholarly")
    def test_search_publications_limit(self, mock_scholarly: MagicMock) -> None:
        """Test that limit is respected."""
        mock_results = [
            {"bib": {"title": f"Paper {i}", "author": []}, "num_citations": i} for i in range(10)
        ]
        mock_scholarly.search_pubs.return_value = iter(mock_results)

        results = list(search_publications("test", limit=3))

        assert len(results) == 3

    @patch("google_scholar_tool.scholar.scholarly")
    def test_search_publications_empty(self, mock_scholarly: MagicMock) -> None:
        """Test handling of empty results."""
        mock_scholarly.search_pubs.return_value = iter([])

        results = list(search_publications("nonexistent query", limit=10))

        assert len(results) == 0


class TestSearchAuthors:
    """Tests for the search_authors function with mocked scholarly."""

    @patch("google_scholar_tool.scholar.scholarly")
    def test_search_authors_basic(self, mock_scholarly: MagicMock) -> None:
        """Test basic author search with mocked results."""
        mock_result = {
            "name": "Test Author",
            "affiliation": "Test University",
            "email_domain": "test.edu",
            "citedby": 1000,
            "hindex": 20,
            "i10index": 50,
            "interests": ["AI", "ML"],
            "scholar_id": "ABC123",
        }
        mock_scholarly.search_author.return_value = iter([mock_result])

        results = list(search_authors("Test Author", limit=1))

        assert len(results) == 1
        assert results[0].name == "Test Author"
        assert results[0].h_index == 20

    @patch("google_scholar_tool.scholar.scholarly")
    def test_search_authors_empty(self, mock_scholarly: MagicMock) -> None:
        """Test handling of empty author results."""
        mock_scholarly.search_author.return_value = iter([])

        results = list(search_authors("nonexistent author", limit=10))

        assert len(results) == 0
