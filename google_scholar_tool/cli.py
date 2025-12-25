"""CLI entry point for google-scholar-tool.

This CLI tool provides commands for querying Google Scholar for academic
publications and authors. Supports Boolean operators, exact phrases, and
advanced query syntax.

Note: This code was generated with assistance from AI coding tools
and has been reviewed and tested by a human.
"""

import json
import os
import sys
import warnings

# Suppress SyntaxWarnings from scholarly library before importing it
warnings.filterwarnings("ignore", category=SyntaxWarning, module="scholarly")

import click  # noqa: E402

from google_scholar_tool.books import Book, search_books  # noqa: E402
from google_scholar_tool.completion import completion_command  # noqa: E402
from google_scholar_tool.logging_config import get_logger, setup_logging  # noqa: E402
from google_scholar_tool.scholar import (  # noqa: E402
    Author,
    Publication,
    build_query,
    get_author_details,
    search_authors,
    search_publications,
)

logger = get_logger(__name__)


def hyperlink(url: str, text: str | None = None) -> str:
    """Create a clickable terminal hyperlink using OSC 8 escape sequence.

    Works in most modern terminals (iTerm2, Terminal.app, Windows Terminal, etc.).

    Args:
        url: The URL to link to
        text: Display text (defaults to URL if not provided)

    Returns:
        Clickable hyperlink string or plain text if terminal doesn't support colors
    """
    display = text or url
    # Check if terminal supports colors/escape sequences
    if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
        return f"{display} ({url})" if text else url
    # OSC 8 hyperlink format: \033]8;;URL\033\\TEXT\033]8;;\033\\
    return f"\033]8;;{url}\033\\{display}\033]8;;\033\\"


@click.group(invoke_without_command=True)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Enable verbose output (use -v for INFO, -vv for DEBUG, -vvv for TRACE)",
)
@click.option("-q", "--quiet", is_flag=True, help="Suppress all output except errors")
@click.version_option(version="0.1.0")
@click.pass_context
def main(ctx: click.Context, verbose: int, quiet: bool) -> None:
    """Google Scholar CLI tool for academic research queries.

    Query Google Scholar for publications and authors using Boolean operators
    and advanced search syntax.

    Examples:

    \b
        # Search for publications
        google-scholar-tool search "machine learning"

    \b
        # Raw Google Scholar query
        google-scholar-tool search '"HRM" AND "job satisfaction" intitle:"Netherlands"'

    \b
        # Search for authors
        google-scholar-tool author "Albert Einstein"
    """
    # Ensure context object exists for passing data to subcommands
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet

    # Setup logging based on verbosity count
    if quiet:
        setup_logging(-1)  # Suppress all except errors
    else:
        setup_logging(verbose)

    # If no subcommand is provided, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command("search")
@click.argument("query", required=False)
@click.option("-e", "--exact", multiple=True, help="Exact phrase to include (can repeat)")
@click.option("-x", "--exclude", multiple=True, help="Term to exclude (can repeat)")
@click.option("-t", "--intitle", help="Term that must appear in title")
@click.option("-l", "--limit", default=10, show_default=True, help="Maximum results to return")
@click.option("--year-start", type=int, help="Filter results from this year onwards")
@click.option("--year-end", type=int, help="Filter results up to this year")
@click.option(
    "--sort",
    type=click.Choice(["relevance", "date"], case_sensitive=False),
    default="relevance",
    show_default=True,
    help="Sort results by relevance or date (newest first)",
)
@click.option("-j", "--json-output", is_flag=True, help="Output results as JSON")
@click.option("-s", "--stdin", is_flag=True, help="Read query from stdin")
@click.pass_context
def search_cmd(
    ctx: click.Context,
    query: str | None,
    exact: tuple[str, ...],
    exclude: tuple[str, ...],
    intitle: str | None,
    limit: int,
    year_start: int | None,
    year_end: int | None,
    sort: str,
    json_output: bool,
    stdin: bool,
) -> None:
    """Search Google Scholar for publications.

    Supports Boolean operators (AND, OR), exact phrases, exclusions,
    and title filters. Use raw Google Scholar query syntax.

    Examples:

    \b
        # Basic search
        google-scholar-tool search "machine learning"

    \b
        # Raw Google Scholar query with operators
        google-scholar-tool search '"HRM" AND "job satisfaction" intitle:"Netherlands"'

    \b
        # Using helper options
        google-scholar-tool search "HRM" --exact "job satisfaction"

    \b
        # Filter by year range
        google-scholar-tool search "deep learning" --year-start 2020 --year-end 2024

    \b
        # Sort by date (newest first)
        google-scholar-tool search "transformers" --sort date --limit 5

    \b
        # Output as JSON
        google-scholar-tool search "AI" --json-output --limit 5

    \b
    Output Format (JSON):
        [{"title": "...", "authors": [...], "year": "2024",
          "abstract": "...", "citations": 100, "url": "..."}]
    """
    quiet = ctx.obj.get("quiet", False)

    # Handle stdin input
    if stdin:
        if not sys.stdin.isatty():
            query = sys.stdin.read().strip()
        else:
            click.echo("Error: --stdin specified but no input provided", err=True)
            click.echo("Fix: echo 'query' | google-scholar-tool search --stdin", err=True)
            ctx.exit(1)

    # Validate query
    if not query:
        click.echo("Error: Missing query argument", err=True)
        click.echo(
            "Fix: Provide a search query, e.g.: google-scholar-tool search 'machine learning'",
            err=True,
        )
        ctx.exit(1)

    # Build enhanced query if extra options provided
    if exact or exclude or intitle:
        # Parse query for OR terms
        terms = [t.strip() for t in query.split(" OR ")] if " OR " in query else [query]
        final_query = build_query(
            terms=terms,
            exact_phrases=list(exact) if exact else None,
            exclude_terms=list(exclude) if exclude else None,
            intitle=intitle,
        )
    else:
        final_query = query

    # Execute search
    logger.info("Executing search: %s", final_query)
    results: list[Publication] = list(
        search_publications(
            final_query,
            limit=limit,
            year_start=year_start,
            year_end=year_end,
            sort_by=sort,
        )
    )

    if not results:
        if not quiet:
            click.echo("No results found")
        return

    # Output results
    if json_output:
        output = [pub.to_dict() for pub in results]
        click.echo(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        for i, pub in enumerate(results, 1):
            if not quiet:
                # Title with clickable link if pub_url available
                if pub.pub_url:
                    title_display = hyperlink(pub.pub_url, pub.title)
                else:
                    title_display = pub.title
                click.echo(f"\n{i}. {title_display}")
                click.echo(f"   Authors: {', '.join(pub.authors) if pub.authors else 'Unknown'}")
                click.echo(f"   Year: {pub.year or 'Unknown'}")
                click.echo(f"   Citations: {pub.citations}")
                if pub.url:
                    # PDF/eprint link
                    click.echo(f"   PDF: {hyperlink(pub.url, '[Download]')}")


@main.command("author")
@click.argument("query", required=False)
@click.option("-l", "--limit", default=5, show_default=True, help="Maximum results to return")
@click.option("-i", "--scholar-id", help="Get author by Google Scholar ID")
@click.option("-j", "--json-output", is_flag=True, help="Output results as JSON")
@click.option("-s", "--stdin", is_flag=True, help="Read query from stdin")
@click.pass_context
def author_cmd(
    ctx: click.Context,
    query: str | None,
    limit: int,
    scholar_id: str | None,
    json_output: bool,
    stdin: bool,
) -> None:
    """Search Google Scholar for authors.

    Find authors by name or get detailed info by Scholar ID.
    Note: Author search may be rate-limited by Google.

    Examples:

    \b
        # Search by name
        google-scholar-tool author "Albert Einstein"

    \b
        # Get author by Scholar ID
        google-scholar-tool author --scholar-id "XrH4VJUAAAAJ"

    \b
        # Output as JSON
        google-scholar-tool author "John Doe" --json-output

    \b
    Output Format (JSON):
        [{"name": "...", "affiliation": "...", "citations": 1000,
          "h_index": 50, "i10_index": 100, "interests": [...]}]
    """
    quiet = ctx.obj.get("quiet", False)

    # Handle stdin input
    if stdin:
        if not sys.stdin.isatty():
            query = sys.stdin.read().strip()
        else:
            click.echo("Error: --stdin specified but no input provided", err=True)
            click.echo("Fix: echo 'name' | google-scholar-tool author --stdin", err=True)
            ctx.exit(1)

    # Validate input
    if not query and not scholar_id:
        click.echo("Error: Provide either a query or --scholar-id", err=True)
        click.echo("Fix: author 'name' OR author --scholar-id 'ID'", err=True)
        ctx.exit(1)

    # Get author by ID
    if scholar_id:
        logger.info("Getting author by ID: %s", scholar_id)
        author = get_author_details(scholar_id)
        if not author:
            click.echo("Author not found", err=True)
            ctx.exit(1)
        results: list[Author] = [author]
    else:
        # Search by name
        logger.info("Searching for author: %s", query)
        results = list(search_authors(query or "", limit=limit))

    if not results:
        if not quiet:
            click.echo("No authors found")
        return

    # Output results
    if json_output:
        output = [author.to_dict() for author in results]
        click.echo(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        for i, author in enumerate(results, 1):
            if not quiet:
                click.echo(f"\n{i}. {author.name}")
                if author.affiliation:
                    click.echo(f"   Affiliation: {author.affiliation}")
                click.echo(f"   Citations: {author.citations}")
                click.echo(f"   h-index: {author.h_index}")
                click.echo(f"   i10-index: {author.i10_index}")
                if author.interests:
                    click.echo(f"   Interests: {', '.join(author.interests)}")
                if author.scholar_id:
                    click.echo(f"   Scholar ID: {author.scholar_id}")


@main.command("books")
@click.argument("query", required=False)
@click.option("-l", "--limit", default=10, show_default=True, help="Maximum results to return")
@click.option("-j", "--json-output", is_flag=True, help="Output results as JSON")
@click.option("-s", "--stdin", is_flag=True, help="Read query from stdin")
@click.option(
    "-c",
    "--cite",
    type=click.Choice(["apa", "mla", "chicago", "harvard"], case_sensitive=False),
    help="Output citations in specified style",
)
@click.pass_context
def books_cmd(
    ctx: click.Context,
    query: str | None,
    limit: int,
    json_output: bool,
    stdin: bool,
    cite: str | None,
) -> None:
    """Search Google Books for volumes.

    Requires GOOGLE_BOOKS_API_KEY environment variable to be set.

    Examples:

    \b
        # Basic search
        google-scholar-tool books "machine learning"

    \b
        # Output as JSON
        google-scholar-tool books "python programming" --json-output

    \b
        # Get APA citations for papers
        google-scholar-tool books "python programming" --cite apa

    \b
        # Get MLA citations
        google-scholar-tool books "machine learning" --cite mla --limit 5

    \b
    Note: Content search within books is not available via the API.
    Use --preview-link in output to search manually in Google Books.

    \b
    Output Format (JSON):
        [{"title": "...", "authors": [...], "publisher": "...",
          "published_date": "2024", "description": "...", "page_count": 300}]
    """
    quiet = ctx.obj.get("quiet", False)

    # Handle stdin input
    if stdin:
        if not sys.stdin.isatty():
            query = sys.stdin.read().strip()
        else:
            click.echo("Error: --stdin specified but no input provided", err=True)
            click.echo("Fix: echo 'query' | google-scholar-tool books --stdin", err=True)
            ctx.exit(1)

    # Validate query
    if not query:
        click.echo("Error: Missing query argument", err=True)
        click.echo(
            "Fix: Provide a search query, e.g.: google-scholar-tool books 'python'",
            err=True,
        )
        ctx.exit(1)

    # Execute search
    logger.info("Executing books search: %s", query)
    try:
        results: list[Book] = list(search_books(query, limit=limit))
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)

    if not results:
        if not quiet:
            click.echo("No results found")
        return

    # Output results
    if json_output:
        output = [book.to_dict() for book in results]
        click.echo(json.dumps(output, indent=2, ensure_ascii=False))
    elif cite:
        # Citation output mode
        for book in results:
            click.echo(book.cite(cite))
    else:
        for i, book in enumerate(results, 1):
            if not quiet:
                # Title with clickable link if info_link available
                if book.info_link:
                    title_display = hyperlink(book.info_link, book.title)
                else:
                    title_display = book.title
                click.echo(f"\n{i}. {title_display}")
                click.echo(f"   Authors: {', '.join(book.authors) if book.authors else 'Unknown'}")
                if book.publisher:
                    click.echo(f"   Publisher: {book.publisher}")
                if book.published_date:
                    click.echo(f"   Published: {book.published_date}")
                if book.page_count:
                    click.echo(f"   Pages: {book.page_count}")
                if book.categories:
                    click.echo(f"   Categories: {', '.join(book.categories)}")
                if book.isbn:
                    click.echo(f"   ISBN: {book.isbn}")
                if book.preview_link:
                    click.echo(f"   Preview: {hyperlink(book.preview_link, '[Search in book]')}")


# Add completion subcommand
main.add_command(completion_command)


if __name__ == "__main__":
    main()
