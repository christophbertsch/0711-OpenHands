# Content Enrichment & Analytics Platform

## Overview

This platform transforms OpenHands into a comprehensive content enrichment and analytics solution designed for e-commerce and product data optimization. It provides AI-powered micro agents that specialize in SEO optimization, Amazon marketplace optimization, and advanced analytics for product content.

## Key Features

### 🚀 Micro Agents for Content Optimization

#### SEO Optimizer Agent
- **Keyword Research & Analysis**: Analyzes keyword density, identifies opportunities
- **Content Optimization**: Optimizes titles, meta descriptions, and content structure
- **Technical SEO**: URL optimization, schema markup, internal linking
- **E-commerce SEO**: Product-specific optimization for search visibility

#### Amazon Optimizer Agent
- **A9 Algorithm Optimization**: Optimizes for Amazon's search algorithm
- **Product Listing Enhancement**: Creates compelling titles, bullet points, descriptions
- **Backend Search Terms**: Generates optimized search terms for Amazon
- **Competitive Analysis**: Monitors and analyzes competitor strategies

#### Analytics Agent
- **Performance Monitoring**: Tracks KPIs across multiple channels
- **Trend Analysis**: Identifies patterns and forecasts performance
- **A/B Testing**: Provides statistical analysis for content variations
- **Business Intelligence**: Generates actionable insights and recommendations

#### Content Enrichment Agent
- **Content Generation**: Creates compelling product descriptions and titles
- **Multi-Channel Adaptation**: Optimizes content for different platforms
- **Quality Scoring**: Evaluates and scores content quality
- **Brand Compliance**: Ensures consistency with brand guidelines

### 📊 Data Processing Capabilities

#### XML Data Processing
- Supports standard e-commerce XML feeds
- PIM system exports
- Custom XML schemas with flexible mapping
- Multi-language product data

#### CSV Data Processing
- Standard e-commerce product exports
- Flexible column mapping and validation
- Batch processing for large datasets
- Data cleaning and standardization

#### API Integrations
- **PIM Connectors**: Akeneo, Pimcore, inRiver, and others
- **ERP Connectors**: SAP, Oracle, Microsoft Dynamics
- **Real-time Synchronization**: Automated data updates
- **Conflict Resolution**: Intelligent handling of data conflicts

### 📈 Analytics & Reporting

#### Performance Metrics
- Content quality scores
- SEO performance tracking
- Conversion rate analysis
- Multi-channel performance comparison

#### Advanced Analytics
- Cohort analysis and segmentation
- Predictive modeling and forecasting
- Anomaly detection and alerting
- Custom dashboard creation

#### Business Intelligence
- Executive summary reports
- Competitive benchmarking
- ROI analysis and optimization
- Trend identification and insights

## Architecture

### Backend Components

```
openhands/
├── data_processing/
│   ├── xml_processor.py          # XML data ingestion and processing
│   ├── csv_processor.py          # CSV data handling and validation
│   ├── api_connector.py          # PIM/ERP API integrations
│   ├── data_enricher.py          # Content enrichment engine
│   └── analytics_processor.py    # Analytics and reporting engine
├── server/routes/
│   └── content_enrichment.py     # REST API endpoints
└── microagents/
    ├── seo_optimizer.md          # SEO optimization micro agent
    ├── amazon_optimizer.md       # Amazon marketplace optimization
    ├── analytics_agent.md        # Analytics and insights
    └── content_enrichment.md     # Content generation and enhancement
```

### Frontend Components

```
frontend/src/
├── components/content-enrichment/
│   └── ContentEnrichmentDashboard.tsx  # Main dashboard interface
├── routes/
│   └── content-enrichment.tsx           # Route configuration
└── api/
    └── content-enrichment-api.ts        # API client methods
```

## API Endpoints

### Data Processing
- `POST /api/content-enrichment/upload/xml` - Upload and process XML files
- `POST /api/content-enrichment/upload/csv` - Upload and process CSV files
- `POST /api/content-enrichment/validate/xml` - Validate XML structure
- `POST /api/content-enrichment/validate/csv` - Validate CSV structure

### Content Enrichment
- `POST /api/content-enrichment/enrich/product` - Enrich single product
- `POST /api/content-enrichment/enrich/batch` - Batch product enrichment
- `GET /api/content-enrichment/stats/enrichment` - Enrichment statistics

### Analytics
- `POST /api/content-enrichment/analytics/track-metric` - Track single metric
- `POST /api/content-enrichment/analytics/track-metrics` - Batch metric tracking
- `GET /api/content-enrichment/analytics/performance-report` - Generate reports
- `POST /api/content-enrichment/analytics/content-performance` - Content analysis
- `GET /api/content-enrichment/analytics/trend-analysis/{metric}` - Trend analysis
- `GET /api/content-enrichment/analytics/dashboard` - Dashboard data

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 18+
- Poetry for Python dependency management
- npm for frontend dependencies

### Installation

1. **Install Backend Dependencies**
   ```bash
   poetry install
   ```

2. **Install Frontend Dependencies**
   ```bash
   cd frontend
   npm install
   ```

3. **Start the Development Server**
   ```bash
   # Backend
   poetry run python -m openhands.server

   # Frontend (in another terminal)
   cd frontend
   npm run dev
   ```

4. **Access the Platform**
   - Main application: `http://localhost:3000`
   - Content Enrichment Dashboard: `http://localhost:3000/content-enrichment`
   - API Documentation: `http://localhost:8000/docs`

### Configuration

#### Environment Variables
```bash
# API Configuration
CONTENT_ENRICHMENT_API_KEY=your_api_key
PIM_API_URL=https://your-pim-system.com/api
ERP_API_URL=https://your-erp-system.com/api

# Analytics Configuration
ANALYTICS_RETENTION_DAYS=365
ENABLE_PREDICTIVE_ANALYTICS=true

# Enrichment Configuration
DEFAULT_SEO_KEYWORDS=product,quality,premium
BRAND_GUIDELINES_PATH=./config/brand_guidelines.json
```

#### Brand Guidelines Configuration
```json
{
  "required_brand_mention": "YourBrand",
  "forbidden_words": ["cheap", "low-quality"],
  "tone": "professional",
  "style_guide": {
    "title_max_length": 60,
    "description_max_length": 300,
    "required_attributes": ["material", "dimensions"]
  }
}
```

## Usage Examples

### 1. Upload and Process Product Data

```python
# Upload XML file
with open('products.xml', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/content-enrichment/upload/xml',
        files={'file': f}
    )
    products = response.json()['products']
```

### 2. Enrich Product Content

```python
# Enrich single product
product_data = {
    "id": "PROD001",
    "title": "Basic Product Title",
    "description": "Simple description",
    "category": "Electronics"
}

enrichment_config = {
    "enabled_types": ["seo_optimization", "content_generation"],
    "target_channels": ["website", "amazon"],
    "seo_keywords": ["premium", "quality", "durable"]
}

response = requests.post(
    'http://localhost:8000/api/content-enrichment/enrich/product',
    json={
        "product": product_data,
        "config": enrichment_config
    }
)

enriched_result = response.json()
```

### 3. Analyze Content Performance

```python
# Analyze content performance
response = requests.post(
    'http://localhost:8000/api/content-enrichment/analytics/content-performance',
    json=products
)

analysis = response.json()
print(f"Average quality score: {analysis['content_quality_scores']['average']}")
print(f"SEO performance: {analysis['seo_performance']['average']}")
```

### 4. Generate Performance Report

```python
# Generate performance report
from datetime import datetime, timedelta

start_date = datetime.now() - timedelta(days=30)
end_date = datetime.now()

response = requests.get(
    'http://localhost:8000/api/content-enrichment/analytics/performance-report',
    params={
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'metric_types': ['performance', 'quality']
    }
)

report = response.json()
```

## Micro Agent Configuration

### SEO Optimizer
```yaml
---
name: seo_optimizer
triggers:
  - seo
  - search engine optimization
  - keywords
type: knowledge
---
```

### Amazon Optimizer
```yaml
---
name: amazon_optimizer
triggers:
  - amazon
  - marketplace
  - product listing
type: knowledge
---
```

### Analytics Agent
```yaml
---
name: analytics_agent
triggers:
  - analytics
  - data analysis
  - metrics
type: knowledge
---
```

## Integration Examples

### PIM System Integration

```python
from openhands.data_processing import PIMConnector, APIConfig

# Configure PIM connection
config = APIConfig(
    base_url="https://your-pim.com/api",
    api_key="your_api_key",
    timeout=30
)

# Connect and sync products
async with PIMConnector(config) as pim:
    products = await pim.get_products()

    # Enrich products
    for product in products:
        enriched = await data_enricher.enrich_product(product)
        await pim.update_product(product.id, enriched.enriched_product)
```

### ERP System Integration

```python
from openhands.data_processing import ERPConnector

# Configure ERP connection
erp_config = APIConfig(
    base_url="https://your-erp.com/api",
    username="api_user",
    password="api_password"
)

# Sync inventory and pricing data
async with ERPConnector(erp_config) as erp:
    inventory = await erp.get_inventory_levels(product_ids)
    pricing = await erp.get_pricing_data(product_ids)
```

## Performance Optimization

### Batch Processing
- Process up to 100 products per batch for enrichment
- Use async processing for large datasets
- Implement rate limiting for API calls

### Caching Strategy
- Cache enrichment results for 24 hours
- Use Redis for session storage
- Implement CDN for static assets

### Monitoring
- Track API response times
- Monitor enrichment success rates
- Set up alerts for system health

## Security Considerations

### Data Protection
- Encrypt sensitive product data
- Implement API rate limiting
- Use secure authentication methods

### Access Control
- Role-based access to different features
- API key management
- Audit logging for all operations

## Troubleshooting

### Common Issues

1. **File Upload Failures**
   - Check file format (XML/CSV)
   - Verify file size limits
   - Ensure proper encoding (UTF-8)

2. **Enrichment Errors**
   - Validate product data structure
   - Check API connectivity
   - Review error logs

3. **Analytics Issues**
   - Verify metric data format
   - Check time range parameters
   - Ensure sufficient data points

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
poetry run python -m openhands.server
```

## Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Install development dependencies
4. Run tests before submitting

### Code Style
- Follow PEP 8 for Python code
- Use TypeScript for frontend components
- Add comprehensive docstrings
- Include unit tests for new features

### Testing
```bash
# Backend tests
poetry run pytest tests/unit/test_content_enrichment.py

# Frontend tests
cd frontend
npm run test
```

## Roadmap

### Phase 1 (Current)
- ✅ Basic data processing (XML/CSV)
- ✅ Core enrichment agents
- ✅ Analytics framework
- ✅ Web dashboard

### Phase 2 (Next)
- 🔄 Advanced ML models for content generation
- 🔄 Real-time data synchronization
- 🔄 Multi-language support
- 🔄 Advanced visualization tools

### Phase 3 (Future)
- 📋 AI-powered image optimization
- 📋 Voice and video content generation
- 📋 Advanced competitive intelligence
- 📋 Automated A/B testing

## Support

### Documentation
- API Reference: `/docs` endpoint
- Micro Agent Guide: `microagents/README.md`
- Integration Examples: `examples/` directory

### Community
- GitHub Issues: Report bugs and feature requests
- Discussions: Community support and questions
- Wiki: Additional documentation and guides

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

**Built with ❤️ by the OpenHands team**

Transform your product content with AI-powered optimization and analytics!
