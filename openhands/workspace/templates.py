"""
Code templates for workspace script generation
"""

from typing import Dict, Any
from .models import Plan


class CodeTemplates:
    """Templates for generating Python scripts from plans"""
    
    def generate_competitive_analysis_script(self, plan: Plan) -> str:
        """Generate competitive analysis script for BMEcat processing"""
        
        # Create a simple working script without complex template formatting
        script_content = f'''#!/usr/bin/env python3
"""
Generated competitive analysis script for BMEcat processing
Plan ID: {plan.plan_id}
Generated: {plan.created_at.isoformat()}
"""

import os
import pandas as pd
import json
import time
import re
from pathlib import Path

try:
    from lxml import etree
except ImportError:
    print("Warning: lxml not available, using xml.etree.ElementTree")
    import xml.etree.ElementTree as etree


def run(input_path, output_dir, tavily_key="demo", qps=1):
    """Competitive intelligence pipeline for BMEcat products"""
    print("🚀 Starting competitive analysis pipeline...")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Parse BMEcat XML
    print("🔍 Parsing BMEcat catalog...")
    products = parse_bmecat_catalog(input_path)
    print(f"✅ Extracted {{len(products)}} products")
    
    # Save intermediate results
    intermediate_dir = output_path.parent / "intermediate"
    intermediate_dir.mkdir(exist_ok=True)
    
    with open(intermediate_dir / "products_structured.json", "w") as f:
        json.dump(products, f, indent=2, default=str)
    
    # Step 2: Generate search queries
    print("🎯 Generating competitive search queries...")
    search_queries = generate_search_queries(products)
    
    with open(intermediate_dir / "search_queries.json", "w") as f:
        json.dump(search_queries, f, indent=2)
    
    # Step 3: Mock competitive search (Tavily simulation)
    print("🌐 Simulating competitor search...")
    competitors = simulate_competitor_search(search_queries)
    
    with open(intermediate_dir / "competitor_matches.json", "w") as f:
        json.dump(competitors, f, indent=2)
    
    # Step 4: Mock competitor details
    print("📊 Simulating competitor details extraction...")
    enriched_competitors = simulate_competitor_details(competitors)
    
    with open(intermediate_dir / "competitor_details.json", "w") as f:
        json.dump(enriched_competitors, f, indent=2, default=str)
    
    # Step 5: Generate competitive analysis
    print("📈 Generating competitive analysis...")
    analysis_results = generate_competitive_analysis(products, enriched_competitors)
    
    # Export results
    export_results(analysis_results, output_path, products, enriched_competitors)
    print(f"✅ Analysis complete! Results saved to {{output_path}}")


def parse_bmecat_catalog(xml_path):
    """Extract structured product data from BMEcat XML"""
    print(f"  Parsing XML file: {{xml_path}}")
    
    try:
        tree = etree.parse(xml_path)
        products = []
        
        # Handle both lxml and ElementTree
        if hasattr(tree, 'xpath'):
            # lxml
            product_elements = tree.xpath("//PRODUCT")
        else:
            # ElementTree
            product_elements = tree.findall(".//PRODUCT")
        
        for i, product in enumerate(product_elements[:50]):  # Limit for demo
            if hasattr(product, 'xpath'):
                # lxml
                supplier_pid = product.xpath(".//SUPPLIER_PID/text()")
                supplier_pid = supplier_pid[0] if supplier_pid else ""
                
                short_desc = product.xpath(".//DESCRIPTION_SHORT/text()")
                short_desc = short_desc[0] if short_desc else ""
                
                manufacturer = product.xpath(".//MANUFACTURER_NAME/text()")
                manufacturer = manufacturer[0] if manufacturer else ""
                
                keywords = [kw.text for kw in product.xpath(".//KEYWORD[@lang='deu']") if kw.text]
            else:
                # ElementTree
                supplier_pid_elem = product.find(".//SUPPLIER_PID")
                supplier_pid = supplier_pid_elem.text if supplier_pid_elem is not None else ""
                
                short_desc_elem = product.find(".//DESCRIPTION_SHORT")
                short_desc = short_desc_elem.text if short_desc_elem is not None else ""
                
                manufacturer_elem = product.find(".//MANUFACTURER_NAME")
                manufacturer = manufacturer_elem.text if manufacturer_elem is not None else ""
                
                keywords = [kw.text for kw in product.findall(".//KEYWORD") if kw.text and kw.get('lang') == 'deu']
            
            products.append({{
                "supplier_pid": supplier_pid,
                "description": short_desc,
                "manufacturer": manufacturer,
                "keywords": keywords,
                "category": "LED_Product"
            }})
        
        return products
        
    except Exception as e:
        print(f"  ❌ Error parsing BMEcat: {{e}}")
        return []


def generate_search_queries(products):
    """Generate optimized search queries for competitive research"""
    queries = {{}}
    
    for product in products:
        pid = product["supplier_pid"]
        desc = product["description"]
        manufacturer = product["manufacturer"]
        
        product_queries = []
        
        # Strategy 1: Generic LED search
        if "led" in desc.lower():
            product_queries.append(f"LED lighting {{desc[:30]}} buy online")
        
        # Strategy 2: Manufacturer search
        if manufacturer:
            product_queries.append(f"{{manufacturer}} LED products price")
        
        # Default search
        if not product_queries:
            product_queries.append(f"LED product {{pid}}")
        
        queries[pid] = product_queries[:2]  # Limit to top 2 queries per product
    
    return queries


def simulate_competitor_search(search_queries):
    """Simulate competitor search results"""
    competitors = []
    
    platforms = ["amazon.de", "ebay.de", "conrad.de"]
    
    for product_id, queries in list(search_queries.items())[:10]:  # Limit for demo
        for query in queries:
            for i, platform in enumerate(platforms):
                competitors.append({{
                    "source_product_id": product_id,
                    "search_query": query,
                    "competitor_url": f"https://{{platform}}/led-product-{{product_id}}-{{i}}",
                    "competitor_title": f"LED Product {{i}} - {{query[:30]}}",
                    "competitor_snippet": f"High quality LED product. Great value for money."
                }})
    
    return competitors


def simulate_competitor_details(competitors):
    """Simulate competitor details extraction"""
    enriched = []
    
    for i, comp in enumerate(competitors):
        # Simulate varying prices
        base_price = 45 + (i % 10) * 15
        price = base_price + (hash(comp["source_product_id"]) % 50)
        
        availability_options = ["In Stock", "Available", "Limited Stock", "Out of Stock"]
        availability = availability_options[i % len(availability_options)]
        
        enriched.append({{
            **comp,
            "competitor_price": price,
            "competitor_currency": "EUR",
            "availability": availability,
            "crawl_timestamp": time.time()
        }})
    
    return enriched


def generate_competitive_analysis(source_products, competitors):
    """Generate comprehensive competitive analysis"""
    total_competitors = len(competitors)
    
    # Price analysis
    prices = [c.get("competitor_price") for c in competitors if c.get("competitor_price")]
    avg_price = sum(prices) / len(prices) if prices else 0
    
    analysis = {{
        "summary": {{
            "total_source_products": len(source_products),
            "total_competitors_found": total_competitors,
            "avg_competitors_per_product": total_competitors / max(len(source_products), 1),
            "average_competitor_price": avg_price
        }},
        "price_analysis": {{
            "min_price": min(prices) if prices else 0,
            "max_price": max(prices) if prices else 0,
            "avg_price": avg_price,
            "price_range": max(prices) - min(prices) if prices else 0
        }},
        "market_gaps": [
            {{"category": "RGB Controllers", "opportunity": "Premium segment underserved"}},
            {{"category": "IP67 Strips", "opportunity": "Limited outdoor options"}}
        ],
        "competitor_landscape": {{
            "amazon_de": len([c for c in competitors if "amazon.de" in c.get("competitor_url", "")]),
            "ebay_de": len([c for c in competitors if "ebay.de" in c.get("competitor_url", "")]),
            "conrad_de": len([c for c in competitors if "conrad.de" in c.get("competitor_url", "")])
        }}
    }}
    
    return analysis


def export_results(analysis, output_path, products, competitors):
    """Export analysis results in multiple formats"""
    
    # CSV export
    csv_data = []
    for comp in competitors:
        csv_data.append({{
            "source_product_id": comp.get("source_product_id", ""),
            "search_query": comp.get("search_query", ""),
            "competitor_title": comp.get("competitor_title", ""),
            "competitor_url": comp.get("competitor_url", ""),
            "competitor_price": comp.get("competitor_price", ""),
            "availability": comp.get("availability", ""),
        }})
    
    if csv_data:
        df = pd.DataFrame(csv_data)
        df.to_csv(output_path / "competitive_analysis.csv", index=False)
        print(f"  ✅ CSV exported: {{len(csv_data)}} competitor records")
    
    # JSON export
    with open(output_path / "market_gaps_analysis.json", "w") as f:
        json.dump(analysis, f, indent=2, default=str)
    
    # HTML report - simple version
    html_parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "    <title>Competitive Analysis Report</title>",
        "</head>",
        "<body>",
        "    <h1>BMEcat Competitive Analysis Report</h1>",
        "    <h2>Executive Summary</h2>",
        "    <p>Source Products: " + str(analysis['summary']['total_source_products']) + "</p>",
        "    <p>Competitors Found: " + str(analysis['summary']['total_competitors_found']) + "</p>",
        "    <p>Average Price: €" + f"{{analysis['price_analysis']['avg_price']:.2f}}" + "</p>",
        "    <h2>Market Gaps Identified</h2>",
        "    <ul>",
        "        <li><strong>RGB Controllers</strong>: Premium segment underserved</li>",
        "        <li><strong>IP67 Strips</strong>: Limited outdoor options</li>",
        "    </ul>",
        "    <p><em>Report generated on " + time.strftime('%Y-%m-%d %H:%M:%S') + "</em></p>",
        "</body>",
        "</html>"
    ]
    
    html_content = "\\n".join(html_parts)
    
    with open(output_path / "price_comparison_report.html", "w") as f:
        f.write(html_content)
    
    print("  ✅ HTML report exported")
    print("  ✅ JSON analysis exported")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python script.py <input_xml> <output_dir> <tavily_key>")
        sys.exit(1)
    
    run(sys.argv[1], sys.argv[2], sys.argv[3])
'''
        
        return script_content