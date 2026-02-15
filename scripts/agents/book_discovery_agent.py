#!/usr/bin/env python3
"""
Chrystallum Book Discovery Agent
Purpose: Discover and rank books using Perplexity API
Date: February 15, 2026
Status: Production ready

Phase 2.5: Index Mining - Stage 1
- Query library catalogs for books on topics
- Rate books by 7-indicator score
- Export ranked list for team review
"""

import os
import json
import sys
import requests
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
import re

# Import configuration loader
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config_loader import (
    PERPLEXITY_API_KEY,
    OPENAI_API_KEY,
    validate_agent_config
)


class BookDiscoveryAgent:
    """
    Discovers books on historical topics using Perplexity API
    Rates books by 7-indicator scoring algorithm
    """

    # 7-indicator scoring algorithm (Phase 2.5)
    SCORING_INDICATORS = {
        "english_language": {"weight": 1.0, "max": 1.0},  # English=1.0, other=0.0
        "full_text_available": {"weight": 1.0, "max": 1.0},  # Full text accessible
        "index_presence": {"weight": 0.8, "max": 1.0},  # Has detailed index
        "publication_year": {"weight": 0.6, "max": 1.0},  # 1950+ higher, older lower
        "academic_authority": {"weight": 0.9, "max": 1.0},  # Academic press vs trade
        "page_count": {"weight": 0.5, "max": 1.0},  # 300-600pp optimal
        "historical_closeness": {"weight": 0.7, "max": 1.0},  # Written close to period
    }

    def __init__(self):
        """Initialize discovery agent"""
        # Validate configuration
        validate_agent_config(require_openai=False, require_perplexity=True, require_neo4j=False)
        
        self.api_key = PERPLEXITY_API_KEY
        self.base_url = "https://api.perplexity.ai/chat/completions"
        
        print("✓ Initialized Book Discovery Agent (Perplexity)")
        print(f"  Scoring algorithm: 7 indicators")
        print(f"  Target: Phase 2.5 index mining")

    def discover_books(
        self, 
        topic: str, 
        context: str,
        library: str = "all",
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Discover books on a topic using Perplexity
        
        Args:
            topic: Book topic (e.g., "Roman legions")
            context: Historical context (e.g., "ancient rome")
            library: Library source (all, archive, hathitrust, loc)
            max_results: Target number of results
            
        Returns:
            List of book dictionaries with metadata
        """
        print(f"\n▶ Discovering books on: {topic}")
        print(f"  Context: {context}")
        print(f"  Library: {library}")
        
        query = self._build_discovery_query(topic, context, library, max_results)
        
        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "pplx-7b-chat",
                    "messages": [
                        {
                            "role": "user",
                            "content": query
                        }
                    ],
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "top_k": 40
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            books = self._parse_book_results(result["choices"][0]["message"]["content"])
            print(f"✓ Found {len(books)} books")
            
            return books
            
        except requests.exceptions.RequestException as e:
            print(f"✗ API Error: {e}")
            return []

    def _build_discovery_query(
        self, 
        topic: str, 
        context: str,
        library: str,
        max_results: int
    ) -> str:
        """Build discovery query for Perplexity"""
        
        library_filter = {
            "archive": "Internet Archive (archive.org)",
            "hathitrust": "HathiTrust Digital Library",
            "loc": "Library of Congress",
            "all": "Internet Archive, HathiTrust, Library of Congress"
        }.get(library, "Internet Archive, HathiTrust, Library of Congress")
        
        return f"""Find historical books on this topic for academic research.

TOPIC: {topic}
HISTORICAL CONTEXT: {context}

SEARCH LIBRARIES: {library_filter}

REQUIREMENTS FOR EACH BOOK:
1. Full text must be available online and OCR-readable
2. Dedicated detailed index (table of contents + subject index)
3. 300-600 pages (optimal for Phase 2.5 indexing)
4. Academic or university press preferred
5. English language
6. Publication year 1950+ preferred (but older acceptable if authoritative)
7. Author expertise or institutional authority

RETURN FORMAT: JSON array with exactly {max_results} books, each with:
{{
  "title": "Full title",
  "author": "Author name",
  "year": publication_year (number),
  "pages": page_count (number),
  "publisher": "Publisher name",
  "url": "Full URL to full text (Internet Archive, HathiTrust, or Library of Congress)",
  "access_type": "full_text|preview|restricted",
  "language": "en|other",
  "has_index": true|false,
  "academic_press": true|false,
  "description": "One sentence description of scope and relevance to {topic}",
  "confidence": 0.0-1.0 (your confidence this is the right source)
}}

STRICT OUTPUT: Return ONLY the JSON array, no other text."""

    def _parse_book_results(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse book results from Perplexity response"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\[.*?\]', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"⚠ Failed to parse response: {e}")
        
        return []

    def score_books(self, books: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Score books by 7-indicator algorithm
        
        Args:
            books: List of book dictionaries
            
        Returns:
            Books sorted by quality score (descending)
        """
        print(f"\n▶ Scoring {len(books)} books by 7-indicator algorithm...")
        
        scored_books = []
        
        for book in books:
            score_breakdown = {}
            
            # 1. English language (weight 1.0)
            lang_score = 1.0 if book.get("language", "").lower() == "en" else 0.0
            score_breakdown["english_language"] = lang_score
            
            # 2. Full text available (weight 1.0)
            access_score = 1.0 if book.get("access_type") == "full_text" else 0.5 if book.get("access_type") == "preview" else 0.0
            score_breakdown["full_text_available"] = access_score
            
            # 3. Index presence (weight 0.8)
            index_score = 1.0 if book.get("has_index") else 0.5
            score_breakdown["index_presence"] = index_score
            
            # 4. Publication year (weight 0.6)
            year = book.get("year", 1900)
            if year >= 2000:
                year_score = 1.0
            elif year >= 1950:
                year_score = 0.9
            elif year >= 1900:
                year_score = 0.7
            else:
                year_score = 0.5
            score_breakdown["publication_year"] = year_score
            
            # 5. Academic authority (weight 0.9)
            academic_score = 1.0 if book.get("academic_press") else 0.6
            score_breakdown["academic_authority"] = academic_score
            
            # 6. Page count (weight 0.5)
            pages = book.get("pages", 400)
            if 300 <= pages <= 600:
                pages_score = 1.0
            elif 200 <= pages <= 800:
                pages_score = 0.8
            elif 100 <= pages <= 1000:
                pages_score = 0.6
            else:
                pages_score = 0.3
            score_breakdown["page_count"] = pages_score
            
            # 7. Historical closeness (weight 0.7)
            # Approximation: books written closer to period have better primary source access
            # Assumes academic books, so weight newer heavily
            if year >= 1980:
                closeness_score = 0.8  # Modern with research access
            elif year >= 1950:
                closeness_score = 0.7
            elif year >= 1900:
                closeness_score = 0.9  # Older can be primary source
            else:
                closeness_score = 0.6
            score_breakdown["historical_closeness"] = closeness_score
            
            # Calculate weighted total
            total_score = 0.0
            max_possible = 0.0
            
            for indicator, config in self.SCORING_INDICATORS.items():
                weight = config["weight"]
                max_val = config["max"]
                actual = score_breakdown.get(indicator, 0.0)
                
                total_score += actual * weight
                max_possible += max_val * weight
            
            # Normalize to 0-1
            normalized_score = total_score / max_possible if max_possible > 0 else 0.0
            
            scored_books.append({
                **book,
                "quality_score": round(normalized_score, 3),
                "score_breakdown": score_breakdown,
                "indicators_met": sum(1 for v in score_breakdown.values() if v >= 0.7)
            })
        
        # Sort by quality score descending
        scored_books.sort(key=lambda x: x["quality_score"], reverse=True)
        
        # Add rank
        for rank, book in enumerate(scored_books, 1):
            book["rank"] = rank
        
        print(f"✓ Scored {len(scored_books)} books")
        print(f"  Top score: {scored_books[0]['quality_score']:.3f}")
        print(f"  Median score: {scored_books[len(scored_books)//2]['quality_score']:.3f}")
        
        return scored_books

    def export_rankings(
        self, 
        scored_books: List[Dict[str, Any]], 
        topic: str,
        output_file: Optional[str] = None
    ) -> str:
        """
        Export ranked books to JSON and markdown
        
        Args:
            scored_books: Scored and ranked books
            topic: Topic for filename
            output_file: Optional output file path
            
        Returns:
            Path to exported file
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            topic_slug = topic.lower().replace(" ", "_")[:20]
            output_file = f"tmp/book_rankings_{topic_slug}_{timestamp}.json"
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Export JSON
        with open(output_file, 'w') as f:
            json.dump({
                "topic": topic,
                "timestamp": datetime.now().isoformat(),
                "total_books": len(scored_books),
                "top_10_average": round(sum(b["quality_score"] for b in scored_books[:10]) / min(10, len(scored_books)), 3),
                "books": scored_books
            }, f, indent=2)
        
        print(f"\n✓ Exported JSON: {output_file}")
        
        # Export Markdown summary
        markdown_file = output_file.replace(".json", ".md")
        
        with open(markdown_file, 'w') as f:
            f.write(f"# Book Rankings for: {topic}\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Total Books:** {len(scored_books)}\n")
            f.write(f"**Top 10 Average Score:** {round(sum(b['quality_score'] for b in scored_books[:10]) / min(10, len(scored_books)), 3)}\n\n")
            
            f.write("## Top 10 Books\n\n")
            
            for book in scored_books[:10]:
                f.write(f"### #{book['rank']} - {book['title']}\n\n")
                f.write(f"**Score:** {book['quality_score']:.3f}  \n")
                f.write(f"**Author:** {book.get('author', 'Unknown')}  \n")
                f.write(f"**Year:** {book.get('year', 'Unknown')}  \n")
                f.write(f"**Pages:** {book.get('pages', 'Unknown')}  \n")
                f.write(f"**Publisher:** {book.get('publisher', 'Unknown')}  \n")
                f.write(f"**Access:** {book.get('access_type', 'Unknown')}  \n")
                f.write(f"**URL:** [{book.get('url', 'N/A')}]({book.get('url', '#')})  \n\n")
                f.write(f"**Description:** {book.get('description', 'N/A')}\n\n")
                f.write(f"**Indicators Met:** {book.get('indicators_met', 0)}/7\n\n")
        
        print(f"✓ Exported Markdown: {markdown_file}")
        
        return output_file

    def discover_and_rank(
        self, 
        topic: str, 
        context: str,
        library: str = "all",
        max_results: int = 50
    ) -> Tuple[List[Dict[str, Any]], str]:
        """
        Complete discovery + ranking workflow
        
        Args:
            topic: Book topic
            context: Historical context
            library: Library source
            max_results: Target number of results
            
        Returns:
            Tuple of (ranked_books, export_file_path)
        """
        # Discover
        books = self.discover_books(topic, context, library, max_results)
        
        if not books:
            print("⚠ No books found")
            return [], ""
        
        # Score
        scored_books = self.score_books(books)
        
        # Export
        export_file = self.export_rankings(scored_books, topic)
        
        return scored_books, export_file


# Test script
if __name__ == "__main__":
    print("Chrystallum Book Discovery Agent")
    print("=" * 60)

    try:
        validate_agent_config(require_perplexity=True, require_neo4j=False)
    except ValueError as e:
        print(f"✗ Configuration Error:\n{e}")
        sys.exit(1)
    
    agent = BookDiscoveryAgent()
    
    print("\n→ Discovering books on Roman military history...")
    books, export_file = agent.discover_and_rank(
        topic="Roman legions and military campaigns",
        context="Ancient Rome, 27 BCE - 476 CE",
        library="all",
        max_results=20
    )
    
    if books:
        print(f"\n→ Top 3 books:")
        for book in books[:3]:
            print(f"   [{book['rank']}] {book['title']} ({book['year']}) - Score: {book['quality_score']}")
            print(f"       {book['description']}")
            print(f"       URL: {book['url']}\n")
    
    print("✓ Discovery test complete")
