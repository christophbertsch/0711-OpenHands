#!/usr/bin/env python3
"""
Content Enrichment Platform Demo

This script demonstrates the key features of the content enrichment and analytics platform.
"""

import asyncio
from datetime import datetime
from pathlib import Path

from openhands.data_processing import (
    AnalyticsProcessor,
    CSVProcessor,
    DataEnricher,
    XMLProcessor,
)
from openhands.data_processing.analytics_processor import MetricData
from openhands.data_processing.data_enricher import EnrichmentConfig, EnrichmentType


async def demo_xml_processing():
    """Demonstrate XML data processing."""
    print('🔄 XML Data Processing Demo')
    print('=' * 50)

    processor = XMLProcessor()
    xml_file = Path('sample_data/products.xml')

    if xml_file.exists():
        # Process XML file
        products = processor.process_xml_file(xml_file)
        print(f'✅ Processed {len(products)} products from XML')

        # Show sample product
        if products:
            sample = products[0]
            print('\n📦 Sample Product:')
            print(f'   ID: {sample.id}')
            print(f'   Title: {sample.title}')
            print(f'   Price: ${sample.price}')
            print(f'   Category: {sample.category}')
            print(
                f'   Attributes: {len(sample.attributes) if sample.attributes else 0}'
            )
            print(f'   Images: {len(sample.images) if sample.images else 0}')

        # Get processing stats
        stats = processor.get_processing_stats()
        print('\n📊 Processing Stats:')
        print(f'   Success Rate: {stats["success_rate"]:.1f}%')
        print(f'   Processed: {stats["processed_count"]}')
        print(f'   Errors: {stats["error_count"]}')

        return products
    else:
        print('❌ Sample XML file not found')
        return []


async def demo_csv_processing():
    """Demonstrate CSV data processing."""
    print('\n🔄 CSV Data Processing Demo')
    print('=' * 50)

    processor = CSVProcessor()
    csv_file = Path('sample_data/products.csv')

    if csv_file.exists():
        # Process CSV file
        products = processor.process_csv_file(csv_file)
        print(f'✅ Processed {len(products)} products from CSV')

        # Show sample product
        if products:
            sample = products[0]
            print('\n📦 Sample Product:')
            print(f'   ID: {sample.id}')
            print(f'   Title: {sample.title}')
            print(f'   Price: ${sample.price}')
            print(f'   Category: {sample.category}')
            print(
                f'   Attributes: {len(sample.attributes) if sample.attributes else 0}'
            )

        return products
    else:
        print('❌ Sample CSV file not found')
        return []


async def demo_content_enrichment(products):
    """Demonstrate content enrichment."""
    print('\n🚀 Content Enrichment Demo')
    print('=' * 50)

    if not products:
        print('❌ No products to enrich')
        return []

    # Configure enrichment
    config = EnrichmentConfig(
        enabled_types=[
            EnrichmentType.SEO_OPTIMIZATION,
            EnrichmentType.CONTENT_GENERATION,
            EnrichmentType.AMAZON_OPTIMIZATION,
            EnrichmentType.QUALITY_SCORING,
        ],
        target_channels=['website', 'amazon', 'ebay'],
        languages=['en'],
        seo_keywords=['premium', 'quality', 'professional', 'advanced'],
        brand_guidelines={'tone': 'professional', 'required_brand_mention': 'brand'},
    )

    enricher = DataEnricher(config)

    # Enrich first few products
    sample_products = products[:3]
    print(f'🔄 Enriching {len(sample_products)} products...')

    results = await enricher.enrich_products_batch(sample_products)

    print('✅ Enrichment completed!')

    # Show results
    for result in results:
        print(f'\n📈 Product: {result.original_product.id}')
        print(f'   Enrichment Score: {result.enrichment_score:.1f}/100')
        print(f'   Applied Enrichments: {len(result.applied_enrichments)}')
        print(f'   Suggestions: {len(result.suggestions)}')

        # Show quality metrics
        if result.quality_metrics:
            print('   Quality Metrics:')
            for metric, value in list(result.quality_metrics.items())[:3]:
                print(f'     - {metric}: {value:.1f}')

        # Show top suggestions
        if result.suggestions:
            print('   Top Suggestions:')
            for suggestion in result.suggestions[:2]:
                print(f'     - {suggestion}')

    # Get enrichment statistics
    stats = enricher.get_enrichment_statistics()
    print('\n📊 Enrichment Statistics:')
    print(f'   Total Enrichments: {stats["total_enrichments"]}')
    print(f'   Average Score: {stats["average_score"]:.1f}')
    print(f'   Success Rate: {stats["success_rate"]:.1f}%')

    return results


async def demo_analytics(products, enrichment_results):
    """Demonstrate analytics capabilities."""
    print('\n📊 Analytics Demo')
    print('=' * 50)

    processor = AnalyticsProcessor()

    # Track some sample metrics
    print('🔄 Tracking sample metrics...')

    metrics = []
    for i, product in enumerate(products[:5]):
        # Simulate various metrics
        metrics.extend(
            [
                MetricData(
                    metric_name='content_quality',
                    value=75 + (i * 5),
                    timestamp=datetime.now(),
                    dimensions={'product_id': product.id, 'category': product.category},
                ),
                MetricData(
                    metric_name='seo_score',
                    value=65 + (i * 7),
                    timestamp=datetime.now(),
                    dimensions={'product_id': product.id, 'category': product.category},
                ),
                MetricData(
                    metric_name='completeness',
                    value=80 + (i * 3),
                    timestamp=datetime.now(),
                    dimensions={'product_id': product.id, 'category': product.category},
                ),
            ]
        )

    await processor.track_metrics_batch(metrics)
    print(f'✅ Tracked {len(metrics)} metrics')

    # Analyze content performance
    print('\n🔍 Analyzing content performance...')
    analysis = await processor.analyze_content_performance(products)

    print('📈 Content Analysis Results:')
    print(f'   Total Products: {analysis["total_products"]}')
    print(f'   Avg Quality Score: {analysis["content_quality_scores"]["average"]:.1f}')
    print(f'   Avg SEO Score: {analysis["seo_performance"]["average"]:.1f}')
    print(f'   Avg Completeness: {analysis["completeness_analysis"]["average"]:.1f}')

    # Show quality distribution
    print('\n📊 Quality Score Distribution:')
    for range_key, count in analysis['content_quality_scores']['distribution'].items():
        print(f'   {range_key}: {count} products')

    # Show recommendations
    if analysis['recommendations']:
        print('\n💡 Recommendations:')
        for rec in analysis['recommendations'][:3]:
            print(f'   - {rec}')

    # Perform trend analysis
    print('\n📈 Trend Analysis:')
    trend = await processor.perform_trend_analysis('content_quality', days=7)
    if 'error' not in trend:
        print(f'   Metric: {trend["metric_name"]}')
        print(f'   Data Points: {trend["data_points"]}')
        print(f'   Average Value: {trend["average_value"]:.1f}')
        print(f'   Trend Direction: {trend["trend_direction"]}')
        print(f'   Growth Rate: {trend["growth_rate"]:.1f}%')

    # Generate dashboard data
    print('\n🎛️ Dashboard Data:')
    dashboard = await processor.create_dashboard_data()
    print(f'   Time Frame: {dashboard["time_frame"]}')
    print(f'   KPIs: {len(dashboard["kpis"])} metrics')
    print(f'   Charts: {len(dashboard["charts"])} charts')
    print(f'   Alerts: {len(dashboard["alerts"])} active alerts')

    return analysis


async def demo_micro_agents():
    """Demonstrate micro agent capabilities."""
    print('\n🤖 Micro Agents Demo')
    print('=' * 50)

    # Simulate micro agent trigger matching
    test_messages = [
        'I need help with SEO optimization for my products',
        'How can I optimize my Amazon product listings?',
        'I want to analyze the performance of my content',
        'Can you help me enrich my product descriptions?',
    ]

    agent_triggers = {
        'SEO Optimizer': ['seo', 'search engine optimization', 'keywords'],
        'Amazon Optimizer': ['amazon', 'marketplace', 'product listing'],
        'Analytics Agent': ['analytics', 'performance', 'metrics'],
        'Content Enrichment': ['enrich', 'content generation', 'descriptions'],
    }

    print('🔍 Testing micro agent trigger matching:')

    for message in test_messages:
        print(f"\n💬 Message: '{message}'")
        matched_agents = []

        message_lower = message.lower()
        for agent_name, triggers in agent_triggers.items():
            for trigger in triggers:
                if trigger in message_lower:
                    matched_agents.append(agent_name)
                    break

        if matched_agents:
            print(f'   🎯 Matched Agents: {", ".join(matched_agents)}')
        else:
            print('   ❌ No agents matched')

    print('\n✅ Micro agent system operational!')


async def main():
    """Run the complete demo."""
    print('🎉 Content Enrichment & Analytics Platform Demo')
    print('=' * 60)
    print('This demo showcases the key features of the platform:')
    print('• XML/CSV data processing')
    print('• AI-powered content enrichment')
    print('• Advanced analytics and insights')
    print('• Micro agent system')
    print('=' * 60)

    try:
        # Demo data processing
        xml_products = await demo_xml_processing()
        csv_products = await demo_csv_processing()

        # Use XML products if available, otherwise CSV
        products = xml_products if xml_products else csv_products

        if products:
            # Demo content enrichment
            enrichment_results = await demo_content_enrichment(products)

            # Demo analytics
            await demo_analytics(products, enrichment_results)

        # Demo micro agents
        await demo_micro_agents()

        print('\n🎉 Demo completed successfully!')
        print('\n🚀 Next Steps:')
        print('• Start the server: poetry run python -m openhands.server')
        print('• Access the dashboard: http://localhost:3000/content-enrichment')
        print('• Upload your own product data')
        print('• Explore the API documentation: http://localhost:8000/docs')

    except Exception as e:
        print(f'\n❌ Demo failed with error: {e}')
        import traceback

        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())
