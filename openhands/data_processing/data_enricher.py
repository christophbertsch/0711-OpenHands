"""
Data enrichment engine for content optimization and enhancement.

This module provides intelligent data enrichment capabilities including
content generation, SEO optimization, multi-channel adaptation,
and quality scoring for product information.
"""

import asyncio
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from openhands.core.logger import openhands_logger as logger

from .xml_processor import ProductData


class EnrichmentType(Enum):
    """Types of content enrichment."""

    SEO_OPTIMIZATION = 'seo_optimization'
    CONTENT_GENERATION = 'content_generation'
    AMAZON_OPTIMIZATION = 'amazon_optimization'
    MULTI_CHANNEL = 'multi_channel'
    QUALITY_SCORING = 'quality_scoring'
    TRANSLATION = 'translation'
    CATEGORIZATION = 'categorization'


@dataclass
class EnrichmentConfig:
    """Configuration for data enrichment."""

    enabled_types: list[EnrichmentType] = field(
        default_factory=lambda: list(EnrichmentType)
    )
    target_channels: list[str] = field(
        default_factory=lambda: ['website', 'amazon', 'ebay']
    )
    languages: list[str] = field(default_factory=lambda: ['en'])
    seo_keywords: list[str] = field(default_factory=list)
    brand_guidelines: dict[str, Any] = field(default_factory=dict)
    quality_thresholds: dict[str, float] = field(
        default_factory=lambda: {
            'title_length': 60,
            'description_length': 160,
            'keyword_density': 0.02,
            'readability_score': 60,
        }
    )


@dataclass
class EnrichmentResult:
    """Result of data enrichment process."""

    original_product: ProductData
    enriched_product: ProductData
    enrichment_score: float
    applied_enrichments: list[EnrichmentType]
    quality_metrics: dict[str, float]
    suggestions: list[str]
    timestamp: datetime = field(default_factory=datetime.now)


class DataEnricher:
    """
    Intelligent data enrichment engine for product content optimization.

    Provides comprehensive content enhancement including:
    - SEO optimization and keyword integration
    - Content generation and expansion
    - Multi-channel adaptation
    - Quality scoring and validation
    - Brand compliance checking
    """

    def __init__(self, config: Optional[EnrichmentConfig] = None):
        """
        Initialize data enricher.

        Args:
            config: Enrichment configuration
        """
        self.config = config or EnrichmentConfig()
        self.enrichment_history = []
        self.keyword_cache = {}
        self.category_mappings = {}

    async def enrich_product(self, product: ProductData) -> EnrichmentResult:
        """
        Enrich a single product with all configured enhancements.

        Args:
            product: Product to enrich

        Returns:
            EnrichmentResult with original and enriched data
        """
        logger.info(f'Starting enrichment for product: {product.id}')

        # Create a copy for enrichment
        enriched = ProductData(
            id=product.id,
            title=product.title,
            description=product.description,
            price=product.price,
            category=product.category,
            brand=product.brand,
            sku=product.sku,
            attributes=product.attributes.copy() if product.attributes else {},
            images=product.images.copy() if product.images else [],
        )

        applied_enrichments = []
        quality_metrics = {}
        suggestions = []

        # Apply each enabled enrichment type
        for enrichment_type in self.config.enabled_types:
            try:
                if enrichment_type == EnrichmentType.SEO_OPTIMIZATION:
                    (
                        enriched,
                        metrics,
                        seo_suggestions,
                    ) = await self._apply_seo_optimization(enriched)
                    quality_metrics.update(metrics)
                    suggestions.extend(seo_suggestions)
                    applied_enrichments.append(enrichment_type)

                elif enrichment_type == EnrichmentType.CONTENT_GENERATION:
                    (
                        enriched,
                        metrics,
                        content_suggestions,
                    ) = await self._apply_content_generation(enriched)
                    quality_metrics.update(metrics)
                    suggestions.extend(content_suggestions)
                    applied_enrichments.append(enrichment_type)

                elif enrichment_type == EnrichmentType.AMAZON_OPTIMIZATION:
                    (
                        enriched,
                        metrics,
                        amazon_suggestions,
                    ) = await self._apply_amazon_optimization(enriched)
                    quality_metrics.update(metrics)
                    suggestions.extend(amazon_suggestions)
                    applied_enrichments.append(enrichment_type)

                elif enrichment_type == EnrichmentType.QUALITY_SCORING:
                    metrics, quality_suggestions = await self._apply_quality_scoring(
                        enriched
                    )
                    quality_metrics.update(metrics)
                    suggestions.extend(quality_suggestions)
                    applied_enrichments.append(enrichment_type)

                elif enrichment_type == EnrichmentType.CATEGORIZATION:
                    (
                        enriched,
                        metrics,
                        cat_suggestions,
                    ) = await self._apply_categorization(enriched)
                    quality_metrics.update(metrics)
                    suggestions.extend(cat_suggestions)
                    applied_enrichments.append(enrichment_type)

            except Exception as e:
                logger.error(f'Error applying {enrichment_type.value}: {e}')
                suggestions.append(f'Failed to apply {enrichment_type.value}: {e}')

        # Calculate overall enrichment score
        enrichment_score = self._calculate_enrichment_score(
            product, enriched, quality_metrics
        )

        result = EnrichmentResult(
            original_product=product,
            enriched_product=enriched,
            enrichment_score=enrichment_score,
            applied_enrichments=applied_enrichments,
            quality_metrics=quality_metrics,
            suggestions=suggestions,
        )

        self.enrichment_history.append(result)
        logger.info(
            f'Enrichment completed for product {product.id} with score: {enrichment_score:.2f}'
        )

        return result

    async def enrich_products_batch(
        self, products: list[ProductData]
    ) -> list[EnrichmentResult]:
        """
        Enrich multiple products in batch.

        Args:
            products: List of products to enrich

        Returns:
            List of EnrichmentResult objects
        """
        logger.info(f'Starting batch enrichment for {len(products)} products')

        # Process products concurrently with limited concurrency
        semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent enrichments

        async def enrich_with_semaphore(product):
            async with semaphore:
                return await self.enrich_product(product)

        tasks = [enrich_with_semaphore(product) for product in products]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and log errors
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f'Error enriching product {products[i].id}: {result}')
            else:
                valid_results.append(result)

        logger.info(
            f'Batch enrichment completed: {len(valid_results)}/{len(products)} successful'
        )
        return valid_results

    async def _apply_seo_optimization(
        self, product: ProductData
    ) -> tuple[ProductData, dict[str, float], list[str]]:
        """Apply SEO optimization to product."""
        metrics = {}
        suggestions = []

        # Optimize title for SEO
        if product.title:
            original_title = product.title
            product.title = self._optimize_title_for_seo(
                product.title, product.category, product.brand
            )

            # Calculate title metrics
            metrics['title_length'] = len(product.title)
            metrics['title_keyword_density'] = self._calculate_keyword_density(
                product.title
            )

            if product.title != original_title:
                suggestions.append(
                    f"Optimized title for SEO: '{original_title}' → '{product.title}'"
                )

        # Optimize description for SEO
        if product.description:
            original_desc = product.description
            product.description = self._optimize_description_for_seo(
                product.description, product.title, product.category
            )

            # Calculate description metrics
            metrics['description_length'] = len(product.description)
            metrics['description_keyword_density'] = self._calculate_keyword_density(
                product.description
            )
            metrics['readability_score'] = self._calculate_readability_score(
                product.description
            )

            if product.description != original_desc:
                suggestions.append(
                    'Enhanced description with SEO keywords and improved readability'
                )

        # Add SEO-friendly attributes
        if not product.attributes:
            product.attributes = {}

        # Generate meta description
        if 'meta_description' not in product.attributes:
            meta_desc = self._generate_meta_description(product)
            if meta_desc:
                product.attributes['meta_description'] = meta_desc
                metrics['meta_description_length'] = len(meta_desc)
                suggestions.append('Generated SEO meta description')

        # Add structured data attributes
        product.attributes['seo_optimized'] = 'true'
        product.attributes['seo_timestamp'] = datetime.now().isoformat()

        return product, metrics, suggestions

    async def _apply_content_generation(
        self, product: ProductData
    ) -> tuple[ProductData, dict[str, float], list[str]]:
        """Apply content generation and enhancement."""
        metrics = {}
        suggestions = []

        # Enhance title if missing or too short
        if not product.title or len(product.title) < 20:
            enhanced_title = self._generate_enhanced_title(product)
            if enhanced_title:
                original_title = product.title or 'No title'
                product.title = enhanced_title
                suggestions.append(
                    f"Generated enhanced title: '{original_title}' → '{enhanced_title}'"
                )

        # Enhance description if missing or too short
        if not product.description or len(product.description) < 100:
            enhanced_desc = self._generate_enhanced_description(product)
            if enhanced_desc:
                product.description = enhanced_desc
                suggestions.append('Generated comprehensive product description')

        # Generate bullet points for key features
        bullet_points = self._generate_bullet_points(product)
        if bullet_points:
            if not product.attributes:
                product.attributes = {}
            product.attributes['key_features'] = bullet_points
            metrics['feature_count'] = len(bullet_points.split('\n'))
            suggestions.append(
                f'Generated {len(bullet_points.split("•")) - 1} key feature bullet points'
            )

        # Generate usage scenarios
        usage_scenarios = self._generate_usage_scenarios(product)
        if usage_scenarios:
            product.attributes['usage_scenarios'] = usage_scenarios
            suggestions.append('Generated product usage scenarios')

        # Calculate content richness metrics
        metrics['content_richness'] = self._calculate_content_richness(product)
        metrics['content_completeness'] = self._calculate_content_completeness(product)

        return product, metrics, suggestions

    async def _apply_amazon_optimization(
        self, product: ProductData
    ) -> tuple[ProductData, dict[str, float], list[str]]:
        """Apply Amazon marketplace optimization."""
        metrics = {}
        suggestions = []

        # Optimize title for Amazon (150-200 characters)
        if product.title:
            amazon_title = self._optimize_title_for_amazon(product)
            if amazon_title != product.title:
                if not product.attributes:
                    product.attributes = {}
                product.attributes['amazon_title'] = amazon_title
                metrics['amazon_title_length'] = len(amazon_title)
                suggestions.append('Created Amazon-optimized title')

        # Generate Amazon bullet points (5 key features)
        amazon_bullets = self._generate_amazon_bullet_points(product)
        if amazon_bullets:
            if not product.attributes:
                product.attributes = {}
            product.attributes['amazon_bullet_points'] = amazon_bullets
            metrics['amazon_bullet_count'] = len(amazon_bullets.split('\n'))
            suggestions.append('Generated Amazon-style bullet points')

        # Generate backend search terms for Amazon
        search_terms = self._generate_amazon_search_terms(product)
        if search_terms:
            product.attributes['amazon_search_terms'] = search_terms
            suggestions.append('Generated Amazon backend search terms')

        # Optimize for Amazon A9 algorithm
        a9_score = self._calculate_amazon_a9_score(product)
        metrics['amazon_a9_score'] = a9_score

        if a9_score < 70:
            suggestions.append(
                f'Amazon A9 optimization score: {a9_score:.1f}/100 - Consider improving keywords and content'
            )

        return product, metrics, suggestions

    async def _apply_quality_scoring(
        self, product: ProductData
    ) -> tuple[dict[str, float], list[str]]:
        """Apply quality scoring and validation."""
        metrics = {}
        suggestions = []

        # Title quality metrics
        if product.title:
            metrics['title_quality'] = self._score_title_quality(product.title)
            if metrics['title_quality'] < 70:
                suggestions.append(
                    'Title quality could be improved - consider adding more descriptive keywords'
                )

        # Description quality metrics
        if product.description:
            metrics['description_quality'] = self._score_description_quality(
                product.description
            )
            if metrics['description_quality'] < 70:
                suggestions.append(
                    'Description quality could be improved - add more details and benefits'
                )

        # Content completeness
        metrics['completeness_score'] = self._calculate_content_completeness(product)
        if metrics['completeness_score'] < 80:
            suggestions.append(
                'Product information is incomplete - consider adding missing fields'
            )

        # Brand compliance
        if self.config.brand_guidelines:
            metrics['brand_compliance'] = self._check_brand_compliance(product)
            if metrics['brand_compliance'] < 90:
                suggestions.append('Content may not fully comply with brand guidelines')

        # Overall quality score
        quality_scores = [
            score for score in metrics.values() if isinstance(score, (int, float))
        ]
        metrics['overall_quality'] = (
            sum(quality_scores) / len(quality_scores) if quality_scores else 0
        )

        return metrics, suggestions

    async def _apply_categorization(
        self, product: ProductData
    ) -> tuple[ProductData, dict[str, float], list[str]]:
        """Apply intelligent categorization."""
        metrics = {}
        suggestions = []

        # Auto-categorize based on title and description
        if not product.category or product.category.lower() in [
            'uncategorized',
            'other',
            'misc',
        ]:
            suggested_category = self._suggest_category(product)
            if suggested_category:
                original_category = product.category or 'No category'
                product.category = suggested_category
                suggestions.append(
                    f"Suggested category: '{original_category}' → '{suggested_category}'"
                )

        # Add category confidence score
        if product.category:
            confidence = self._calculate_category_confidence(product)
            metrics['category_confidence'] = confidence

            if confidence < 70:
                suggestions.append(
                    f'Category confidence is low ({confidence:.1f}%) - manual review recommended'
                )

        # Generate category-specific attributes
        category_attrs = self._generate_category_attributes(product)
        if category_attrs:
            if not product.attributes:
                product.attributes = {}
            product.attributes.update(category_attrs)
            suggestions.append(
                f'Added {len(category_attrs)} category-specific attributes'
            )

        return product, metrics, suggestions

    def _optimize_title_for_seo(
        self, title: str, category: Optional[str], brand: Optional[str]
    ) -> str:
        """Optimize title for SEO."""
        if not title:
            return title

        # Clean and enhance title
        optimized = title.strip()

        # Add brand if not present and available
        if brand and brand.lower() not in optimized.lower():
            optimized = f'{brand} {optimized}'

        # Add category keywords if relevant and not present
        if category and len(optimized) < 50:
            category_keywords = self._extract_category_keywords(category)
            for keyword in category_keywords:
                if (
                    keyword.lower() not in optimized.lower()
                    and len(optimized) + len(keyword) < 60
                ):
                    optimized = f'{optimized} {keyword}'

        # Ensure proper capitalization
        optimized = self._capitalize_title(optimized)

        return optimized[:60]  # Limit to 60 characters for SEO

    def _optimize_description_for_seo(
        self, description: str, title: Optional[str], category: Optional[str]
    ) -> str:
        """Optimize description for SEO."""
        if not description:
            return description

        # Extract keywords from title and category
        keywords = set()
        if title:
            keywords.update(self._extract_keywords(title))
        if category:
            keywords.update(self._extract_category_keywords(category))

        # Add SEO keywords from config
        keywords.update(self.config.seo_keywords)

        # Enhance description with keywords naturally
        enhanced = description
        for keyword in keywords:
            if keyword.lower() not in enhanced.lower() and len(enhanced) < 500:
                # Try to add keyword naturally
                enhanced = self._add_keyword_naturally(enhanced, keyword)

        return enhanced

    def _generate_meta_description(self, product: ProductData) -> Optional[str]:
        """Generate SEO meta description for product."""
        if not product.title and not product.description:
            return None

        # Start with product title or name
        meta_parts = []
        if product.title:
            meta_parts.append(product.title)

        # Add key benefits from description
        if product.description:
            # Take first sentence or first 100 characters
            desc_part = product.description.split('.')[0]
            if len(desc_part) > 100:
                desc_part = desc_part[:100] + '...'
            meta_parts.append(desc_part)

        # Add brand if available
        if product.brand:
            meta_parts.append(f'by {product.brand}')

        # Add price if available
        if product.price:
            meta_parts.append(f'${product.price}')

        meta_description = '. '.join(meta_parts)

        # Ensure it's within SEO limits (150-160 characters)
        if len(meta_description) > 160:
            meta_description = meta_description[:157] + '...'

        return meta_description

    def _generate_enhanced_title(self, product: ProductData) -> Optional[str]:
        """Generate enhanced title for product."""
        components = []

        # Add brand
        if product.brand:
            components.append(product.brand)

        # Add main product identifier
        if product.title:
            components.append(product.title)
        elif product.sku:
            components.append(f'Product {product.sku}')

        # Add key attributes
        if product.attributes:
            key_attrs = ['color', 'size', 'model', 'type', 'material']
            for attr in key_attrs:
                if attr in product.attributes and len(' '.join(components)) < 40:
                    components.append(str(product.attributes[attr]))

        # Add category if space allows
        if product.category and len(' '.join(components)) < 45:
            components.append(product.category)

        return ' '.join(components) if components else None

    def _generate_enhanced_description(self, product: ProductData) -> Optional[str]:
        """Generate enhanced description for product."""
        if not product.title and not product.brand:
            return None

        description_parts = []

        # Opening statement
        product_name = product.title or f'{product.brand} Product'
        description_parts.append(f'Discover the exceptional {product_name}.')

        # Key features from attributes
        if product.attributes:
            features = []
            feature_attrs = [
                'material',
                'color',
                'size',
                'weight',
                'dimensions',
                'capacity',
            ]
            for attr in feature_attrs:
                if attr in product.attributes:
                    features.append(f'{attr}: {product.attributes[attr]}')

            if features:
                description_parts.append(
                    f'Key specifications include {", ".join(features[:3])}.'
                )

        # Benefits statement
        if product.category:
            description_parts.append(
                f'Perfect for {product.category.lower()} applications.'
            )

        # Quality assurance
        if product.brand:
            description_parts.append(
                f"Backed by {product.brand}'s commitment to quality and performance."
            )

        # Call to action
        description_parts.append('Experience the difference today.')

        return ' '.join(description_parts)

    def _generate_bullet_points(self, product: ProductData) -> Optional[str]:
        """Generate bullet points for key features."""
        if not product.attributes:
            return None

        bullets = []

        # Priority attributes for bullet points
        priority_attrs = [
            'material',
            'color',
            'size',
            'weight',
            'dimensions',
            'capacity',
            'power',
            'warranty',
            'compatibility',
        ]

        for attr in priority_attrs:
            if attr in product.attributes and len(bullets) < 5:
                value = product.attributes[attr]
                bullets.append(f'• {attr.title()}: {value}')

        # Add other important attributes
        for key, value in product.attributes.items():
            if key not in priority_attrs and len(bullets) < 5:
                if len(str(value)) < 50:  # Keep bullet points concise
                    bullets.append(f'• {key.replace("_", " ").title()}: {value}')

        return '\n'.join(bullets) if bullets else None

    def _generate_usage_scenarios(self, product: ProductData) -> Optional[str]:
        """Generate usage scenarios based on product category."""
        if not product.category:
            return None

        category_lower = product.category.lower()
        scenarios = []

        # Category-specific scenarios
        if 'electronics' in category_lower:
            scenarios = [
                'Home entertainment',
                'Office productivity',
                'Travel companion',
            ]
        elif 'clothing' in category_lower or 'apparel' in category_lower:
            scenarios = ['Casual wear', 'Professional settings', 'Special occasions']
        elif 'kitchen' in category_lower or 'cooking' in category_lower:
            scenarios = [
                'Daily meal preparation',
                'Special occasions',
                'Professional cooking',
            ]
        elif 'tools' in category_lower:
            scenarios = [
                'Professional projects',
                'Home improvement',
                'Maintenance tasks',
            ]
        else:
            scenarios = ['Daily use', 'Special projects', 'Professional applications']

        return f'Ideal for: {", ".join(scenarios)}'

    def _optimize_title_for_amazon(self, product: ProductData) -> str:
        """Optimize title specifically for Amazon."""
        components = []

        # Amazon title format: Brand + Product Name + Key Features + Size/Color
        if product.brand:
            components.append(product.brand)

        if product.title:
            # Remove brand from title if already added
            title_clean = product.title
            if product.brand and product.brand.lower() in title_clean.lower():
                title_clean = title_clean.replace(product.brand, '').strip()
            components.append(title_clean)

        # Add key attributes for Amazon
        if product.attributes:
            amazon_attrs = ['color', 'size', 'model', 'pack_size', 'quantity']
            for attr in amazon_attrs:
                if attr in product.attributes and len(' '.join(components)) < 150:
                    components.append(str(product.attributes[attr]))

        amazon_title = ' '.join(components)
        return amazon_title[:200]  # Amazon limit

    def _generate_amazon_bullet_points(self, product: ProductData) -> Optional[str]:
        """Generate Amazon-style bullet points."""
        bullets = []

        # Amazon bullet point best practices
        if product.description:
            # Extract key benefits from description
            sentences = product.description.split('.')
            for sentence in sentences[:3]:
                if len(sentence.strip()) > 10:
                    bullets.append(f'• {sentence.strip()}')

        # Add attribute-based bullets
        if product.attributes:
            priority_attrs = [
                'material',
                'dimensions',
                'weight',
                'warranty',
                'compatibility',
            ]
            for attr in priority_attrs:
                if attr in product.attributes and len(bullets) < 5:
                    bullets.append(
                        f'• {attr.replace("_", " ").title()}: {product.attributes[attr]}'
                    )

        # Ensure we have 5 bullets (Amazon recommendation)
        while len(bullets) < 5 and len(bullets) < 3:
            if product.category:
                bullets.append(f'• Perfect for {product.category.lower()} applications')
            if product.brand:
                bullets.append(f'• Trusted {product.brand} quality and reliability')
            break

        return '\n'.join(bullets[:5]) if bullets else None

    def _generate_amazon_search_terms(self, product: ProductData) -> Optional[str]:
        """Generate backend search terms for Amazon."""
        terms = set()

        # Extract from title
        if product.title:
            terms.update(self._extract_keywords(product.title))

        # Extract from category
        if product.category:
            terms.update(self._extract_category_keywords(product.category))

        # Add synonyms and variations
        if product.brand:
            terms.add(product.brand.lower())

        # Add attribute values
        if product.attributes:
            for value in product.attributes.values():
                if isinstance(value, str) and len(value.split()) <= 2:
                    terms.add(value.lower())

        # Filter and format for Amazon (250 characters max per field)
        filtered_terms = [term for term in terms if len(term) > 2 and len(term) < 20]
        search_terms = ' '.join(filtered_terms[:20])  # Limit number of terms

        return search_terms[:250] if search_terms else None

    def _calculate_keyword_density(self, text: str) -> float:
        """Calculate keyword density in text."""
        if not text or not self.config.seo_keywords:
            return 0.0

        text_lower = text.lower()
        total_words = len(text.split())
        keyword_count = 0

        for keyword in self.config.seo_keywords:
            keyword_count += text_lower.count(keyword.lower())

        return (keyword_count / total_words) if total_words > 0 else 0.0

    def _calculate_readability_score(self, text: str) -> float:
        """Calculate readability score (simplified Flesch score)."""
        if not text:
            return 0.0

        sentences = len([s for s in text.split('.') if s.strip()])
        words = len(text.split())
        syllables = sum(self._count_syllables(word) for word in text.split())

        if sentences == 0 or words == 0:
            return 0.0

        # Simplified Flesch Reading Ease formula
        score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
        return max(0, min(100, score))

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)."""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False

        for char in word:
            if char in vowels:
                if not previous_was_vowel:
                    syllable_count += 1
                previous_was_vowel = True
            else:
                previous_was_vowel = False

        # Handle silent e
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1

        return max(1, syllable_count)

    def _calculate_content_richness(self, product: ProductData) -> float:
        """Calculate content richness score."""
        score = 0.0

        # Title contribution
        if product.title:
            score += min(20, len(product.title.split()) * 2)

        # Description contribution
        if product.description:
            score += min(40, len(product.description.split()) * 0.5)

        # Attributes contribution
        if product.attributes:
            score += min(30, len(product.attributes) * 3)

        # Images contribution
        if product.images:
            score += min(10, len(product.images) * 2)

        return min(100, score)

    def _calculate_content_completeness(self, product: ProductData) -> float:
        """Calculate content completeness score."""
        required_fields = ['id', 'title', 'description', 'price', 'category']
        optional_fields = ['brand', 'sku', 'images', 'attributes']

        score = 0.0

        # Required fields (70% of score)
        for field in required_fields:
            if getattr(product, field):
                score += 14  # 70/5 = 14 points each

        # Optional fields (30% of score)
        for field in optional_fields:
            value = getattr(product, field)
            if value:
                if field == 'attributes' and isinstance(value, dict):
                    score += min(
                        7.5, len(value) * 1.5
                    )  # Up to 7.5 points for attributes
                elif field == 'images' and isinstance(value, list):
                    score += min(7.5, len(value) * 2.5)  # Up to 7.5 points for images
                else:
                    score += 7.5  # 30/4 = 7.5 points each for brand, sku

        return min(100, score)

    def _calculate_enrichment_score(
        self, original: ProductData, enriched: ProductData, metrics: dict[str, float]
    ) -> float:
        """Calculate overall enrichment score."""
        # Base score from quality metrics
        quality_scores = [
            v for k, v in metrics.items() if 'quality' in k or 'score' in k
        ]
        base_score = sum(quality_scores) / len(quality_scores) if quality_scores else 50

        # Improvement bonus
        improvement_bonus = 0

        # Title improvement
        if enriched.title != original.title:
            improvement_bonus += 10

        # Description improvement
        if enriched.description != original.description:
            improvement_bonus += 15

        # Attributes added
        original_attrs = len(original.attributes) if original.attributes else 0
        enriched_attrs = len(enriched.attributes) if enriched.attributes else 0
        if enriched_attrs > original_attrs:
            improvement_bonus += min(20, (enriched_attrs - original_attrs) * 2)

        # Category improvement
        if enriched.category != original.category and enriched.category:
            improvement_bonus += 5

        return min(100, base_score + improvement_bonus)

    def _extract_keywords(self, text: str) -> list[str]:
        """Extract keywords from text."""
        if not text:
            return []

        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

        # Filter out common stop words
        stop_words = {
            'the',
            'and',
            'for',
            'are',
            'but',
            'not',
            'you',
            'all',
            'can',
            'had',
            'her',
            'was',
            'one',
            'our',
            'out',
            'day',
            'get',
            'has',
            'him',
            'his',
            'how',
            'its',
            'may',
            'new',
            'now',
            'old',
            'see',
            'two',
            'who',
            'boy',
            'did',
            'she',
            'use',
            'way',
            'will',
            'with',
        }

        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        return list(set(keywords))

    def _extract_category_keywords(self, category: str) -> list[str]:
        """Extract keywords from category."""
        if not category:
            return []

        # Split category path and extract keywords
        parts = re.split(r'[>/|]', category)
        keywords = []

        for part in parts:
            keywords.extend(self._extract_keywords(part))

        return keywords

    def _add_keyword_naturally(self, text: str, keyword: str) -> str:
        """Add keyword to text naturally."""
        # Simple implementation - could be enhanced with NLP
        sentences = text.split('.')

        # Try to add to the first sentence if it's not too long
        if sentences and len(sentences[0]) < 100:
            sentences[0] = f'{sentences[0].strip()} with {keyword}'
            return '.'.join(sentences)

        # Otherwise append as new sentence
        return f'{text.rstrip(".")}. Features {keyword}.'

    def _capitalize_title(self, title: str) -> str:
        """Properly capitalize title."""
        # Simple title case with exceptions for common words
        words = title.split()
        capitalized = []

        for i, word in enumerate(words):
            if i == 0 or word.lower() not in [
                'and',
                'or',
                'but',
                'for',
                'nor',
                'on',
                'at',
                'to',
                'from',
                'by',
                'of',
                'in',
                'with',
            ]:
                capitalized.append(word.capitalize())
            else:
                capitalized.append(word.lower())

        return ' '.join(capitalized)

    def _suggest_category(self, product: ProductData) -> Optional[str]:
        """Suggest category based on product information."""
        # Simple category suggestion based on keywords
        category_keywords = {
            'Electronics': [
                'electronic',
                'digital',
                'computer',
                'phone',
                'tablet',
                'camera',
                'audio',
                'video',
            ],
            'Clothing & Apparel': [
                'shirt',
                'pants',
                'dress',
                'shoes',
                'jacket',
                'clothing',
                'apparel',
                'fashion',
            ],
            'Home & Garden': [
                'home',
                'garden',
                'furniture',
                'decor',
                'kitchen',
                'bathroom',
                'bedroom',
            ],
            'Sports & Outdoors': [
                'sports',
                'outdoor',
                'fitness',
                'exercise',
                'camping',
                'hiking',
                'athletic',
            ],
            'Books & Media': [
                'book',
                'dvd',
                'cd',
                'magazine',
                'media',
                'entertainment',
            ],
            'Health & Beauty': [
                'health',
                'beauty',
                'cosmetic',
                'skincare',
                'wellness',
                'medical',
            ],
            'Automotive': [
                'car',
                'auto',
                'vehicle',
                'automotive',
                'parts',
                'accessories',
            ],
            'Tools & Hardware': [
                'tool',
                'hardware',
                'construction',
                'repair',
                'maintenance',
            ],
        }

        text = f'{product.title or ""} {product.description or ""}'.lower()

        category_scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                category_scores[category] = score

        if category_scores:
            return max(category_scores, key=category_scores.get)

        return None

    def _calculate_category_confidence(self, product: ProductData) -> float:
        """Calculate confidence in category assignment."""
        if not product.category:
            return 0.0

        # Simple confidence calculation based on keyword matches
        category_keywords = {
            'electronics': ['electronic', 'digital', 'computer', 'tech'],
            'clothing': ['shirt', 'pants', 'dress', 'apparel'],
            'home': ['home', 'house', 'furniture', 'decor'],
            'sports': ['sports', 'fitness', 'athletic', 'outdoor'],
        }

        category_lower = product.category.lower()
        text = f'{product.title or ""} {product.description or ""}'.lower()

        # Find matching keyword set
        matching_keywords = []
        for cat_key, keywords in category_keywords.items():
            if cat_key in category_lower:
                matching_keywords = keywords
                break

        if not matching_keywords:
            return 50.0  # Default confidence for unknown categories

        # Count keyword matches
        matches = sum(1 for keyword in matching_keywords if keyword in text)
        confidence = min(100, 30 + (matches * 20))  # Base 30% + 20% per match

        return confidence

    def _generate_category_attributes(self, product: ProductData) -> dict[str, str]:
        """Generate category-specific attributes."""
        if not product.category:
            return {}

        category_lower = product.category.lower()
        attributes = {}

        # Category-specific attribute suggestions
        if 'electronics' in category_lower:
            attributes.update(
                {
                    'power_source': 'Electric',
                    'warranty': '1 Year',
                    'connectivity': 'Wired/Wireless',
                }
            )
        elif 'clothing' in category_lower:
            attributes.update(
                {
                    'care_instructions': 'Machine Washable',
                    'fit': 'Regular',
                    'season': 'All Season',
                }
            )
        elif 'home' in category_lower:
            attributes.update(
                {
                    'room_type': 'Living Room',
                    'assembly_required': 'Yes',
                    'style': 'Modern',
                }
            )

        return attributes

    def _score_title_quality(self, title: str) -> float:
        """Score title quality."""
        if not title:
            return 0.0

        score = 0.0

        # Length score (optimal 30-60 characters)
        length = len(title)
        if 30 <= length <= 60:
            score += 30
        elif 20 <= length < 30 or 60 < length <= 80:
            score += 20
        else:
            score += 10

        # Word count score (optimal 4-8 words)
        word_count = len(title.split())
        if 4 <= word_count <= 8:
            score += 25
        elif 3 <= word_count < 4 or 8 < word_count <= 10:
            score += 15
        else:
            score += 5

        # Keyword presence
        if self.config.seo_keywords:
            keyword_matches = sum(
                1
                for keyword in self.config.seo_keywords
                if keyword.lower() in title.lower()
            )
            score += min(25, keyword_matches * 8)
        else:
            score += 15  # Default if no keywords configured

        # Capitalization and formatting
        if title[0].isupper():
            score += 10

        # No excessive punctuation
        if title.count('!') <= 1 and title.count('?') <= 1:
            score += 10

        return min(100, score)

    def _score_description_quality(self, description: str) -> float:
        """Score description quality."""
        if not description:
            return 0.0

        score = 0.0

        # Length score (optimal 150-300 characters)
        length = len(description)
        if 150 <= length <= 300:
            score += 25
        elif 100 <= length < 150 or 300 < length <= 500:
            score += 20
        else:
            score += 10

        # Sentence structure
        sentences = [s.strip() for s in description.split('.') if s.strip()]
        if 2 <= len(sentences) <= 5:
            score += 20
        else:
            score += 10

        # Keyword density
        keyword_density = self._calculate_keyword_density(description)
        if 0.01 <= keyword_density <= 0.03:
            score += 20
        elif keyword_density > 0:
            score += 10

        # Readability
        readability = self._calculate_readability_score(description)
        if readability >= 60:
            score += 20
        elif readability >= 40:
            score += 15
        else:
            score += 5

        # Benefits vs features (simple heuristic)
        benefit_words = [
            'improve',
            'enhance',
            'better',
            'perfect',
            'ideal',
            'excellent',
            'superior',
        ]
        benefit_count = sum(1 for word in benefit_words if word in description.lower())
        score += min(15, benefit_count * 3)

        return min(100, score)

    def _check_brand_compliance(self, product: ProductData) -> float:
        """Check brand compliance score."""
        if not self.config.brand_guidelines:
            return 100.0  # No guidelines to check

        score = 100.0
        guidelines = self.config.brand_guidelines

        # Check required brand elements
        if 'required_brand_mention' in guidelines:
            brand_mention = guidelines['required_brand_mention']
            text = f'{product.title or ""} {product.description or ""}'.lower()
            if brand_mention.lower() not in text:
                score -= 20

        # Check forbidden words
        if 'forbidden_words' in guidelines:
            forbidden = guidelines['forbidden_words']
            text = f'{product.title or ""} {product.description or ""}'.lower()
            for word in forbidden:
                if word.lower() in text:
                    score -= 10

        # Check tone requirements
        if 'tone' in guidelines:
            required_tone = guidelines['tone'].lower()
            if required_tone == 'professional':
                # Check for casual language
                casual_words = ['awesome', 'cool', 'super', 'amazing']
                text = f'{product.title or ""} {product.description or ""}'.lower()
                casual_count = sum(1 for word in casual_words if word in text)
                score -= casual_count * 5

        return max(0, score)

    def _calculate_amazon_a9_score(self, product: ProductData) -> float:
        """Calculate Amazon A9 algorithm optimization score."""
        score = 0.0

        # Title optimization (25 points)
        if product.title:
            title_length = len(product.title)
            if 150 <= title_length <= 200:
                score += 25
            elif 100 <= title_length < 150:
                score += 20
            else:
                score += 10

        # Bullet points (20 points)
        if product.attributes and 'amazon_bullet_points' in product.attributes:
            bullet_count = len(product.attributes['amazon_bullet_points'].split('\n'))
            if bullet_count == 5:
                score += 20
            elif bullet_count >= 3:
                score += 15
            else:
                score += 5

        # Backend search terms (15 points)
        if product.attributes and 'amazon_search_terms' in product.attributes:
            search_terms = product.attributes['amazon_search_terms']
            if len(search_terms) > 100:
                score += 15
            elif len(search_terms) > 50:
                score += 10
            else:
                score += 5

        # Images (15 points)
        if product.images:
            image_count = len(product.images)
            if image_count >= 7:
                score += 15
            elif image_count >= 5:
                score += 12
            elif image_count >= 3:
                score += 8
            else:
                score += 3

        # Price competitiveness (10 points) - simplified
        if product.price:
            score += 10  # Assume competitive if price is present

        # Category relevance (10 points)
        if product.category:
            score += 10

        # Brand presence (5 points)
        if product.brand:
            score += 5

        return min(100, score)

    def get_enrichment_statistics(self) -> dict[str, Any]:
        """Get enrichment statistics."""
        if not self.enrichment_history:
            return {'total_enrichments': 0}

        scores = [result.enrichment_score for result in self.enrichment_history]
        applied_types = {}

        for result in self.enrichment_history:
            for enrichment_type in result.applied_enrichments:
                applied_types[enrichment_type.value] = (
                    applied_types.get(enrichment_type.value, 0) + 1
                )

        return {
            'total_enrichments': len(self.enrichment_history),
            'average_score': sum(scores) / len(scores),
            'min_score': min(scores),
            'max_score': max(scores),
            'applied_enrichment_types': applied_types,
            'success_rate': len([s for s in scores if s >= 70]) / len(scores) * 100,
        }
