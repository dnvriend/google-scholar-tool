"""Google Scholar query functionality using the scholarly library.

This module provides functions for searching Google Scholar publications,
authors, and citations. It supports Boolean operators, exact phrase matching,
and advanced query syntax.

Note: This code was generated with assistance from AI coding tools
and has been reviewed and tested by a human.
"""

import json
from collections.abc import Iterator
from dataclasses import dataclass

from scholarly import scholarly  # type: ignore[import-untyped]

from google_scholar_tool.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class Publication:
    """Represents a Google Scholar publication."""

    title: str
    authors: list[str]
    year: str | None
    abstract: str | None
    citations: int
    url: str | None
    pub_url: str | None

    def to_dict(self) -> dict[str, str | int | list[str] | None]:
        """Convert publication to dictionary."""
        return {
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "abstract": self.abstract,
            "citations": self.citations,
            "url": self.url,
            "pub_url": self.pub_url,
        }

    def to_json(self) -> str:
        """Convert publication to JSON string."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


@dataclass
class Author:
    """Represents a Google Scholar author."""

    name: str
    affiliation: str | None
    email_domain: str | None
    citations: int
    h_index: int
    i10_index: int
    interests: list[str]
    scholar_id: str | None

    def to_dict(self) -> dict[str, str | int | list[str] | None]:
        """Convert author to dictionary."""
        return {
            "name": self.name,
            "affiliation": self.affiliation,
            "email_domain": self.email_domain,
            "citations": self.citations,
            "h_index": self.h_index,
            "i10_index": self.i10_index,
            "interests": self.interests,
            "scholar_id": self.scholar_id,
        }

    def to_json(self) -> str:
        """Convert author to JSON string."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


def build_query(
    terms: list[str],
    exact_phrases: list[str] | None = None,
    exclude_terms: list[str] | None = None,
    intitle: str | None = None,
) -> str:
    """Build a Google Scholar query string with Boolean operators.

    Args:
        terms: List of search terms to combine with OR
        exact_phrases: List of exact phrases (will be quoted)
        exclude_terms: List of terms to exclude (prefixed with -)
        intitle: Term that must appear in the title

    Returns:
        Formatted query string for Google Scholar

    Example:
        >>> build_query(
        ...     terms=["HRM", "human resource management"],
        ...     exact_phrases=["job satisfaction"],
        ...     intitle="the Netherlands"
        ... )
        '(HRM OR "human resource management") AND "job satisfaction" intitle:"the Netherlands"'
    """
    query_parts = []

    # Handle main terms with OR
    if terms:
        if len(terms) == 1:
            query_parts.append(terms[0])
        else:
            # Combine with OR
            or_terms = " OR ".join(terms)
            query_parts.append(f"({or_terms})")

    # Handle exact phrases
    if exact_phrases:
        for phrase in exact_phrases:
            if " " in phrase:
                query_parts.append(f'"{phrase}"')
            else:
                query_parts.append(phrase)

    # Combine with AND
    query = " AND ".join(query_parts) if len(query_parts) > 1 else "".join(query_parts)

    # Add intitle constraint
    if intitle:
        query += f' intitle:"{intitle}"'

    # Add exclusions
    if exclude_terms:
        for term in exclude_terms:
            query += f" -{term}"

    logger.debug("Built query: %s", query)
    return query


def search_publications(
    query: str,
    limit: int = 10,
    year_start: int | None = None,
    year_end: int | None = None,
) -> Iterator[Publication]:
    """Search Google Scholar for publications.

    Args:
        query: Search query string (supports Boolean operators)
        limit: Maximum number of results to return
        year_start: Filter results from this year onwards
        year_end: Filter results up to this year

    Yields:
        Publication objects matching the query

    Example:
        >>> for pub in search_publications('"machine learning" AND healthcare', limit=5):
        ...     print(pub.title)
    """
    logger.info("Searching publications: %s (limit=%d)", query, limit)

    search_query = scholarly.search_pubs(query, year_low=year_start, year_high=year_end)

    count = 0
    for result in search_query:
        if count >= limit:
            break

        bib = result.get("bib", {})
        pub = Publication(
            title=bib.get("title", "Unknown"),
            authors=bib.get("author", []),
            year=bib.get("pub_year"),
            abstract=bib.get("abstract"),
            citations=result.get("num_citations", 0),
            url=result.get("eprint_url"),
            pub_url=result.get("pub_url"),
        )
        logger.debug("Found publication: %s (%s)", pub.title, pub.year)
        yield pub
        count += 1

    logger.info("Found %d publications", count)


def search_authors(query: str, limit: int = 10) -> Iterator[Author]:
    """Search Google Scholar for authors.

    Args:
        query: Author name or keywords to search
        limit: Maximum number of results to return

    Yields:
        Author objects matching the query

    Example:
        >>> for author in search_authors("Albert Einstein", limit=3):
        ...     print(author.name, author.h_index)
    """
    logger.info("Searching authors: %s (limit=%d)", query, limit)

    search_query = scholarly.search_author(query)

    count = 0
    for result in search_query:
        if count >= limit:
            break

        author = Author(
            name=result.get("name", "Unknown"),
            affiliation=result.get("affiliation"),
            email_domain=result.get("email_domain"),
            citations=result.get("citedby", 0),
            h_index=result.get("hindex", 0),
            i10_index=result.get("i10index", 0),
            interests=result.get("interests", []),
            scholar_id=result.get("scholar_id"),
        )
        logger.debug("Found author: %s (h-index=%d)", author.name, author.h_index)
        yield author
        count += 1

    logger.info("Found %d authors", count)


def get_author_details(scholar_id: str) -> Author | None:
    """Get detailed information about an author by their Scholar ID.

    Args:
        scholar_id: Google Scholar author ID

    Returns:
        Author object with full details, or None if not found

    Example:
        >>> author = get_author_details("XrH4VJUAAAAJ")
        >>> print(author.name, author.citations)
    """
    logger.info("Getting author details for ID: %s", scholar_id)

    try:
        result = scholarly.search_author_id(scholar_id)
        result = scholarly.fill(result)

        author = Author(
            name=result.get("name", "Unknown"),
            affiliation=result.get("affiliation"),
            email_domain=result.get("email_domain"),
            citations=result.get("citedby", 0),
            h_index=result.get("hindex", 0),
            i10_index=result.get("i10index", 0),
            interests=result.get("interests", []),
            scholar_id=result.get("scholar_id"),
        )
        return author
    except Exception as e:
        logger.error("Failed to get author details: %s", e)
        return None
