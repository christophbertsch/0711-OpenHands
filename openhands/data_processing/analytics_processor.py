"""
Analytics processor for content performance and business intelligence.

This module provides comprehensive analytics capabilities including
performance tracking, trend analysis, predictive modeling,
and business intelligence reporting for content optimization.
"""

import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional, Union

from openhands.core.logger import openhands_logger as logger

from .xml_processor import ProductData


class MetricType(Enum):
    """Types of analytics metrics."""

    PERFORMANCE = 'performance'
    ENGAGEMENT = 'engagement'
    CONVERSION = 'conversion'
    SEO = 'seo'
    QUALITY = 'quality'
    INVENTORY = 'inventory'
    FINANCIAL = 'financial'


class TimeFrame(Enum):
    """Time frame for analytics."""

    HOURLY = 'hourly'
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    QUARTERLY = 'quarterly'
    YEARLY = 'yearly'


@dataclass
class AnalyticsConfig:
    """Configuration for analytics processing."""

    enabled_metrics: list[MetricType] = field(default_factory=lambda: list(MetricType))
    time_frames: list[TimeFrame] = field(
        default_factory=lambda: [TimeFrame.DAILY, TimeFrame.WEEKLY, TimeFrame.MONTHLY]
    )
    retention_days: int = 365
    aggregation_intervals: dict[str, int] = field(
        default_factory=lambda: {
            'real_time': 1,  # minutes
            'hourly': 60,
            'daily': 1440,
        }
    )
    alert_thresholds: dict[str, float] = field(default_factory=dict)
    comparison_periods: list[str] = field(
        default_factory=lambda: ['previous_period', 'year_over_year']
    )


@dataclass
class MetricData:
    """Individual metric data point."""

    metric_name: str
    value: Union[float, int]
    timestamp: datetime
    dimensions: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalyticsReport:
    """Analytics report structure."""

    report_id: str
    report_type: str
    time_frame: TimeFrame
    start_date: datetime
    end_date: datetime
    metrics: list[MetricData]
    insights: list[str]
    recommendations: list[str]
    charts_data: dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)


class AnalyticsProcessor:
    """
    Comprehensive analytics processor for content and business intelligence.

    Provides advanced analytics capabilities including:
    - Performance tracking and KPI monitoring
    - Trend analysis and forecasting
    - Cohort analysis and segmentation
    - A/B testing and experimentation
    - Predictive modeling and insights
    - Real-time dashboards and alerts
    """

    def __init__(self, config: Optional[AnalyticsConfig] = None):
        """
        Initialize analytics processor.

        Args:
            config: Analytics configuration
        """
        self.config = config or AnalyticsConfig()
        self.metrics_store = defaultdict(list)
        self.reports_cache = {}
        self.alert_history = []
        self.model_cache = {}

    async def track_metric(self, metric: MetricData) -> None:
        """
        Track a single metric data point.

        Args:
            metric: Metric data to track
        """
        self.metrics_store[metric.metric_name].append(metric)

        # Check for alerts
        await self._check_alerts(metric)

        logger.debug(f'Tracked metric: {metric.metric_name} = {metric.value}')

    async def track_metrics_batch(self, metrics: list[MetricData]) -> None:
        """
        Track multiple metrics in batch.

        Args:
            metrics: List of metrics to track
        """
        for metric in metrics:
            await self.track_metric(metric)

        logger.info(f'Tracked {len(metrics)} metrics in batch')

    async def generate_performance_report(
        self,
        start_date: datetime,
        end_date: datetime,
        metric_types: Optional[list[MetricType]] = None,
    ) -> AnalyticsReport:
        """
        Generate comprehensive performance report.

        Args:
            start_date: Report start date
            end_date: Report end date
            metric_types: Optional list of metric types to include

        Returns:
            AnalyticsReport with performance data
        """
        metric_types = metric_types or self.config.enabled_metrics

        logger.info(f'Generating performance report from {start_date} to {end_date}')

        # Collect relevant metrics
        relevant_metrics = []
        for metric_name, metric_list in self.metrics_store.items():
            for metric in metric_list:
                if start_date <= metric.timestamp <= end_date:
                    relevant_metrics.append(metric)

        # Generate insights
        insights = await self._generate_insights(relevant_metrics, start_date, end_date)

        # Generate recommendations
        recommendations = await self._generate_recommendations(
            relevant_metrics, insights
        )

        # Create charts data
        charts_data = await self._generate_charts_data(
            relevant_metrics, start_date, end_date
        )

        report = AnalyticsReport(
            report_id=f'perf_{int(datetime.now().timestamp())}',
            report_type='performance',
            time_frame=self._determine_time_frame(start_date, end_date),
            start_date=start_date,
            end_date=end_date,
            metrics=relevant_metrics,
            insights=insights,
            recommendations=recommendations,
            charts_data=charts_data,
        )

        # Cache report
        self.reports_cache[report.report_id] = report

        logger.info(
            f'Generated performance report with {len(relevant_metrics)} metrics'
        )
        return report

    async def analyze_content_performance(
        self, products: list[ProductData]
    ) -> dict[str, Any]:
        """
        Analyze content performance for products.

        Args:
            products: List of products to analyze

        Returns:
            Content performance analysis
        """
        analysis = {
            'total_products': len(products),
            'content_quality_scores': {},
            'seo_performance': {},
            'completeness_analysis': {},
            'category_performance': {},
            'brand_performance': {},
            'recommendations': [],
        }

        if not products:
            return analysis

        # Analyze content quality
        quality_scores = []
        completeness_scores = []
        seo_scores = []

        category_stats = defaultdict(list)
        brand_stats = defaultdict(list)

        for product in products:
            # Content quality analysis
            quality_score = self._calculate_content_quality_score(product)
            quality_scores.append(quality_score)

            # Completeness analysis
            completeness_score = self._calculate_completeness_score(product)
            completeness_scores.append(completeness_score)

            # SEO analysis
            seo_score = self._calculate_seo_score(product)
            seo_scores.append(seo_score)

            # Category and brand grouping
            if product.category:
                category_stats[product.category].append(
                    {
                        'quality': quality_score,
                        'completeness': completeness_score,
                        'seo': seo_score,
                    }
                )

            if product.brand:
                brand_stats[product.brand].append(
                    {
                        'quality': quality_score,
                        'completeness': completeness_score,
                        'seo': seo_score,
                    }
                )

        # Aggregate statistics
        analysis['content_quality_scores'] = {
            'average': statistics.mean(quality_scores),
            'median': statistics.median(quality_scores),
            'min': min(quality_scores),
            'max': max(quality_scores),
            'distribution': self._create_distribution(quality_scores),
        }

        analysis['seo_performance'] = {
            'average': statistics.mean(seo_scores),
            'median': statistics.median(seo_scores),
            'min': min(seo_scores),
            'max': max(seo_scores),
            'distribution': self._create_distribution(seo_scores),
        }

        analysis['completeness_analysis'] = {
            'average': statistics.mean(completeness_scores),
            'median': statistics.median(completeness_scores),
            'min': min(completeness_scores),
            'max': max(completeness_scores),
            'distribution': self._create_distribution(completeness_scores),
        }

        # Category performance
        analysis['category_performance'] = {}
        for category, stats in category_stats.items():
            analysis['category_performance'][category] = {
                'product_count': len(stats),
                'avg_quality': statistics.mean([s['quality'] for s in stats]),
                'avg_completeness': statistics.mean([s['completeness'] for s in stats]),
                'avg_seo': statistics.mean([s['seo'] for s in stats]),
            }

        # Brand performance
        analysis['brand_performance'] = {}
        for brand, stats in brand_stats.items():
            analysis['brand_performance'][brand] = {
                'product_count': len(stats),
                'avg_quality': statistics.mean([s['quality'] for s in stats]),
                'avg_completeness': statistics.mean([s['completeness'] for s in stats]),
                'avg_seo': statistics.mean([s['seo'] for s in stats]),
            }

        # Generate recommendations
        analysis['recommendations'] = self._generate_content_recommendations(analysis)

        return analysis

    async def perform_trend_analysis(
        self, metric_name: str, days: int = 30
    ) -> dict[str, Any]:
        """
        Perform trend analysis for a specific metric.

        Args:
            metric_name: Name of metric to analyze
            days: Number of days to analyze

        Returns:
            Trend analysis results
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Get metric data
        metric_data = []
        if metric_name in self.metrics_store:
            for metric in self.metrics_store[metric_name]:
                if start_date <= metric.timestamp <= end_date:
                    metric_data.append(metric)

        if not metric_data:
            return {'error': f'No data found for metric {metric_name}'}

        # Sort by timestamp
        metric_data.sort(key=lambda x: x.timestamp)

        # Extract values and timestamps
        values = [m.value for m in metric_data]
        [m.timestamp for m in metric_data]

        # Calculate trend statistics
        trend_analysis = {
            'metric_name': metric_name,
            'period_days': days,
            'data_points': len(values),
            'start_value': values[0] if values else 0,
            'end_value': values[-1] if values else 0,
            'min_value': min(values) if values else 0,
            'max_value': max(values) if values else 0,
            'average_value': statistics.mean(values) if values else 0,
            'median_value': statistics.median(values) if values else 0,
            'trend_direction': self._calculate_trend_direction(values),
            'volatility': self._calculate_volatility(values),
            'growth_rate': self._calculate_growth_rate(values),
            'seasonal_patterns': self._detect_seasonal_patterns(metric_data),
            'anomalies': self._detect_anomalies(values),
            'forecast': await self._generate_forecast(values, days=7),
        }

        return trend_analysis

    async def perform_cohort_analysis(
        self, products: list[ProductData], cohort_field: str = 'category'
    ) -> dict[str, Any]:
        """
        Perform cohort analysis on products.

        Args:
            products: List of products to analyze
            cohort_field: Field to group cohorts by

        Returns:
            Cohort analysis results
        """
        cohorts = defaultdict(list)

        # Group products into cohorts
        for product in products:
            cohort_value = getattr(product, cohort_field, 'Unknown')
            if cohort_value:
                cohorts[str(cohort_value)].append(product)

        cohort_analysis = {
            'cohort_field': cohort_field,
            'total_cohorts': len(cohorts),
            'total_products': len(products),
            'cohort_details': {},
        }

        # Analyze each cohort
        for cohort_name, cohort_products in cohorts.items():
            cohort_metrics = {
                'size': len(cohort_products),
                'percentage': (len(cohort_products) / len(products)) * 100,
                'avg_quality_score': 0,
                'avg_completeness': 0,
                'price_stats': {},
                'attribute_diversity': 0,
            }

            # Calculate cohort metrics
            if cohort_products:
                quality_scores = [
                    self._calculate_content_quality_score(p) for p in cohort_products
                ]
                completeness_scores = [
                    self._calculate_completeness_score(p) for p in cohort_products
                ]

                cohort_metrics['avg_quality_score'] = statistics.mean(quality_scores)
                cohort_metrics['avg_completeness'] = statistics.mean(
                    completeness_scores
                )

                # Price statistics
                prices = [p.price for p in cohort_products if p.price]
                if prices:
                    cohort_metrics['price_stats'] = {
                        'min': min(prices),
                        'max': max(prices),
                        'average': statistics.mean(prices),
                        'median': statistics.median(prices),
                    }

                # Attribute diversity
                all_attributes = set()
                for product in cohort_products:
                    if product.attributes:
                        all_attributes.update(product.attributes.keys())
                cohort_metrics['attribute_diversity'] = len(all_attributes)

            cohort_analysis['cohort_details'][cohort_name] = cohort_metrics

        return cohort_analysis

    async def generate_ab_test_analysis(
        self,
        test_name: str,
        control_metrics: list[MetricData],
        variant_metrics: list[MetricData],
    ) -> dict[str, Any]:
        """
        Generate A/B test analysis.

        Args:
            test_name: Name of the A/B test
            control_metrics: Metrics from control group
            variant_metrics: Metrics from variant group

        Returns:
            A/B test analysis results
        """
        control_values = [m.value for m in control_metrics]
        variant_values = [m.value for m in variant_metrics]

        if not control_values or not variant_values:
            return {'error': 'Insufficient data for A/B test analysis'}

        # Calculate basic statistics
        control_mean = statistics.mean(control_values)
        variant_mean = statistics.mean(variant_values)

        # Calculate statistical significance (simplified)
        improvement = (
            ((variant_mean - control_mean) / control_mean) * 100
            if control_mean != 0
            else 0
        )

        # Confidence calculation (simplified)
        control_std = statistics.stdev(control_values) if len(control_values) > 1 else 0
        variant_std = statistics.stdev(variant_values) if len(variant_values) > 1 else 0

        # Simple t-test approximation
        pooled_std = ((control_std**2 + variant_std**2) / 2) ** 0.5
        t_stat = (
            abs(variant_mean - control_mean)
            / (pooled_std * (2 / min(len(control_values), len(variant_values))) ** 0.5)
            if pooled_std > 0
            else 0
        )

        # Determine significance (simplified)
        is_significant = t_stat > 1.96  # Approximate 95% confidence
        confidence_level = min(99.9, max(50, 50 + (t_stat * 10)))

        analysis = {
            'test_name': test_name,
            'control_group': {
                'sample_size': len(control_values),
                'mean': control_mean,
                'std_dev': control_std,
                'min': min(control_values),
                'max': max(control_values),
            },
            'variant_group': {
                'sample_size': len(variant_values),
                'mean': variant_mean,
                'std_dev': variant_std,
                'min': min(variant_values),
                'max': max(variant_values),
            },
            'results': {
                'improvement_percentage': improvement,
                'is_significant': is_significant,
                'confidence_level': confidence_level,
                'recommendation': 'Deploy variant'
                if is_significant and improvement > 0
                else 'Keep control',
            },
            'statistical_details': {
                't_statistic': t_stat,
                'pooled_std_dev': pooled_std,
                'effect_size': abs(variant_mean - control_mean) / pooled_std
                if pooled_std > 0
                else 0,
            },
        }

        return analysis

    async def generate_predictive_insights(
        self, products: list[ProductData], prediction_days: int = 30
    ) -> dict[str, Any]:
        """
        Generate predictive insights for products.

        Args:
            products: List of products to analyze
            prediction_days: Number of days to predict

        Returns:
            Predictive insights
        """
        insights = {
            'prediction_period_days': prediction_days,
            'total_products_analyzed': len(products),
            'quality_predictions': {},
            'performance_predictions': {},
            'optimization_opportunities': [],
            'risk_factors': [],
        }

        if not products:
            return insights

        # Analyze current state
        current_quality_scores = [
            self._calculate_content_quality_score(p) for p in products
        ]
        [self._calculate_completeness_score(p) for p in products]

        # Predict quality trends
        avg_quality = statistics.mean(current_quality_scores)
        quality_trend = self._predict_quality_trend(products)

        insights['quality_predictions'] = {
            'current_average_quality': avg_quality,
            'predicted_quality_change': quality_trend,
            'predicted_average_quality': avg_quality + quality_trend,
            'confidence': 75.0,  # Simplified confidence score
        }

        # Identify optimization opportunities
        low_quality_products = [
            p for p in products if self._calculate_content_quality_score(p) < 60
        ]
        incomplete_products = [
            p for p in products if self._calculate_completeness_score(p) < 80
        ]

        if low_quality_products:
            insights['optimization_opportunities'].append(
                {
                    'type': 'quality_improvement',
                    'affected_products': len(low_quality_products),
                    'potential_impact': 'High',
                    'description': f'{len(low_quality_products)} products have quality scores below 60',
                }
            )

        if incomplete_products:
            insights['optimization_opportunities'].append(
                {
                    'type': 'content_completion',
                    'affected_products': len(incomplete_products),
                    'potential_impact': 'Medium',
                    'description': f'{len(incomplete_products)} products have incomplete information',
                }
            )

        # Identify risk factors
        no_description_count = len([p for p in products if not p.description])
        no_category_count = len([p for p in products if not p.category])

        if no_description_count > len(products) * 0.1:
            insights['risk_factors'].append(
                {
                    'type': 'missing_descriptions',
                    'severity': 'High',
                    'affected_count': no_description_count,
                    'description': f'{no_description_count} products missing descriptions',
                }
            )

        if no_category_count > len(products) * 0.05:
            insights['risk_factors'].append(
                {
                    'type': 'missing_categories',
                    'severity': 'Medium',
                    'affected_count': no_category_count,
                    'description': f'{no_category_count} products missing categories',
                }
            )

        return insights

    async def create_dashboard_data(
        self, time_frame: TimeFrame = TimeFrame.DAILY
    ) -> dict[str, Any]:
        """
        Create dashboard data for visualization.

        Args:
            time_frame: Time frame for dashboard data

        Returns:
            Dashboard data structure
        """
        end_date = datetime.now()

        # Determine start date based on time frame
        if time_frame == TimeFrame.DAILY:
            start_date = end_date - timedelta(days=1)
        elif time_frame == TimeFrame.WEEKLY:
            start_date = end_date - timedelta(weeks=1)
        elif time_frame == TimeFrame.MONTHLY:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=7)

        dashboard = {
            'time_frame': time_frame.value,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'kpis': {},
            'charts': {},
            'alerts': [],
            'recent_activity': [],
        }

        # Calculate KPIs
        dashboard['kpis'] = await self._calculate_dashboard_kpis(start_date, end_date)

        # Generate chart data
        dashboard['charts'] = await self._generate_dashboard_charts(
            start_date, end_date
        )

        # Get recent alerts
        dashboard['alerts'] = self._get_recent_alerts(hours=24)

        # Get recent activity
        dashboard['recent_activity'] = self._get_recent_activity(hours=24)

        return dashboard

    def _calculate_content_quality_score(self, product: ProductData) -> float:
        """Calculate content quality score for a product."""
        score = 0.0

        # Title quality (25 points)
        if product.title:
            title_length = len(product.title)
            if 30 <= title_length <= 60:
                score += 25
            elif 20 <= title_length < 30 or 60 < title_length <= 80:
                score += 20
            else:
                score += 10

        # Description quality (35 points)
        if product.description:
            desc_length = len(product.description)
            if 150 <= desc_length <= 500:
                score += 35
            elif 100 <= desc_length < 150 or 500 < desc_length <= 1000:
                score += 25
            else:
                score += 15

        # Attributes richness (20 points)
        if product.attributes:
            attr_count = len(product.attributes)
            score += min(20, attr_count * 2)

        # Images presence (10 points)
        if product.images:
            image_count = len(product.images)
            score += min(10, image_count * 2)

        # Basic information completeness (10 points)
        basic_fields = [product.price, product.category, product.brand]
        complete_fields = sum(1 for field in basic_fields if field)
        score += (complete_fields / len(basic_fields)) * 10

        return min(100, score)

    def _calculate_completeness_score(self, product: ProductData) -> float:
        """Calculate completeness score for a product."""
        required_fields = ['id', 'title', 'description', 'price', 'category']
        optional_fields = ['brand', 'sku', 'images', 'attributes']

        score = 0.0

        # Required fields (70% of score)
        for field_name in required_fields:
            if getattr(product, field_name):
                score += 14  # 70/5 = 14 points each

        # Optional fields (30% of score)
        for field_name in optional_fields:
            value = getattr(product, field_name)
            if value:
                if field_name == 'attributes' and isinstance(value, dict) and value:
                    score += 7.5
                elif field_name == 'images' and isinstance(value, list) and value:
                    score += 7.5
                elif value:
                    score += 7.5

        return min(100, score)

    def _calculate_seo_score(self, product: ProductData) -> float:
        """Calculate SEO score for a product."""
        score = 0.0

        # Title SEO (30 points)
        if product.title:
            title_length = len(product.title)
            if 30 <= title_length <= 60:
                score += 30
            elif 20 <= title_length <= 80:
                score += 20
            else:
                score += 10

        # Description SEO (30 points)
        if product.description:
            desc_length = len(product.description)
            if 150 <= desc_length <= 300:
                score += 30
            elif 100 <= desc_length <= 500:
                score += 20
            else:
                score += 10

        # Category presence (20 points)
        if product.category:
            score += 20

        # Brand presence (10 points)
        if product.brand:
            score += 10

        # Meta attributes (10 points)
        if product.attributes:
            seo_attrs = ['meta_description', 'keywords', 'tags']
            seo_attr_count = sum(1 for attr in seo_attrs if attr in product.attributes)
            score += (seo_attr_count / len(seo_attrs)) * 10

        return min(100, score)

    def _create_distribution(self, values: list[float]) -> dict[str, int]:
        """Create distribution buckets for values."""
        if not values:
            return {}

        buckets = {'0-20': 0, '21-40': 0, '41-60': 0, '61-80': 0, '81-100': 0}

        for value in values:
            if value <= 20:
                buckets['0-20'] += 1
            elif value <= 40:
                buckets['21-40'] += 1
            elif value <= 60:
                buckets['41-60'] += 1
            elif value <= 80:
                buckets['61-80'] += 1
            else:
                buckets['81-100'] += 1

        return buckets

    def _generate_content_recommendations(self, analysis: dict[str, Any]) -> list[str]:
        """Generate content improvement recommendations."""
        recommendations = []

        # Quality recommendations
        avg_quality = analysis['content_quality_scores']['average']
        if avg_quality < 70:
            recommendations.append(
                f'Overall content quality is below target (${avg_quality:.1f}/100). Focus on improving titles and descriptions.'
            )

        # Completeness recommendations
        avg_completeness = analysis['completeness_analysis']['average']
        if avg_completeness < 80:
            recommendations.append(
                f'Content completeness needs improvement (${avg_completeness:.1f}/100). Add missing product information.'
            )

        # SEO recommendations
        avg_seo = analysis['seo_performance']['average']
        if avg_seo < 75:
            recommendations.append(
                f'SEO optimization is below target (${avg_seo:.1f}/100). Optimize titles, descriptions, and meta data.'
            )

        # Category-specific recommendations
        if 'category_performance' in analysis:
            low_performing_categories = []
            for category, stats in analysis['category_performance'].items():
                if stats['avg_quality'] < 60:
                    low_performing_categories.append(category)

            if low_performing_categories:
                recommendations.append(
                    f'Categories needing attention: {", ".join(low_performing_categories[:3])}'
                )

        return recommendations

    def _calculate_trend_direction(self, values: list[float]) -> str:
        """Calculate trend direction from values."""
        if len(values) < 2:
            return 'stable'

        # Simple linear trend
        first_half = values[: len(values) // 2]
        second_half = values[len(values) // 2 :]

        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)

        change_percent = (
            ((second_avg - first_avg) / first_avg) * 100 if first_avg != 0 else 0
        )

        if change_percent > 5:
            return 'increasing'
        elif change_percent < -5:
            return 'decreasing'
        else:
            return 'stable'

    def _calculate_volatility(self, values: list[float]) -> float:
        """Calculate volatility of values."""
        if len(values) < 2:
            return 0.0

        mean_val = statistics.mean(values)
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        std_dev = variance**0.5

        # Coefficient of variation
        return (std_dev / mean_val) * 100 if mean_val != 0 else 0.0

    def _calculate_growth_rate(self, values: list[float]) -> float:
        """Calculate growth rate from first to last value."""
        if len(values) < 2 or values[0] == 0:
            return 0.0

        return ((values[-1] - values[0]) / values[0]) * 100

    def _detect_seasonal_patterns(self, metrics: list[MetricData]) -> dict[str, Any]:
        """Detect seasonal patterns in metrics."""
        # Simplified seasonal detection
        if len(metrics) < 7:
            return {'detected': False}

        # Group by day of week
        day_groups = defaultdict(list)
        for metric in metrics:
            day_of_week = metric.timestamp.strftime('%A')
            day_groups[day_of_week].append(metric.value)

        # Calculate averages by day
        day_averages = {}
        for day, values in day_groups.items():
            if values:
                day_averages[day] = statistics.mean(values)

        if len(day_averages) < 3:
            return {'detected': False}

        # Check for significant variation
        avg_values = list(day_averages.values())
        overall_avg = statistics.mean(avg_values)
        max_deviation = max(abs(v - overall_avg) for v in avg_values)

        is_seasonal = (max_deviation / overall_avg) > 0.2 if overall_avg != 0 else False

        return {
            'detected': is_seasonal,
            'day_averages': day_averages,
            'peak_day': max(day_averages, key=day_averages.get)
            if day_averages
            else None,
            'low_day': min(day_averages, key=day_averages.get)
            if day_averages
            else None,
        }

    def _detect_anomalies(self, values: list[float]) -> list[dict[str, Any]]:
        """Detect anomalies in values."""
        if len(values) < 5:
            return []

        mean_val = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0

        anomalies = []
        threshold = 2 * std_dev  # 2 standard deviations

        for i, value in enumerate(values):
            if abs(value - mean_val) > threshold:
                anomalies.append(
                    {
                        'index': i,
                        'value': value,
                        'deviation': abs(value - mean_val),
                        'type': 'high' if value > mean_val else 'low',
                    }
                )

        return anomalies

    async def _generate_forecast(
        self, values: list[float], days: int = 7
    ) -> dict[str, Any]:
        """Generate simple forecast for values."""
        if len(values) < 3:
            return {'error': 'Insufficient data for forecasting'}

        # Simple linear trend forecast
        x = list(range(len(values)))
        y = values

        # Calculate linear regression coefficients
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))

        # Slope and intercept
        slope = (
            (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
            if (n * sum_x2 - sum_x**2) != 0
            else 0
        )
        intercept = (sum_y - slope * sum_x) / n

        # Generate forecast
        forecast_values = []
        for i in range(days):
            future_x = len(values) + i
            forecast_value = slope * future_x + intercept
            forecast_values.append(max(0, forecast_value))  # Ensure non-negative

        return {
            'forecast_days': days,
            'forecast_values': forecast_values,
            'trend_slope': slope,
            'confidence': 70.0,  # Simplified confidence
        }

    def _predict_quality_trend(self, products: list[ProductData]) -> float:
        """Predict quality trend for products."""
        # Simplified prediction based on current state
        quality_scores = [self._calculate_content_quality_score(p) for p in products]
        completeness_scores = [self._calculate_completeness_score(p) for p in products]

        avg_quality = statistics.mean(quality_scores)
        avg_completeness = statistics.mean(completeness_scores)

        # Predict improvement based on completeness gap
        quality_gap = 100 - avg_quality
        completeness_gap = 100 - avg_completeness

        # Assume 10% of gaps will be filled over prediction period
        predicted_improvement = (quality_gap + completeness_gap) * 0.1

        return predicted_improvement

    async def _check_alerts(self, metric: MetricData) -> None:
        """Check if metric triggers any alerts."""
        if not self.config.alert_thresholds:
            return

        for threshold_name, threshold_value in self.config.alert_thresholds.items():
            if threshold_name in metric.metric_name:
                if metric.value < threshold_value:
                    alert = {
                        'timestamp': datetime.now(),
                        'metric_name': metric.metric_name,
                        'value': metric.value,
                        'threshold': threshold_value,
                        'severity': 'warning'
                        if metric.value > threshold_value * 0.8
                        else 'critical',
                    }
                    self.alert_history.append(alert)
                    logger.warning(
                        f'Alert triggered: {metric.metric_name} = {metric.value} (threshold: {threshold_value})'
                    )

    async def _generate_insights(
        self, metrics: list[MetricData], start_date: datetime, end_date: datetime
    ) -> list[str]:
        """Generate insights from metrics."""
        insights = []

        if not metrics:
            insights.append('No metrics data available for the selected period.')
            return insights

        # Group metrics by name
        metric_groups = defaultdict(list)
        for metric in metrics:
            metric_groups[metric.metric_name].append(metric.value)

        # Generate insights for each metric group
        for metric_name, values in metric_groups.items():
            if len(values) > 1:
                avg_value = statistics.mean(values)
                trend = self._calculate_trend_direction(values)

                insights.append(
                    f'{metric_name}: Average {avg_value:.2f}, trend is {trend}'
                )

                if trend == 'increasing':
                    insights.append(f'Positive trend detected in {metric_name}')
                elif trend == 'decreasing':
                    insights.append(
                        f'Declining trend in {metric_name} requires attention'
                    )

        return insights

    async def _generate_recommendations(
        self, metrics: list[MetricData], insights: list[str]
    ) -> list[str]:
        """Generate recommendations based on metrics and insights."""
        recommendations = []

        # Analyze insights for recommendations
        for insight in insights:
            if 'declining' in insight.lower():
                recommendations.append(
                    'Investigate causes of declining metrics and implement improvement strategies'
                )
            elif 'positive trend' in insight.lower():
                recommendations.append(
                    'Continue current strategies that are driving positive trends'
                )

        # Generic recommendations
        if len(metrics) < 10:
            recommendations.append(
                'Increase data collection frequency for better insights'
            )

        return recommendations

    async def _generate_charts_data(
        self, metrics: list[MetricData], start_date: datetime, end_date: datetime
    ) -> dict[str, Any]:
        """Generate data for charts and visualizations."""
        charts_data = {}

        # Group metrics by name
        metric_groups = defaultdict(list)
        for metric in metrics:
            metric_groups[metric.metric_name].append(metric)

        # Generate time series data for each metric
        for metric_name, metric_list in metric_groups.items():
            # Sort by timestamp
            metric_list.sort(key=lambda x: x.timestamp)

            charts_data[metric_name] = {
                'type': 'line',
                'data': {
                    'labels': [
                        m.timestamp.strftime('%Y-%m-%d %H:%M') for m in metric_list
                    ],
                    'values': [m.value for m in metric_list],
                },
            }

        return charts_data

    def _determine_time_frame(
        self, start_date: datetime, end_date: datetime
    ) -> TimeFrame:
        """Determine appropriate time frame based on date range."""
        delta = end_date - start_date

        if delta.days <= 1:
            return TimeFrame.HOURLY
        elif delta.days <= 7:
            return TimeFrame.DAILY
        elif delta.days <= 31:
            return TimeFrame.WEEKLY
        elif delta.days <= 365:
            return TimeFrame.MONTHLY
        else:
            return TimeFrame.YEARLY

    async def _calculate_dashboard_kpis(
        self, start_date: datetime, end_date: datetime
    ) -> dict[str, Any]:
        """Calculate KPIs for dashboard."""
        kpis = {}

        # Get metrics for the period
        period_metrics = []
        for metric_list in self.metrics_store.values():
            for metric in metric_list:
                if start_date <= metric.timestamp <= end_date:
                    period_metrics.append(metric)

        if period_metrics:
            values = [m.value for m in period_metrics]
            kpis['total_metrics'] = len(period_metrics)
            kpis['average_value'] = statistics.mean(values)
            kpis['max_value'] = max(values)
            kpis['min_value'] = min(values)
        else:
            kpis['total_metrics'] = 0
            kpis['average_value'] = 0
            kpis['max_value'] = 0
            kpis['min_value'] = 0

        return kpis

    async def _generate_dashboard_charts(
        self, start_date: datetime, end_date: datetime
    ) -> dict[str, Any]:
        """Generate chart data for dashboard."""
        return await self._generate_charts_data(
            [
                m
                for metric_list in self.metrics_store.values()
                for m in metric_list
                if start_date <= m.timestamp <= end_date
            ],
            start_date,
            end_date,
        )

    def _get_recent_alerts(self, hours: int = 24) -> list[dict[str, Any]]:
        """Get recent alerts."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            alert for alert in self.alert_history if alert['timestamp'] > cutoff_time
        ]

    def _get_recent_activity(self, hours: int = 24) -> list[dict[str, Any]]:
        """Get recent activity."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        activity = []

        for metric_name, metric_list in self.metrics_store.items():
            recent_metrics = [m for m in metric_list if m.timestamp > cutoff_time]
            if recent_metrics:
                activity.append(
                    {
                        'type': 'metric_update',
                        'metric_name': metric_name,
                        'count': len(recent_metrics),
                        'latest_value': recent_metrics[-1].value,
                        'timestamp': recent_metrics[-1].timestamp,
                    }
                )

        # Sort by timestamp
        activity.sort(key=lambda x: x['timestamp'], reverse=True)
        return activity[:10]  # Return latest 10 activities

    def get_analytics_summary(self) -> dict[str, Any]:
        """Get summary of analytics processor state."""
        total_metrics = sum(
            len(metric_list) for metric_list in self.metrics_store.values()
        )

        return {
            'total_metrics_tracked': total_metrics,
            'unique_metric_types': len(self.metrics_store),
            'reports_generated': len(self.reports_cache),
            'alerts_triggered': len(self.alert_history),
            'enabled_metric_types': [mt.value for mt in self.config.enabled_metrics],
            'retention_days': self.config.retention_days,
        }
