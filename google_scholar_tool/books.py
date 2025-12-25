"""Google Books API query functionality.

This module provides functions for searching Google Books using the Google Books API.
Requires GOOGLE_BOOKS_API_KEY environment variable to be set.
"""

import json
import os
import urllib.parse
import urllib.request
from collections.abc import Iterator
from dataclasses import dataclass

from google_scholar_tool.logging_config import get_logger

logger = get_logger(__name__)

GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"


@dataclass
class Book:
    """Represents a Google Books volume."""

    title: str
    authors: list[str]
    publisher: str | None
    published_date: str | None
    description: str | None
    page_count: int | None
    categories: list[str]
    preview_link: str | None
    info_link: str | None
    isbn_10: str | None = None
    isbn_13: str | None = None

    @property
    def year(self) -> str:
        """Extract year from published_date."""
        if self.published_date:
            return self.published_date[:4]
        return "n.d."

    @property
    def isbn(self) -> str | None:
        """Return ISBN-13 if available, else ISBN-10."""
        return self.isbn_13 or self.isbn_10

    def _format_authors_apa(self) -> str:
        """Format authors for APA style: Last, F. M., & Last, F. M."""
        if not self.authors:
            return "Unknown Author"
        formatted = []
        for author in self.authors:
            parts = author.split()
            if len(parts) >= 2:
                last = parts[-1]
                initials = " ".join(f"{p[0]}." for p in parts[:-1])
                formatted.append(f"{last}, {initials}")
            else:
                formatted.append(author)
        if len(formatted) == 1:
            return formatted[0]
        if len(formatted) == 2:
            return f"{formatted[0]} & {formatted[1]}"
        return ", ".join(formatted[:-1]) + f", & {formatted[-1]}"

    def _format_authors_mla(self) -> str:
        """Format authors for MLA style: Last, First, and First Last."""
        if not self.authors:
            return "Unknown Author"
        if len(self.authors) == 1:
            parts = self.authors[0].split()
            if len(parts) >= 2:
                return f"{parts[-1]}, {' '.join(parts[:-1])}"
            return self.authors[0]
        if len(self.authors) == 2:
            first = self.authors[0].split()
            first_formatted = (
                f"{first[-1]}, {' '.join(first[:-1])}" if len(first) >= 2 else first[0]
            )
            return f"{first_formatted}, and {self.authors[1]}"
        first = self.authors[0].split()
        first_formatted = f"{first[-1]}, {' '.join(first[:-1])}" if len(first) >= 2 else first[0]
        return f"{first_formatted}, et al."

    def _format_authors_chicago(self) -> str:
        """Format authors for Chicago style: Last, First, and First Last."""
        return self._format_authors_mla()  # Same as MLA for books

    def _format_authors_harvard(self) -> str:
        """Format authors for Harvard style: Last, F.M. and Last, F.M."""
        if not self.authors:
            return "Unknown Author"
        formatted = []
        for author in self.authors:
            parts = author.split()
            if len(parts) >= 2:
                last = parts[-1]
                initials = "".join(f"{p[0]}." for p in parts[:-1])
                formatted.append(f"{last}, {initials}")
            else:
                formatted.append(author)
        if len(formatted) == 1:
            return formatted[0]
        if len(formatted) == 2:
            return f"{formatted[0]} and {formatted[1]}"
        return ", ".join(formatted[:-1]) + f" and {formatted[-1]}"

    def cite_apa(self) -> str:
        """Generate APA 7th edition citation.

        Format: Author, A. A. (Year). Title of work: Capital letter for subtitle.
                Publisher.
        """
        authors = self._format_authors_apa()
        publisher = self.publisher or "Publisher unknown"
        return f"{authors} ({self.year}). {self.title}. {publisher}."

    def cite_mla(self) -> str:
        """Generate MLA 9th edition citation.

        Format: Last, First. Title of Work. Publisher, Year.
        """
        authors = self._format_authors_mla()
        publisher = self.publisher or "Publisher unknown"
        # Handle "et al." which already ends with a period
        sep = " " if authors.endswith(".") else ". "
        return f"{authors}{sep}{self.title}. {publisher}, {self.year}."

    def cite_chicago(self) -> str:
        """Generate Chicago 17th edition citation (Notes-Bibliography).

        Format: Last, First. Title of Work. Place: Publisher, Year.
        """
        authors = self._format_authors_chicago()
        publisher = self.publisher or "Publisher unknown"
        # Handle "et al." which already ends with a period
        sep = " " if authors.endswith(".") else ". "
        return f"{authors}{sep}{self.title}. {publisher}, {self.year}."

    def cite_harvard(self) -> str:
        """Generate Harvard citation.

        Format: Last, F.M. (Year) Title of work. Publisher.
        """
        authors = self._format_authors_harvard()
        publisher = self.publisher or "Publisher unknown"
        return f"{authors} ({self.year}) {self.title}. {publisher}."

    def cite(self, style: str = "apa") -> str:
        """Generate citation in specified style.

        Args:
            style: Citation style - 'apa', 'mla', 'chicago', or 'harvard'

        Returns:
            Formatted citation string

        Raises:
            ValueError: If style is not supported
        """
        styles = {
            "apa": self.cite_apa,
            "mla": self.cite_mla,
            "chicago": self.cite_chicago,
            "harvard": self.cite_harvard,
        }
        if style.lower() not in styles:
            raise ValueError(f"Unsupported style: {style}. Use: {', '.join(styles.keys())}")
        return styles[style.lower()]()

    def to_dict(self) -> dict[str, str | int | list[str] | None]:
        """Convert book to dictionary."""
        return {
            "title": self.title,
            "authors": self.authors,
            "publisher": self.publisher,
            "published_date": self.published_date,
            "description": self.description,
            "page_count": self.page_count,
            "categories": self.categories,
            "preview_link": self.preview_link,
            "info_link": self.info_link,
            "isbn_10": self.isbn_10,
            "isbn_13": self.isbn_13,
        }

    def to_json(self) -> str:
        """Convert book to JSON string."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


def get_api_key() -> str:
    """Get Google Books API key from environment.

    Returns:
        API key string

    Raises:
        ValueError: If GOOGLE_BOOKS_API_KEY is not set
    """
    api_key = os.environ.get("GOOGLE_BOOKS_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_BOOKS_API_KEY environment variable not set. "
            "Get an API key from https://console.developers.google.com/"
        )
    return api_key


def search_books(query: str, limit: int = 10) -> Iterator[Book]:
    """Search Google Books for volumes.

    Args:
        query: Search query string
        limit: Maximum number of results to return (max 40)

    Yields:
        Book objects matching the query

    Raises:
        ValueError: If API key is not set
        urllib.error.URLError: If network request fails

    Example:
        >>> for book in search_books("machine learning", limit=5):
        ...     print(book.title)
    """
    api_key = get_api_key()

    params = urllib.parse.urlencode(
        {
            "q": query,
            "key": api_key,
            "maxResults": min(limit, 40),  # API max is 40
        }
    )

    url = f"{GOOGLE_BOOKS_API_URL}?{params}"
    logger.info("Searching books: %s (limit=%d)", query, limit)
    logger.debug("Request URL: %s", url.replace(api_key, "***"))

    with urllib.request.urlopen(url) as response:  # nosec B310 - URL from constant HTTPS endpoint
        data = json.loads(response.read().decode("utf-8"))

    items = data.get("items", [])
    logger.info("Found %d books", len(items))

    for item in items:
        volume_info = item.get("volumeInfo", {})

        # Extract ISBNs from industry identifiers
        isbn_10 = None
        isbn_13 = None
        for identifier in volume_info.get("industryIdentifiers", []):
            if identifier.get("type") == "ISBN_10":
                isbn_10 = identifier.get("identifier")
            elif identifier.get("type") == "ISBN_13":
                isbn_13 = identifier.get("identifier")

        book = Book(
            title=volume_info.get("title", "Unknown"),
            authors=volume_info.get("authors", []),
            publisher=volume_info.get("publisher"),
            published_date=volume_info.get("publishedDate"),
            description=volume_info.get("description"),
            page_count=volume_info.get("pageCount"),
            categories=volume_info.get("categories", []),
            preview_link=volume_info.get("previewLink"),
            info_link=volume_info.get("infoLink"),
            isbn_10=isbn_10,
            isbn_13=isbn_13,
        )
        logger.debug("Found book: %s by %s", book.title, ", ".join(book.authors))
        yield book
