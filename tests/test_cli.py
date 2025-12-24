"""Tests for google_scholar_tool.cli module.

Tests CLI commands for Google Scholar queries including help and
validation functionality.

Note: This code was generated with assistance from AI coding tools
and has been reviewed and tested by a human.
"""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from google_scholar_tool.cli import main


class TestMainCommand:
    """Tests for the main CLI command."""

    def test_main_help(self) -> None:
        """Test that main --help shows usage info."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "Google Scholar CLI tool" in result.output
        assert "search" in result.output
        assert "author" in result.output

    def test_main_version(self) -> None:
        """Test that --version shows version info."""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_main_no_command_shows_help(self) -> None:
        """Test that running without command shows help."""
        runner = CliRunner()
        result = runner.invoke(main, [])

        assert result.exit_code == 0
        assert "Google Scholar CLI tool" in result.output


class TestSearchCommand:
    """Tests for the search subcommand."""

    def test_search_help(self) -> None:
        """Test that search --help shows usage info."""
        runner = CliRunner()
        result = runner.invoke(main, ["search", "--help"])

        assert result.exit_code == 0
        assert "Search Google Scholar" in result.output
        assert "--exact" in result.output
        assert "--intitle" in result.output

    def test_search_missing_query(self) -> None:
        """Test that missing query shows error with fix suggestion."""
        runner = CliRunner()
        result = runner.invoke(main, ["search"])

        assert result.exit_code == 1
        assert "Error:" in result.output
        assert "Fix:" in result.output

    @patch("google_scholar_tool.cli.search_publications")
    def test_search_executes(self, mock_search: MagicMock) -> None:
        """Test executing search."""
        mock_search.return_value = iter([])

        runner = CliRunner()
        result = runner.invoke(main, ["search", "test"])

        assert result.exit_code == 0
        mock_search.assert_called_once()

    @patch("google_scholar_tool.cli.search_publications")
    def test_search_json_output(self, mock_search: MagicMock) -> None:
        """Test JSON output format."""
        from google_scholar_tool.scholar import Publication

        mock_pub = Publication(
            title="Test Paper",
            authors=["Author"],
            year="2024",
            abstract="Abstract",
            citations=10,
            url=None,
            pub_url=None,
        )
        mock_search.return_value = iter([mock_pub])

        runner = CliRunner()
        result = runner.invoke(main, ["search", "test", "--json-output"])

        assert result.exit_code == 0
        assert '"title": "Test Paper"' in result.output

    @patch("google_scholar_tool.cli.search_publications")
    def test_search_with_exact(self, mock_search: MagicMock) -> None:
        """Test search with exact phrase option."""
        mock_search.return_value = iter([])

        runner = CliRunner()
        result = runner.invoke(main, ["search", "HRM", "--exact", "job satisfaction"])

        assert result.exit_code == 0
        mock_search.assert_called_once()

    @patch("google_scholar_tool.cli.search_publications")
    def test_search_with_intitle(self, mock_search: MagicMock) -> None:
        """Test search with intitle option."""
        mock_search.return_value = iter([])

        runner = CliRunner()
        result = runner.invoke(
            main,
            ["search", "HRM", "--exact", "job satisfaction", "--intitle", "Netherlands"],
        )

        assert result.exit_code == 0
        mock_search.assert_called_once()


class TestAuthorCommand:
    """Tests for the author subcommand."""

    def test_author_help(self) -> None:
        """Test that author --help shows usage info."""
        runner = CliRunner()
        result = runner.invoke(main, ["author", "--help"])

        assert result.exit_code == 0
        assert "Search Google Scholar for authors" in result.output
        assert "--scholar-id" in result.output

    def test_author_missing_query_and_id(self) -> None:
        """Test that missing query and ID shows error with fix suggestion."""
        runner = CliRunner()
        result = runner.invoke(main, ["author"])

        assert result.exit_code == 1
        assert "Error:" in result.output
        assert "Fix:" in result.output

    @patch("google_scholar_tool.cli.search_authors")
    def test_author_executes(self, mock_search: MagicMock) -> None:
        """Test executing author search."""
        mock_search.return_value = iter([])

        runner = CliRunner()
        result = runner.invoke(main, ["author", "Test"])

        assert result.exit_code == 0
        mock_search.assert_called_once()


class TestQuietMode:
    """Tests for quiet mode."""

    @patch("google_scholar_tool.cli.search_publications")
    def test_search_quiet(self, mock_search: MagicMock) -> None:
        """Test that quiet mode suppresses output."""
        mock_search.return_value = iter([])

        runner = CliRunner()
        result = runner.invoke(main, ["-q", "search", "test"])

        assert result.exit_code == 0
        assert result.output == ""

    @patch("google_scholar_tool.cli.search_authors")
    def test_author_quiet(self, mock_search: MagicMock) -> None:
        """Test that quiet mode suppresses author output."""
        mock_search.return_value = iter([])

        runner = CliRunner()
        result = runner.invoke(main, ["-q", "author", "test"])

        assert result.exit_code == 0
        assert result.output == ""
