"""
Content enrichment API routes.

This module provides REST API endpoints for content enrichment operations
including data processing, optimization, and analytics.
"""

import os
import tempfile
from datetime import datetime
from typing import Any, Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
)
from pydantic import BaseModel, Field

from openhands.core.logger import openhands_logger as logger
from openhands.data_processing import (
    AnalyticsProcessor,
    CSVProcessor,
    DataEnricher,
    XMLProcessor,
)
from openhands.data_processing.analytics_processor import (
    MetricData,
    MetricType,
    TimeFrame,
)
from openhands.data_processing.data_enricher import EnrichmentConfig, EnrichmentType
from openhands.data_processing.xml_processor import ProductData

router = APIRouter(prefix='/api/content-enrichment', tags=['content-enrichment'])

# Global instances (in production, these would be properly managed)
xml_processor = XMLProcessor()
csv_processor = CSVProcessor()
data_enricher = DataEnricher()
analytics_processor = AnalyticsProcessor()


# Pydantic models for API
class ProductDataModel(BaseModel):
    """Product data model for API."""

    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    sku: Optional[str] = None
    attributes: Optional[dict[str, Any]] = None
    images: Optional[list[str]] = None


class EnrichmentConfigModel(BaseModel):
    """Enrichment configuration model."""

    enabled_types: list[str] = Field(
        default_factory=lambda: ['seo_optimization', 'content_generation']
    )
    target_channels: list[str] = Field(default_factory=lambda: ['website', 'amazon'])
    languages: list[str] = Field(default_factory=lambda: ['en'])
    seo_keywords: list[str] = Field(default_factory=list)
    brand_guidelines: dict[str, Any] = Field(default_factory=dict)


class AnalyticsConfigModel(BaseModel):
    """Analytics configuration model."""

    enabled_metrics: list[str] = Field(
        default_factory=lambda: ['performance', 'quality']
    )
    time_frames: list[str] = Field(default_factory=lambda: ['daily', 'weekly'])
    retention_days: int = 365


class MetricDataModel(BaseModel):
    """Metric data model."""

    metric_name: str
    value: float
    timestamp: Optional[datetime] = None
    dimensions: Optional[dict[str, Any]] = None
    metadata: Optional[dict[str, Any]] = None


# Data Processing Endpoints


@router.post('/upload/xml')
async def upload_xml_file(
    file: UploadFile = File(...), background_tasks: BackgroundTasks = None
):
    """
    Upload and process XML file.

    Args:
        file: XML file to process
        background_tasks: Background task manager

    Returns:
        Processing results
    """
    if not file.filename.endswith('.xml'):
        raise HTTPException(status_code=400, detail='File must be XML format')

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Process XML file
        products = xml_processor.process_xml_file(temp_file_path)

        # Clean up temp file
        os.unlink(temp_file_path)

        # Convert to API models
        product_models = []
        for product in products:
            product_models.append(
                ProductDataModel(
                    id=product.id,
                    title=product.title,
                    description=product.description,
                    price=product.price,
                    category=product.category,
                    brand=product.brand,
                    sku=product.sku,
                    attributes=product.attributes,
                    images=product.images,
                )
            )

        # Track metrics
        if background_tasks:
            background_tasks.add_task(
                track_processing_metric,
                'xml_processing',
                len(products),
                {'file_name': file.filename},
            )

        return {
            'status': 'success',
            'products_processed': len(products),
            'file_name': file.filename,
            'products': product_models,
        }

    except Exception as e:
        logger.error(f'Error processing XML file: {e}')
        raise HTTPException(
            status_code=500, detail=f'Error processing XML file: {str(e)}'
        )


@router.post('/upload/csv')
async def upload_csv_file(
    file: UploadFile = File(...),
    delimiter: str = Form(','),
    has_header: bool = Form(True),
    background_tasks: BackgroundTasks = None,
):
    """
    Upload and process CSV file.

    Args:
        file: CSV file to process
        delimiter: CSV delimiter character
        has_header: Whether CSV has header row
        background_tasks: Background task manager

    Returns:
        Processing results
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail='File must be CSV format')

    try:
        # Configure CSV processor
        from openhands.data_processing.csv_processor import CSVConfig

        config = CSVConfig(delimiter=delimiter, has_header=has_header)
        csv_processor.config = config

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Process CSV file
        products = csv_processor.process_csv_file(temp_file_path)

        # Clean up temp file
        os.unlink(temp_file_path)

        # Convert to API models
        product_models = []
        for product in products:
            product_models.append(
                ProductDataModel(
                    id=product.id,
                    title=product.title,
                    description=product.description,
                    price=product.price,
                    category=product.category,
                    brand=product.brand,
                    sku=product.sku,
                    attributes=product.attributes,
                    images=product.images,
                )
            )

        # Track metrics
        if background_tasks:
            background_tasks.add_task(
                track_processing_metric,
                'csv_processing',
                len(products),
                {'file_name': file.filename, 'delimiter': delimiter},
            )

        return {
            'status': 'success',
            'products_processed': len(products),
            'file_name': file.filename,
            'products': product_models,
        }

    except Exception as e:
        logger.error(f'Error processing CSV file: {e}')
        raise HTTPException(
            status_code=500, detail=f'Error processing CSV file: {str(e)}'
        )


@router.post('/validate/xml')
async def validate_xml_file(file: UploadFile = File(...)):
    """
    Validate XML file structure.

    Args:
        file: XML file to validate

    Returns:
        Validation results
    """
    if not file.filename.endswith('.xml'):
        raise HTTPException(status_code=400, detail='File must be XML format')

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Validate XML file
        validation_results = xml_processor.validate_xml_schema(temp_file_path)

        # Clean up temp file
        os.unlink(temp_file_path)

        return validation_results

    except Exception as e:
        logger.error(f'Error validating XML file: {e}')
        raise HTTPException(
            status_code=500, detail=f'Error validating XML file: {str(e)}'
        )


@router.post('/validate/csv')
async def validate_csv_file(
    file: UploadFile = File(...),
    delimiter: str = Form(','),
    has_header: bool = Form(True),
):
    """
    Validate CSV file structure.

    Args:
        file: CSV file to validate
        delimiter: CSV delimiter character
        has_header: Whether CSV has header row

    Returns:
        Validation results
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail='File must be CSV format')

    try:
        # Configure CSV processor
        from openhands.data_processing.csv_processor import CSVConfig

        config = CSVConfig(delimiter=delimiter, has_header=has_header)
        csv_processor.config = config

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Validate CSV file
        validation_results = csv_processor.validate_csv_file(temp_file_path)

        # Clean up temp file
        os.unlink(temp_file_path)

        return validation_results

    except Exception as e:
        logger.error(f'Error validating CSV file: {e}')
        raise HTTPException(
            status_code=500, detail=f'Error validating CSV file: {str(e)}'
        )


# Content Enrichment Endpoints


@router.post('/enrich/product')
async def enrich_single_product(
    product: ProductDataModel,
    config: Optional[EnrichmentConfigModel] = None,
    background_tasks: BackgroundTasks = None,
):
    """
    Enrich a single product.

    Args:
        product: Product data to enrich
        config: Enrichment configuration
        background_tasks: Background task manager

    Returns:
        Enrichment results
    """
    try:
        # Convert API model to internal model
        product_data = ProductData(
            id=product.id,
            title=product.title,
            description=product.description,
            price=product.price,
            category=product.category,
            brand=product.brand,
            sku=product.sku,
            attributes=product.attributes or {},
            images=product.images or [],
        )

        # Configure enricher if config provided
        if config:
            enrichment_config = EnrichmentConfig(
                enabled_types=[
                    EnrichmentType(t)
                    for t in config.enabled_types
                    if t in [e.value for e in EnrichmentType]
                ],
                target_channels=config.target_channels,
                languages=config.languages,
                seo_keywords=config.seo_keywords,
                brand_guidelines=config.brand_guidelines,
            )
            data_enricher.config = enrichment_config

        # Enrich product
        result = await data_enricher.enrich_product(product_data)

        # Track metrics
        if background_tasks:
            background_tasks.add_task(
                track_enrichment_metric,
                result.enrichment_score,
                len(result.applied_enrichments),
                {'product_id': product.id},
            )

        return {
            'status': 'success',
            'original_product': ProductDataModel(
                id=result.original_product.id,
                title=result.original_product.title,
                description=result.original_product.description,
                price=result.original_product.price,
                category=result.original_product.category,
                brand=result.original_product.brand,
                sku=result.original_product.sku,
                attributes=result.original_product.attributes,
                images=result.original_product.images,
            ),
            'enriched_product': ProductDataModel(
                id=result.enriched_product.id,
                title=result.enriched_product.title,
                description=result.enriched_product.description,
                price=result.enriched_product.price,
                category=result.enriched_product.category,
                brand=result.enriched_product.brand,
                sku=result.enriched_product.sku,
                attributes=result.enriched_product.attributes,
                images=result.enriched_product.images,
            ),
            'enrichment_score': result.enrichment_score,
            'applied_enrichments': [e.value for e in result.applied_enrichments],
            'quality_metrics': result.quality_metrics,
            'suggestions': result.suggestions,
            'timestamp': result.timestamp.isoformat(),
        }

    except Exception as e:
        logger.error(f'Error enriching product: {e}')
        raise HTTPException(
            status_code=500, detail=f'Error enriching product: {str(e)}'
        )


@router.post('/enrich/batch')
async def enrich_products_batch(
    products: list[ProductDataModel],
    config: Optional[EnrichmentConfigModel] = None,
    background_tasks: BackgroundTasks = None,
):
    """
    Enrich multiple products in batch.

    Args:
        products: List of products to enrich
        config: Enrichment configuration
        background_tasks: Background task manager

    Returns:
        Batch enrichment results
    """
    if len(products) > 100:
        raise HTTPException(
            status_code=400, detail='Batch size limited to 100 products'
        )

    try:
        # Convert API models to internal models
        product_data_list = []
        for product in products:
            product_data_list.append(
                ProductData(
                    id=product.id,
                    title=product.title,
                    description=product.description,
                    price=product.price,
                    category=product.category,
                    brand=product.brand,
                    sku=product.sku,
                    attributes=product.attributes or {},
                    images=product.images or [],
                )
            )

        # Configure enricher if config provided
        if config:
            enrichment_config = EnrichmentConfig(
                enabled_types=[
                    EnrichmentType(t)
                    for t in config.enabled_types
                    if t in [e.value for e in EnrichmentType]
                ],
                target_channels=config.target_channels,
                languages=config.languages,
                seo_keywords=config.seo_keywords,
                brand_guidelines=config.brand_guidelines,
            )
            data_enricher.config = enrichment_config

        # Enrich products in batch
        results = await data_enricher.enrich_products_batch(product_data_list)

        # Convert results to API format
        api_results = []
        total_score = 0
        total_enrichments = 0

        for result in results:
            api_results.append(
                {
                    'product_id': result.original_product.id,
                    'enrichment_score': result.enrichment_score,
                    'applied_enrichments': [
                        e.value for e in result.applied_enrichments
                    ],
                    'quality_metrics': result.quality_metrics,
                    'suggestions': result.suggestions,
                    'enriched_product': ProductDataModel(
                        id=result.enriched_product.id,
                        title=result.enriched_product.title,
                        description=result.enriched_product.description,
                        price=result.enriched_product.price,
                        category=result.enriched_product.category,
                        brand=result.enriched_product.brand,
                        sku=result.enriched_product.sku,
                        attributes=result.enriched_product.attributes,
                        images=result.enriched_product.images,
                    ),
                }
            )
            total_score += result.enrichment_score
            total_enrichments += len(result.applied_enrichments)

        # Track metrics
        if background_tasks:
            background_tasks.add_task(
                track_batch_enrichment_metric,
                len(results),
                total_score / len(results) if results else 0,
                total_enrichments,
            )

        return {
            'status': 'success',
            'products_processed': len(results),
            'average_enrichment_score': total_score / len(results) if results else 0,
            'total_enrichments_applied': total_enrichments,
            'results': api_results,
        }

    except Exception as e:
        logger.error(f'Error in batch enrichment: {e}')
        raise HTTPException(
            status_code=500, detail=f'Error in batch enrichment: {str(e)}'
        )


# Analytics Endpoints


@router.post('/analytics/track-metric')
async def track_metric(metric: MetricDataModel):
    """
    Track a single metric.

    Args:
        metric: Metric data to track

    Returns:
        Success confirmation
    """
    try:
        metric_data = MetricData(
            metric_name=metric.metric_name,
            value=metric.value,
            timestamp=metric.timestamp or datetime.now(),
            dimensions=metric.dimensions or {},
            metadata=metric.metadata or {},
        )

        await analytics_processor.track_metric(metric_data)

        return {
            'status': 'success',
            'message': f'Metric {metric.metric_name} tracked successfully',
        }

    except Exception as e:
        logger.error(f'Error tracking metric: {e}')
        raise HTTPException(status_code=500, detail=f'Error tracking metric: {str(e)}')


@router.post('/analytics/track-metrics')
async def track_metrics_batch(metrics: list[MetricDataModel]):
    """
    Track multiple metrics in batch.

    Args:
        metrics: List of metrics to track

    Returns:
        Success confirmation
    """
    if len(metrics) > 1000:
        raise HTTPException(
            status_code=400, detail='Batch size limited to 1000 metrics'
        )

    try:
        metric_data_list = []
        for metric in metrics:
            metric_data_list.append(
                MetricData(
                    metric_name=metric.metric_name,
                    value=metric.value,
                    timestamp=metric.timestamp or datetime.now(),
                    dimensions=metric.dimensions or {},
                    metadata=metric.metadata or {},
                )
            )

        await analytics_processor.track_metrics_batch(metric_data_list)

        return {
            'status': 'success',
            'message': f'{len(metrics)} metrics tracked successfully',
        }

    except Exception as e:
        logger.error(f'Error tracking metrics batch: {e}')
        raise HTTPException(
            status_code=500, detail=f'Error tracking metrics batch: {str(e)}'
        )


@router.get('/analytics/performance-report')
async def get_performance_report(
    start_date: datetime = Query(..., description='Report start date'),
    end_date: datetime = Query(..., description='Report end date'),
    metric_types: Optional[list[str]] = Query(
        None, description='Metric types to include'
    ),
):
    """
    Generate performance report.

    Args:
        start_date: Report start date
        end_date: Report end date
        metric_types: Optional list of metric types

    Returns:
        Performance report
    """
    try:
        # Convert metric types if provided
        metric_type_enums = None
        if metric_types:
            metric_type_enums = [
                MetricType(mt)
                for mt in metric_types
                if mt in [m.value for m in MetricType]
            ]

        report = await analytics_processor.generate_performance_report(
            start_date, end_date, metric_type_enums
        )

        return {
            'report_id': report.report_id,
            'report_type': report.report_type,
            'time_frame': report.time_frame.value,
            'start_date': report.start_date.isoformat(),
            'end_date': report.end_date.isoformat(),
            'metrics_count': len(report.metrics),
            'insights': report.insights,
            'recommendations': report.recommendations,
            'charts_data': report.charts_data,
            'generated_at': report.generated_at.isoformat(),
        }

    except Exception as e:
        logger.error(f'Error generating performance report: {e}')
        raise HTTPException(
            status_code=500, detail=f'Error generating performance report: {str(e)}'
        )


@router.post('/analytics/content-performance')
async def analyze_content_performance(products: list[ProductDataModel]):
    """
    Analyze content performance for products.

    Args:
        products: List of products to analyze

    Returns:
        Content performance analysis
    """
    if len(products) > 500:
        raise HTTPException(status_code=400, detail='Analysis limited to 500 products')

    try:
        # Convert API models to internal models
        product_data_list = []
        for product in products:
            product_data_list.append(
                ProductData(
                    id=product.id,
                    title=product.title,
                    description=product.description,
                    price=product.price,
                    category=product.category,
                    brand=product.brand,
                    sku=product.sku,
                    attributes=product.attributes or {},
                    images=product.images or [],
                )
            )

        analysis = await analytics_processor.analyze_content_performance(
            product_data_list
        )

        return analysis

    except Exception as e:
        logger.error(f'Error analyzing content performance: {e}')
        raise HTTPException(
            status_code=500, detail=f'Error analyzing content performance: {str(e)}'
        )


@router.get('/analytics/trend-analysis/{metric_name}')
async def get_trend_analysis(
    metric_name: str, days: int = Query(30, description='Number of days to analyze')
):
    """
    Get trend analysis for a metric.

    Args:
        metric_name: Name of metric to analyze
        days: Number of days to analyze

    Returns:
        Trend analysis results
    """
    try:
        analysis = await analytics_processor.perform_trend_analysis(metric_name, days)
        return analysis

    except Exception as e:
        logger.error(f'Error performing trend analysis: {e}')
        raise HTTPException(
            status_code=500, detail=f'Error performing trend analysis: {str(e)}'
        )


@router.get('/analytics/dashboard')
async def get_dashboard_data(
    time_frame: str = Query('daily', description='Time frame for dashboard'),
):
    """
    Get dashboard data.

    Args:
        time_frame: Time frame for dashboard data

    Returns:
        Dashboard data
    """
    try:
        # Convert time frame string to enum
        time_frame_enum = TimeFrame.DAILY
        if time_frame in [tf.value for tf in TimeFrame]:
            time_frame_enum = TimeFrame(time_frame)

        dashboard_data = await analytics_processor.create_dashboard_data(
            time_frame_enum
        )
        return dashboard_data

    except Exception as e:
        logger.error(f'Error getting dashboard data: {e}')
        raise HTTPException(
            status_code=500, detail=f'Error getting dashboard data: {str(e)}'
        )


# Utility Endpoints


@router.get('/stats/enrichment')
async def get_enrichment_stats():
    """Get enrichment statistics."""
    try:
        stats = data_enricher.get_enrichment_statistics()
        return stats
    except Exception as e:
        logger.error(f'Error getting enrichment stats: {e}')
        raise HTTPException(
            status_code=500, detail=f'Error getting enrichment stats: {str(e)}'
        )


@router.get('/stats/analytics')
async def get_analytics_stats():
    """Get analytics statistics."""
    try:
        stats = analytics_processor.get_analytics_summary()
        return stats
    except Exception as e:
        logger.error(f'Error getting analytics stats: {e}')
        raise HTTPException(
            status_code=500, detail=f'Error getting analytics stats: {str(e)}'
        )


@router.get('/health')
async def health_check():
    """Health check endpoint."""
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'xml_processor': 'active',
            'csv_processor': 'active',
            'data_enricher': 'active',
            'analytics_processor': 'active',
        },
    }


# Background task functions


async def track_processing_metric(
    metric_type: str, count: int, metadata: dict[str, Any]
):
    """Track processing metric in background."""
    try:
        metric = MetricData(
            metric_name=f'processing_{metric_type}',
            value=count,
            timestamp=datetime.now(),
            metadata=metadata,
        )
        await analytics_processor.track_metric(metric)
    except Exception as e:
        logger.error(f'Error tracking processing metric: {e}')


async def track_enrichment_metric(
    score: float, enrichment_count: int, metadata: dict[str, Any]
):
    """Track enrichment metric in background."""
    try:
        score_metric = MetricData(
            metric_name='enrichment_score',
            value=score,
            timestamp=datetime.now(),
            metadata=metadata,
        )
        count_metric = MetricData(
            metric_name='enrichment_count',
            value=enrichment_count,
            timestamp=datetime.now(),
            metadata=metadata,
        )
        await analytics_processor.track_metrics_batch([score_metric, count_metric])
    except Exception as e:
        logger.error(f'Error tracking enrichment metric: {e}')


async def track_batch_enrichment_metric(
    product_count: int, avg_score: float, total_enrichments: int
):
    """Track batch enrichment metrics in background."""
    try:
        metrics = [
            MetricData(
                metric_name='batch_enrichment_products',
                value=product_count,
                timestamp=datetime.now(),
            ),
            MetricData(
                metric_name='batch_enrichment_avg_score',
                value=avg_score,
                timestamp=datetime.now(),
            ),
            MetricData(
                metric_name='batch_enrichment_total_enrichments',
                value=total_enrichments,
                timestamp=datetime.now(),
            ),
        ]
        await analytics_processor.track_metrics_batch(metrics)
    except Exception as e:
        logger.error(f'Error tracking batch enrichment metrics: {e}')
