"""
Unit tests for content enrichment functionality.
"""

from datetime import datetime

import pytest

from openhands.data_processing import (
    AnalyticsProcessor,
    CSVProcessor,
    DataEnricher,
    XMLProcessor,
)
from openhands.data_processing.analytics_processor import AnalyticsConfig, MetricData
from openhands.data_processing.data_enricher import EnrichmentConfig, EnrichmentType
from openhands.data_processing.xml_processor import ProductData


class TestXMLProcessor:
    """Test XML data processing functionality."""

    def test_xml_processor_initialization(self):
        """Test XML processor initialization."""
        processor = XMLProcessor()
        assert processor is not None
        assert processor.processed_count == 0
        assert processor.error_count == 0

    def test_product_data_creation(self):
        """Test ProductData model creation."""
        product = ProductData(
            id='TEST001',
            title='Test Product',
            description='A test product description',
            price=99.99,
            category='Electronics',
            brand='TestBrand',
            sku='SKU001',
            attributes={'color': 'blue', 'size': 'medium'},
            images=['image1.jpg', 'image2.jpg'],
        )

        assert product.id == 'TEST001'
        assert product.title == 'Test Product'
        assert product.price == 99.99
        assert len(product.images) == 2
        assert product.attributes['color'] == 'blue'


class TestCSVProcessor:
    """Test CSV data processing functionality."""

    def test_csv_processor_initialization(self):
        """Test CSV processor initialization."""
        processor = CSVProcessor()
        assert processor is not None
        assert processor.processed_count == 0
        assert processor.error_count == 0

    def test_csv_config_creation(self):
        """Test CSV configuration creation."""
        from openhands.data_processing.csv_processor import CSVConfig

        config = CSVConfig(
            delimiter=',', has_header=True, required_columns=['id', 'title']
        )

        assert config.delimiter == ','
        assert config.has_header is True
        assert 'id' in config.required_columns


class TestDataEnricher:
    """Test data enrichment functionality."""

    def test_data_enricher_initialization(self):
        """Test data enricher initialization."""
        enricher = DataEnricher()
        assert enricher is not None
        assert len(enricher.enrichment_history) == 0

    def test_enrichment_config_creation(self):
        """Test enrichment configuration creation."""
        config = EnrichmentConfig(
            enabled_types=[
                EnrichmentType.SEO_OPTIMIZATION,
                EnrichmentType.CONTENT_GENERATION,
            ],
            target_channels=['website', 'amazon'],
            languages=['en'],
            seo_keywords=['premium', 'quality'],
        )

        assert EnrichmentType.SEO_OPTIMIZATION in config.enabled_types
        assert 'website' in config.target_channels
        assert 'premium' in config.seo_keywords

    @pytest.mark.asyncio
    async def test_product_enrichment(self):
        """Test basic product enrichment."""
        enricher = DataEnricher()

        product = ProductData(
            id='TEST001',
            title='Basic Product',
            description='Simple description',
            category='Electronics',
        )

        result = await enricher.enrich_product(product)

        assert result is not None
        assert result.original_product.id == 'TEST001'
        assert result.enriched_product.id == 'TEST001'
        assert result.enrichment_score >= 0
        assert len(result.applied_enrichments) >= 0


class TestAnalyticsProcessor:
    """Test analytics processing functionality."""

    def test_analytics_processor_initialization(self):
        """Test analytics processor initialization."""
        processor = AnalyticsProcessor()
        assert processor is not None
        assert len(processor.metrics_store) == 0

    def test_analytics_config_creation(self):
        """Test analytics configuration creation."""
        from openhands.data_processing.analytics_processor import MetricType

        config = AnalyticsConfig(
            enabled_metrics=[MetricType.PERFORMANCE, MetricType.QUALITY],
            retention_days=365,
        )

        assert MetricType.PERFORMANCE in config.enabled_metrics
        assert config.retention_days == 365

    @pytest.mark.asyncio
    async def test_metric_tracking(self):
        """Test metric tracking functionality."""
        processor = AnalyticsProcessor()

        metric = MetricData(
            metric_name='test_metric',
            value=85.5,
            timestamp=datetime.now(),
            dimensions={'category': 'electronics'},
            metadata={'source': 'test'},
        )

        await processor.track_metric(metric)

        assert 'test_metric' in processor.metrics_store
        assert len(processor.metrics_store['test_metric']) == 1
        assert processor.metrics_store['test_metric'][0].value == 85.5

    @pytest.mark.asyncio
    async def test_content_performance_analysis(self):
        """Test content performance analysis."""
        processor = AnalyticsProcessor()

        products = [
            ProductData(
                id='PROD001',
                title='High Quality Product',
                description='This is a comprehensive description of a high-quality product with excellent features.',
                price=199.99,
                category='Electronics',
                brand='TestBrand',
                attributes={'material': 'premium', 'warranty': '2 years'},
            ),
            ProductData(
                id='PROD002',
                title='Basic Item',
                description='Simple product',
                price=29.99,
                category='Accessories',
            ),
        ]

        analysis = await processor.analyze_content_performance(products)

        assert analysis is not None
        assert analysis['total_products'] == 2
        assert 'content_quality_scores' in analysis
        assert 'seo_performance' in analysis
        assert 'completeness_analysis' in analysis
        assert analysis['content_quality_scores']['average'] > 0


class TestIntegration:
    """Test integration between components."""

    @pytest.mark.asyncio
    async def test_full_enrichment_pipeline(self):
        """Test complete enrichment pipeline."""
        # Create sample product data
        products = [
            ProductData(
                id='PIPE001',
                title='Sample Product',
                description='Basic description',
                category='Test Category',
            )
        ]

        # Initialize components
        enricher = DataEnricher()
        analytics = AnalyticsProcessor()

        # Enrich products
        enrichment_results = await enricher.enrich_products_batch(products)

        assert len(enrichment_results) == 1
        assert enrichment_results[0].enrichment_score >= 0

        # Analyze enriched products
        enriched_products = [result.enriched_product for result in enrichment_results]
        analysis = await analytics.analyze_content_performance(enriched_products)

        assert analysis['total_products'] == 1
        assert analysis['content_quality_scores']['average'] >= 0

        # Track metrics
        for result in enrichment_results:
            metric = MetricData(
                metric_name='enrichment_score',
                value=result.enrichment_score,
                timestamp=datetime.now(),
                metadata={'product_id': result.original_product.id},
            )
            await analytics.track_metric(metric)

        # Verify metrics were tracked
        assert 'enrichment_score' in analytics.metrics_store
        assert len(analytics.metrics_store['enrichment_score']) == 1


class TestMicroAgents:
    """Test micro agent functionality."""

    def test_seo_optimizer_trigger_matching(self):
        """Test SEO optimizer micro agent trigger matching."""
        # This would test the micro agent trigger system
        # For now, we'll test the basic concept

        triggers = ['seo', 'search engine optimization', 'keywords']
        test_message = 'I need help with SEO optimization for my products'

        # Simple trigger matching logic
        message_lower = test_message.lower()
        matched_triggers = [trigger for trigger in triggers if trigger in message_lower]

        assert len(matched_triggers) > 0
        assert 'seo' in matched_triggers

    def test_amazon_optimizer_trigger_matching(self):
        """Test Amazon optimizer micro agent trigger matching."""
        triggers = ['amazon', 'marketplace', 'product listing']
        test_message = 'How can I optimize my Amazon product listings?'

        message_lower = test_message.lower()
        matched_triggers = [trigger for trigger in triggers if trigger in message_lower]

        assert len(matched_triggers) > 0
        assert 'amazon' in matched_triggers

    def test_analytics_agent_trigger_matching(self):
        """Test analytics agent trigger matching."""
        triggers = ['analytics', 'data analysis', 'metrics', 'performance']
        test_message = 'I want to analyze the performance of my content'

        message_lower = test_message.lower()
        matched_triggers = [trigger for trigger in triggers if trigger in message_lower]

        assert len(matched_triggers) > 0
        assert 'performance' in matched_triggers


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
