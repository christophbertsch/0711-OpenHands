---
triggers:
- bmecat
- workspace
- competitive analysis
- product catalog
- etim
- xml catalog
---

# BMEcat Workspace Processing Agent

Specialized knowledge for processing BMEcat XML catalogs with ETIM classifications in OpenHands Workspace system.

## BMEcat Format Understanding

BMEcat is a standardized XML format for electronic product catalogs, commonly used in B2B e-commerce:

- **HEADER**: Contains catalog metadata, supplier info, and buyer details
- **CATALOG_GROUP_SYSTEM**: Defines product hierarchy and categories
- **PRODUCT**: Individual product entries with specifications and features
- **ETIM Features**: Standardized technical attributes using ETIM classification system

## Common BMEcat Processing Tasks

### 1. Product Extraction
```python
# Extract products with ETIM features
for product in tree.xpath("//PRODUCT"):
    supplier_pid = product.xpath(".//SUPPLIER_PID/text()")[0]
    description = product.xpath(".//DESCRIPTION_SHORT/text()")[0]

    # Extract ETIM features
    features = {}
    for feature in product.xpath(".//FEATURE"):
        fname = feature.xpath(".//FNAME/text()")[0]  # ETIM feature code
        fvalue = feature.xpath(".//FVALUE/text()")[0]  # Feature value
        features[fname] = fvalue
```

### 2. Competitive Intelligence Workflow
When users request competitive analysis:

1. **Parse BMEcat**: Extract product data and specifications
2. **Generate Search Queries**: Create optimized search terms from product descriptions
3. **External Search**: Use Tavily to find competing products on e-commerce sites
4. **Data Enrichment**: Crawl competitor pages for pricing and availability
5. **Analysis**: Compare features, prices, and market positioning

### 3. ETIM Feature Mapping
Common ETIM codes in LED/lighting products:
- `EF000010`: Product type
- `EF008856`: Nominal voltage (V)
- `EF000381`: IP protection class
- `EF002423`: LED type/color
- `EF012487`: Luminous flux (lm)

## Workspace Integration

### Intent Processing
Transform natural language intents into structured plans:

**User Intent**: "Extract products and crawl with Tavily all competition product on leading e-commerce sites"

**Generated Operations**:
1. `parse_bmecat_catalog` - Extract structured product data
2. `generate_search_queries` - Create competitive search terms
3. `tavily_competitive_search` - Search e-commerce platforms
4. `crawl_competitor_details` - Extract pricing/availability
5. `competitive_analysis` - Generate comparison reports

### Security Considerations
- **Network Allowlists**: Restrict egress to approved domains (api.tavily.com, major e-commerce sites)
- **Rate Limiting**: Respect site policies with appropriate delays
- **PII Redaction**: Remove sensitive data before external API calls
- **Sandboxed Execution**: Run all processing in isolated containers

### Output Formats
Generate multiple output formats for different stakeholders:
- **CSV**: Structured data for spreadsheet analysis
- **JSON**: Programmatic access to analysis results
- **HTML**: Executive reports with visualizations
- **Markdown**: Documentation and decision logs

## Best Practices

### Data Quality
- Validate ETIM feature codes against standard dictionaries
- Handle missing or malformed XML gracefully
- Implement fallback strategies for incomplete data

### Performance Optimization
- Process products in batches to manage memory usage
- Cache search results to avoid duplicate API calls
- Use parallel processing for independent operations

### Error Handling
- Log all processing steps for debugging
- Implement retry logic for network operations
- Provide clear error messages for user feedback

## Example Workspace Structure
```
workspace-bmecat-analysis/
├── data/
│   ├── uploads/BMEcat_catalog.xml
│   ├── intermediate/
│   │   ├── products_structured.json
│   │   ├── search_queries.json
│   │   └── competitor_matches.json
│   └── outputs/
│       ├── competitive_analysis.csv
│       ├── market_gaps_analysis.json
│       └── price_comparison_report.html
├── scripts/
│   ├── job_12345678.py
│   └── requirements.lock
└── context/
    ├── plans/plan_abc123.json
    ├── reports/job_12345678_*.json
    └── decisions/2025-01-20_notes.md
```

This agent ensures BMEcat processing follows workspace system patterns while maintaining data quality and security standards.
