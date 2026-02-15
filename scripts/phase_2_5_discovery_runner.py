#!/usr/bin/env python3
"""
Chrystallum Discovery Phase 2.5 Runner
Purpose: Orchestrate book discovery across 17 facet agents
Date: February 15, 2026
Status: Production ready

Phase 2.5: Index Mining - Complete Workflow
- Stage 1: Book discovery + 7-indicator scoring (THIS FILE)
- Parallel: Stage 2-4 ready (extraction, generation, validation)
"""

import os
import json
import sys
from typing import Dict, Any, List
from datetime import datetime
import concurrent.futures

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents'))
from book_discovery_agent import BookDiscoveryAgent
from facet_agent_framework import FacetAgentFactory


class DiscoveryPhase25Runner:
    """
    Orchestrates Stage 1 of Phase 2.5: Book discovery across all facets
    """

    # Topic configurations per facet
    FACET_DISCOVERY_TOPICS = {
        "military": {
            "queries": [
                "Roman legions military campaigns warfare tactics strategy",
                "Ancient warfare soldiers weapons battle formations",
                "Military history conflict and conquest"
            ],
            "context": "Ancient Rome, 27 BCE - 476 CE",
            "max_results": 30
        },
        "political": {
            "queries": [
                "Roman Republic Empire government administration succession",
                "Ancient political systems emperors rulers governance",
                "Political history state and power"
            ],
            "context": "Ancient Rome, 27 BCE - 476 CE",
            "max_results": 30
        },
        "economic": {
            "queries": [
                "Roman trade commerce economy currency taxation",
                "Ancient economic systems commerce and trade routes",
                "Economic history markets and finance"
            ],
            "context": "Ancient Rome, 27 BCE - 476 CE",
            "max_results": 25
        },
        "religious": {
            "queries": [
                "Roman religion temples clergy paganism Christianity",
                "Ancient religious systems beliefs and institutions",
                "Religious history and faith"
            ],
            "context": "Ancient Rome, 27 BCE - 476 CE",
            "max_results": 20
        },
        "social": {
            "queries": [
                "Roman society class family slavery social structure",
                "Ancient social systems hierarchy and kinship",
                "Social history communities and organization"
            ],
            "context": "Ancient Rome, 27 BCE - 476 CE",
            "max_results": 20
        },
        "cultural": {
            "queries": [
                "Roman culture art literature philosophy civilization",
                "Ancient cultural systems identity and values",
                "Cultural history traditions and practices"
            ],
            "context": "Ancient Rome, 27 BCE - 476 CE",
            "max_results": 25
        },
        "artistic": {
            "queries": [
                "Roman art architecture sculpture painting mosaics",
                "Ancient art movements styles aesthetic schools",
                "Artistic history visual culture and architecture"
            ],
            "context": "Ancient Rome, 27 BCE - 476 CE",
            "max_results": 20
        },
        "intellectual": {
            "queries": [
                "Roman philosophy rhetoric education scholarship",
                "Ancient philosophy schools of thought ideas",
                "Intellectual history thought and learning"
            ],
            "context": "Ancient Rome, 27 BCE - 476 CE",
            "max_results": 15
        },
        "linguistic": {
            "queries": [
                "Latin language Roman writing script linguistics",
                "Ancient languages writing systems communication",
                "Linguistic history language and scripts"
            ],
            "context": "Ancient Rome, 27 BCE - 476 CE",
            "max_results": 15
        },
        "geographic": {
            "queries": [
                "Roman Empire territories borders regions provinces",
                "Ancient geography mapping territories and regions",
                "Geographic history land and space"
            ],
            "context": "Ancient Rome, 27 BCE - 476 CE",
            "max_results": 20
        },
        "environmental": {
            "queries": [
                "Climate environment ecology Rome ancient world",
                "Ancient environmental history climate and nature",
                "Environmental history nature and ecology"
            ],
            "context": "Ancient Rome, 27 BCE - 476 CE",
            "max_results": 10
        },
        "technological": {
            "queries": [
                "Roman technology engineering innovation tools",
                "Ancient technology innovation and crafts",
                "Technological history tools and innovation"
            ],
            "context": "Ancient Rome, 27 BCE - 476 CE",
            "max_results": 15
        },
        "demographic": {
            "queries": [
                "Roman population migration urbanization demographics",
                "Ancient demographics population cities settlement",
                "Demographic history people and population"
            ],
            "context": "Ancient Rome, 27 BCE - 476 CE",
            "max_results": 10
        },
        "diplomatic": {
            "queries": [
                "Roman diplomacy treaties alliances interstate relations",
                "Ancient diplomacy treaties and international relations",
                "Diplomatic history relations and treaties"
            ],
            "context": "Ancient Rome, 27 BCE - 476 CE",
            "max_results": 15
        },
        "scientific": {
            "queries": [
                "Roman science mathematics astronomy medicine",
                "Ancient science natural philosophy learning",
                "Scientific history knowledge and discovery"
            ],
            "context": "Ancient Rome, 27 BCE - 476 CE",
            "max_results": 12
        },
        "archaeological": {
            "queries": [
                "Roman archaeology sites artifacts excavation material culture",
                "Ancient archaeology material culture archaeological sites",
                "Archaeological history evidence and artifacts"
            ],
            "context": "Ancient Rome, 27 BCE - 476 CE",
            "max_results": 15
        },
        "communication": {
            "queries": [
                "Roman communication propaganda messaging rhetoric public speech",
                "Ancient communication messages rhetoric ceremonies",
                "Communication history narratives and transmission"
            ],
            "context": "Ancient Rome, 27 BCE - 476 CE",
            "max_results": 12
        }
    }

    def __init__(self):
        """Initialize discovery runner"""
        self.discovery_agent = BookDiscoveryAgent()
        self.results = {}
        self.all_rankings = {}
        
        print("✓ Initialized Discovery Phase 2.5 Runner")
        print(f"  Facets to discover: {len(self.FACET_DISCOVERY_TOPICS)}")
        print(f"  Target: Comprehensive book recommendations per facet")

    def discover_facet(self, facet_key: str) -> Dict[str, Any]:
        """
        Discover books for a single facet
        
        Args:
            facet_key: Facet registry key
            
        Returns:
            Facet discovery result dict
        """
        config = self.FACET_DISCOVERY_TOPICS.get(facet_key)
        if not config:
            print(f"⚠ Facet '{facet_key}' not configured")
            return {"facet": facet_key, "status": "not_configured"}
        
        print(f"\n{'='*60}")
        print(f"DISCOVERING: {facet_key.upper()}")
        print(f"{'='*60}")
        
        all_books = []
        
        # Try multiple queries for coverage
        for query in config["queries"]:
            try:
                books = self.discovery_agent.discover_books(
                    topic=query,
                    context=config["context"],
                    library="all",
                    max_results=config["max_results"]
                )
                all_books.extend(books)
            except Exception as e:
                print(f"⚠ Error on query '{query}': {e}")
        
        # Deduplicate by title
        unique_books = {}
        for book in all_books:
            title = book.get("title", "").lower()
            if title not in unique_books:
                unique_books[title] = book
        
        books_list = list(unique_books.values())
        
        # Score books
        scored_books = self.discovery_agent.score_books(books_list)
        
        # Export rankings
        export_file = self.discovery_agent.export_rankings(
            scored_books, 
            f"{facet_key}_books"
        )
        
        result = {
            "facet": facet_key,
            "status": "success",
            "total_discovered": len(books_list),
            "top_books": scored_books[:5],
            "average_score": round(sum(b["quality_score"] for b in scored_books) / len(scored_books), 3) if scored_books else 0,
            "export_file": export_file
        }
        
        self.results[facet_key] = result
        self.all_rankings[facet_key] = scored_books
        
        return result

    def discover_all_facets(self, parallel: bool = True, max_workers: int = 3) -> Dict[str, Any]:
        """
        Discover books for all 17 facets
        
        Args:
            parallel: Whether to run in parallel
            max_workers: Number of parallel workers
            
        Returns:
            Summary of all discoveries
        """
        print(f"\n{'='*60}")
        print("PHASE 2.5 DISCOVERY - STAGE 1: BOOK DISCOVERY")
        print(f"{'='*60}")
        print(f"Starting: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Facets to discover: {len(self.FACET_DISCOVERY_TOPICS)}")
        print(f"Parallel: {parallel} (workers={max_workers})\n")
        
        if parallel:
            # Parallel discovery
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self.discover_facet, facet_key): facet_key
                    for facet_key in self.FACET_DISCOVERY_TOPICS.keys()
                }
                
                for future in concurrent.futures.as_completed(futures):
                    facet_key = futures[future]
                    try:
                        result = future.result()
                        print(f"\n✓ Completed {facet_key}: {result['total_discovered']} books")
                    except Exception as e:
                        print(f"\n✗ Error in {facet_key}: {e}")
        else:
            # Sequential discovery
            for facet_key in self.FACET_DISCOVERY_TOPICS.keys():
                try:
                    result = self.discover_facet(facet_key)
                    print(f"\n✓ Completed {facet_key}: {result['total_discovered']} books")
                except Exception as e:
                    print(f"\n✗ Error in {facet_key}: {e}")
        
        # Generate summary
        summary = self._generate_summary()
        
        return summary

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary of all discoveries"""
        total_books = sum(r.get("total_discovered", 0) for r in self.results.values())
        successful_facets = sum(1 for r in self.results.values() if r.get("status") == "success")
        
        top_books_overall = []
        for facet_books in self.all_rankings.values():
            top_books_overall.extend(facet_books[:3])
        
        top_books_overall.sort(key=lambda x: x["quality_score"], reverse=True)
        top_books_overall = top_books_overall[:10]
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_facets": len(self.FACET_DISCOVERY_TOPICS),
            "successful_facets": successful_facets,
            "total_books_discovered": total_books,
            "average_books_per_facet": round(total_books / successful_facets, 1) if successful_facets > 0 else 0,
            "top_10_overall": top_books_overall,
            "facet_results": self.results
        }
        
        return summary

    def export_summary(self, summary: Dict[str, Any], output_file: str = None) -> str:
        """
        Export discovery summary to JSON and markdown
        
        Args:
            summary: Summary dictionary
            output_file: Optional output file path
            
        Returns:
            Path to exported file
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            output_file = f"tmp/PHASE_2_5_DISCOVERY_SUMMARY_{timestamp}.json"
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Export JSON
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n✓ Exported summary: {output_file}")
        
        # Export Markdown
        markdown_file = output_file.replace(".json", ".md")
        
        with open(markdown_file, 'w') as f:
            f.write("# Phase 2.5 Discovery Summary\n\n")
            f.write(f"**Generated:** {summary['timestamp']}\n\n")
            f.write("## Overview\n\n")
            f.write(f"- **Total Facets:** {summary['total_facets']}\n")
            f.write(f"- **Successful Facets:** {summary['successful_facets']}\n")
            f.write(f"- **Total Books Discovered:** {summary['total_books_discovered']}\n")
            f.write(f"- **Average Books/Facet:** {summary['average_books_per_facet']}\n\n")
            
            f.write("## Top 10 Books Overall\n\n")
            
            for i, book in enumerate(summary['top_10_overall'], 1):
                f.write(f"{i}. **{book['title']}** ({book.get('year', '?')})\n")
                f.write(f"   - Author: {book.get('author', 'Unknown')}\n")
                f.write(f"   - Score: {book.get('quality_score', 0):.3f}\n")
                f.write(f"   - [View](file:///{book.get('url', '#')})\n\n")
            
            f.write("## Facet Results\n\n")
            
            for facet_key, result in summary['facet_results'].items():
                if result.get('status') == 'success':
                    f.write(f"### {facet_key.title()}\n\n")
                    f.write(f"- **Books Discovered:** {result['total_discovered']}\n")
                    f.write(f"- **Average Score:** {result['average_score']:.3f}\n")
                    f.write(f"- **Export:** `{result.get('export_file', 'N/A')}`\n\n")
        
        print(f"✓ Exported markdown: {markdown_file}")
        
        return output_file


# Run Phase 2.5 Discovery
if __name__ == "__main__":
    print("Chrystallum Discovery Phase 2.5 - Stage 1")
    print("=" * 60)
    
    runner = DiscoveryPhase25Runner()
    
    # Run discovery (parallel by default for speed)
    summary = runner.discover_all_facets(parallel=True, max_workers=3)
    
    # Export summary
    summary_file = runner.export_summary(summary)
    
    # Print summary
    print(f"\n{'='*60}")
    print("DISCOVERY PHASE 2.5 COMPLETE")
    print(f"{'='*60}")
    print(f"✓ Total books discovered: {summary['total_books_discovered']}")
    print(f"✓ Facets with results: {summary['successful_facets']}/{summary['total_facets']}")
    print(f"✓ Summary exported to: {summary_file}")
    print(f"\nNEXT STEPS:")
    print(f"1. Review top books in summary ({summary_file})")
    print(f"2. Team selects 5-7 pilot books for indexing")
    print(f"3. Begin Stage 2: Index extraction (Feb 19-22)")
