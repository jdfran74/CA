"""
Fetch documents from Readwise Reader API.

Usage:
    python execution/fetch_readwise.py                    # Fetch all recent documents
    python execution/fetch_readwise.py --category tweet   # Fetch only tweets
    python execution/fetch_readwise.py --category video   # Fetch only videos
    python execution/fetch_readwise.py --limit 5          # Limit to 5 results
    python execution/fetch_readwise.py --with-content     # Include full HTML content
"""

import os
import sys
import argparse
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

READWISE_API_KEY = os.getenv("READWISE_API_KEY")
BASE_URL = "https://readwise.io/api/v3"


def verify_token():
    """Check if the API token is valid."""
    response = requests.get(
        "https://readwise.io/api/v2/auth/",
        headers={"Authorization": f"Token {READWISE_API_KEY}"}
    )
    return response.status_code == 204


def fetch_documents(category=None, location=None, updated_after=None, with_content=False, limit=None):
    """
    Fetch documents from Readwise Reader.

    Args:
        category: Filter by type (article, tweet, video, pdf, epub, rss, email, highlight, note)
        location: Filter by location (new, later, shortlist, archive, feed)
        updated_after: ISO 8601 date string, only fetch docs updated after this
        with_content: Include full HTML content in response
        limit: Maximum number of documents to return

    Returns:
        List of document dictionaries
    """
    all_documents = []
    next_page_cursor = None

    while True:
        params = {}
        if next_page_cursor:
            params['pageCursor'] = next_page_cursor
        if category:
            params['category'] = category
        if location:
            params['location'] = location
        if updated_after:
            params['updatedAfter'] = updated_after
        if with_content:
            params['withHtmlContent'] = 'true'

        response = requests.get(
            f"{BASE_URL}/list/",
            params=params,
            headers={"Authorization": f"Token {READWISE_API_KEY}"}
        )

        if response.status_code != 200:
            print(f"Error: API returned status {response.status_code}")
            print(response.text)
            sys.exit(1)

        data = response.json()
        all_documents.extend(data['results'])

        # Check if we've hit the limit
        if limit and len(all_documents) >= limit:
            all_documents = all_documents[:limit]
            break

        # Check for more pages
        next_page_cursor = data.get('nextPageCursor')
        if not next_page_cursor:
            break

    return all_documents


def format_document(doc):
    """Format a document for display."""
    output = []
    output.append(f"{'='*60}")
    output.append(f"Title: {doc.get('title', 'No title')}")
    output.append(f"Category: {doc.get('category', 'unknown')}")
    output.append(f"Author: {doc.get('author', 'Unknown')}")
    output.append(f"Source URL: {doc.get('source_url', 'N/A')}")
    output.append(f"Saved at: {doc.get('saved_at', 'N/A')}")
    output.append(f"Location: {doc.get('location', 'N/A')}")
    output.append(f"Reading progress: {doc.get('reading_progress', 0)*100:.0f}%")

    if doc.get('summary'):
        output.append(f"\nSummary: {doc.get('summary')}")

    if doc.get('notes'):
        output.append(f"\nNotes: {doc.get('notes')}")

    tags = doc.get('tags', {})
    if tags:
        tag_names = list(tags.keys()) if isinstance(tags, dict) else tags
        output.append(f"Tags: {', '.join(tag_names)}")

    if doc.get('html_content'):
        # Truncate for display
        content = doc['html_content'][:500] + "..." if len(doc.get('html_content', '')) > 500 else doc.get('html_content', '')
        output.append(f"\nContent preview:\n{content}")

    output.append(f"{'='*60}\n")
    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(description='Fetch documents from Readwise Reader')
    parser.add_argument('--category', choices=['article', 'tweet', 'video', 'pdf', 'epub', 'rss', 'email', 'highlight', 'note'],
                        help='Filter by document category')
    parser.add_argument('--location', choices=['new', 'later', 'shortlist', 'archive', 'feed'],
                        help='Filter by document location')
    parser.add_argument('--days', type=int, default=None,
                        help='Only fetch documents from the last N days')
    parser.add_argument('--limit', type=int, default=10,
                        help='Maximum number of documents to fetch (default: 10)')
    parser.add_argument('--with-content', action='store_true',
                        help='Include full HTML content')
    parser.add_argument('--json', action='store_true',
                        help='Output raw JSON instead of formatted text')

    args = parser.parse_args()

    # Verify token first
    if not READWISE_API_KEY:
        print("Error: READWISE_API_KEY not found in .env file")
        sys.exit(1)

    print("Verifying API token...")
    if not verify_token():
        print("Error: Invalid API token")
        sys.exit(1)
    print("Token valid!\n")

    # Calculate updated_after if days specified
    updated_after = None
    if args.days:
        updated_after = (datetime.now() - timedelta(days=args.days)).isoformat()

    # Fetch documents
    print(f"Fetching documents...")
    if args.category:
        print(f"  Category: {args.category}")
    if args.location:
        print(f"  Location: {args.location}")
    if args.days:
        print(f"  From last {args.days} days")
    print()

    documents = fetch_documents(
        category=args.category,
        location=args.location,
        updated_after=updated_after,
        with_content=args.with_content,
        limit=args.limit
    )

    print(f"Found {len(documents)} documents\n")

    if args.json:
        import json
        print(json.dumps(documents, indent=2))
    else:
        for doc in documents:
            print(format_document(doc))


if __name__ == "__main__":
    main()
