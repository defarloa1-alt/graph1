#!/usr/bin/env python3
"""
LCC Source Data Explorer
========================

Examine the LCC source files to understand structure and propose 
course of action for implementing taxonomy persistence.
"""

import pandas as pd
import os
from pathlib import Path
import json
from typing import Dict, List, Any

def explore_lcc_files():
    """Explore available LCC source files and analyze structure"""
    
    source_dir = Path(r"c:\Projects\Subjects\source")
    
    print("🔍 Exploring LCC Source Files")
    print("=" * 50)
    
    files = list(source_dir.glob("*.xlsx")) + list(source_dir.glob("*.csv"))
    
    analysis_results = {}
    
    for file_path in files:
        print(f"\n📄 Analyzing: {file_path.name}")
        print("-" * 30)
        
        try:
            # Try to read the file
            if file_path.suffix == '.csv':
                df = pd.read_csv(file_path, encoding='utf-8', nrows=10)
            else:
                df = pd.read_excel(file_path, nrows=10)
            
            print(f"  Shape: {df.shape}")
            print(f"  Columns: {list(df.columns)}")
            
            # Show first few rows
            print("  Sample data:")
            for i, row in df.head(3).iterrows():
                print(f"    Row {i}: {dict(row)}")
            
            analysis_results[file_path.name] = {
                "shape": df.shape,
                "columns": list(df.columns),
                "sample_data": df.head(3).to_dict('records')
            }
            
        except Exception as e:
            print(f"  ❌ Error reading file: {e}")
            analysis_results[file_path.name] = {"error": str(e)}
    
    return analysis_results

def check_lcc_api():
    """Check if Library of Congress API is available"""
    
    print("\n🌐 Checking Library of Congress API")
    print("=" * 50)
    
    try:
        import requests
        
        # Try the LC Classification API
        api_url = "https://id.loc.gov/vocabulary/classification.json"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ LC Classification API is available")
            data = response.json()
            print(f"  Total concepts: {len(data.get('@graph', []))}")
            
            # Show sample entry
            if '@graph' in data and len(data['@graph']) > 0:
                sample = data['@graph'][0]
                print(f"  Sample entry: {sample}")
            
            return {"available": True, "url": api_url, "sample": data}
        else:
            print(f"❌ API not available (status: {response.status_code})")
            return {"available": False, "status": response.status_code}
            
    except Exception as e:
        print(f"❌ Error accessing API: {e}")
        return {"available": False, "error": str(e)}

def propose_implementation_plan(file_analysis: Dict, api_status: Dict) -> Dict[str, Any]:
    """Propose implementation plan based on available data sources"""
    
    print("\n📋 Implementation Plan Proposal")
    print("=" * 50)
    
    plan = {
        "data_sources": [],
        "recommended_approach": "",
        "implementation_phases": [],
        "required_components": []
    }
    
    # Analyze available data sources
    valid_files = [name for name, analysis in file_analysis.items() 
                   if "error" not in analysis]
    
    print(f"✅ Valid source files: {len(valid_files)}")
    for filename in valid_files:
        print(f"  • {filename}")
    
    plan["data_sources"].append({
        "type": "local_files",
        "count": len(valid_files),
        "files": valid_files
    })
    
    if api_status.get("available"):
        print("✅ LC API available as supplementary source")
        plan["data_sources"].append({
            "type": "lc_api",
            "url": api_status["url"],
            "status": "available"
        })
    
    # Recommend approach
    if len(valid_files) > 0:
        plan["recommended_approach"] = "hybrid_file_api"
        print("\n🎯 Recommended Approach: Hybrid File + API")
        print("  1. Primary: Parse local XLSX/CSV files")
        print("  2. Supplement: Use LC API for missing data/validation")
        
        plan["implementation_phases"] = [
            {
                "phase": 1,
                "title": "File Parser Development",
                "tasks": [
                    "Create unified LCC file parser",
                    "Normalize field mappings across files",
                    "Extract hierarchical relationships",
                    "Generate standardized JSON output"
                ]
            },
            {
                "phase": 2,
                "title": "Database Schema Implementation",
                "tasks": [
                    "Create Postgres tables (subject_nodes, subject_edges)",
                    "Implement ETL script with upsert logic",
                    "Add validation and data quality checks",
                    "Create indexes for performance"
                ]
            },
            {
                "phase": 3,
                "title": "Bundle Integration",
                "tasks": [
                    "Update SubjectTaxonomyBundle loader",
                    "Implement startup hydration",
                    "Add refresh mechanisms",
                    "Create configuration management"
                ]
            },
            {
                "phase": 4,
                "title": "API Enhancement (Optional)",
                "tasks": [
                    "Integrate LC API for data enrichment",
                    "Add cross-reference validation",
                    "Implement incremental updates",
                    "Add monitoring and alerting"
                ]
            }
        ]
        
    else:
        plan["recommended_approach"] = "api_only"
        print("\n🎯 Recommended Approach: API-Only")
        print("  Fallback to LC API since local files have issues")
    
    plan["required_components"] = [
        "LCC file parser (Python)",
        "Database schema (Postgres)",
        "ETL script with validation",
        "SubjectTaxonomyBundle integration",
        "Configuration management",
        "Documentation and testing"
    ]
    
    return plan

def main():
    """Main analysis and planning function"""
    
    print("📚 Library of Congress Classification (LCC) Taxonomy Implementation")
    print("=" * 70)
    
    # Check for requests package
    try:
        import requests
    except ImportError:
        print("Installing requests package...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests
    
    # Analyze source files
    file_analysis = explore_lcc_files()
    
    # Check API availability
    api_status = check_lcc_api()
    
    # Propose implementation plan
    plan = propose_implementation_plan(file_analysis, api_status)
    
    # Save analysis results
    results = {
        "timestamp": "2025-09-30T00:00:00Z",
        "file_analysis": file_analysis,
        "api_status": api_status,
        "implementation_plan": plan
    }
    
    with open("lcc_analysis_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Analysis results saved to: lcc_analysis_results.json")
    
    return results

if __name__ == "__main__":
    results = main()