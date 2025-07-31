"""
API connector for PIM and ERP system integrations.

This module provides connectors for various external systems including
Product Information Management (PIM) systems, Enterprise Resource Planning (ERP)
systems, and other third-party APIs for data synchronization and enrichment.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional
from urllib.parse import urlencode, urljoin

import aiohttp

from openhands.core.logger import openhands_logger as logger

from .xml_processor import ProductData


@dataclass
class APIConfig:
    """Configuration for API connections."""

    base_url: str
    api_key: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    headers: dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    rate_limit: int = 100  # requests per minute
    retry_attempts: int = 3
    retry_delay: float = 1.0
    verify_ssl: bool = True


@dataclass
class SyncConfig:
    """Configuration for data synchronization."""

    batch_size: int = 100
    sync_interval: int = 3600  # seconds
    auto_sync: bool = False
    conflict_resolution: str = 'latest'  # 'latest', 'manual', 'source_wins'
    sync_fields: list[str] = field(default_factory=list)
    exclude_fields: list[str] = field(default_factory=list)


class APIConnector(ABC):
    """
    Abstract base class for API connectors.

    Provides common functionality for connecting to external APIs
    including authentication, rate limiting, error handling, and retry logic.
    """

    def __init__(self, config: APIConfig, sync_config: Optional[SyncConfig] = None):
        """
        Initialize API connector.

        Args:
            config: API configuration
            sync_config: Synchronization configuration
        """
        self.config = config
        self.sync_config = sync_config or SyncConfig()
        self.session = None
        self.last_request_time = 0
        self.request_count = 0
        self.rate_limit_reset = time.time() + 60

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            headers=self.config.headers,
            connector=aiohttp.TCPConnector(verify_ssl=self.config.verify_ssl),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    def _check_rate_limit(self):
        """Check and enforce rate limiting."""
        current_time = time.time()

        # Reset counter if minute has passed
        if current_time > self.rate_limit_reset:
            self.request_count = 0
            self.rate_limit_reset = current_time + 60

        # Check if we've exceeded rate limit
        if self.request_count >= self.config.rate_limit:
            sleep_time = self.rate_limit_reset - current_time
            if sleep_time > 0:
                logger.info(
                    f'Rate limit reached, sleeping for {sleep_time:.2f} seconds'
                )
                time.sleep(sleep_time)
                self.request_count = 0
                self.rate_limit_reset = time.time() + 60

        self.request_count += 1

    async def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> dict[str, Any]:
        """
        Make HTTP request with error handling and retries.

        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request parameters

        Returns:
            Response data as dictionary
        """
        url = urljoin(self.config.base_url, endpoint)

        for attempt in range(self.config.retry_attempts):
            try:
                self._check_rate_limit()

                # Add authentication if configured
                if self.config.api_key:
                    kwargs.setdefault('headers', {})['Authorization'] = (
                        f'Bearer {self.config.api_key}'
                    )
                elif self.config.username and self.config.password:
                    kwargs['auth'] = aiohttp.BasicAuth(
                        self.config.username, self.config.password
                    )

                async with self.session.request(method, url, **kwargs) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:  # Rate limited
                        retry_after = int(response.headers.get('Retry-After', 60))
                        logger.warning(f'Rate limited, waiting {retry_after} seconds')
                        await asyncio.sleep(retry_after)
                        continue
                    else:
                        response.raise_for_status()

            except Exception as e:
                logger.warning(f'Request attempt {attempt + 1} failed: {e}')
                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(self.config.retry_delay * (2**attempt))
                else:
                    raise

        raise Exception(
            f'Failed to make request after {self.config.retry_attempts} attempts'
        )

    @abstractmethod
    async def get_products(
        self, filters: Optional[dict[str, Any]] = None
    ) -> list[ProductData]:
        """Get products from the API."""
        pass

    @abstractmethod
    async def get_product(self, product_id: str) -> Optional[ProductData]:
        """Get a specific product by ID."""
        pass

    @abstractmethod
    async def create_product(self, product: ProductData) -> str:
        """Create a new product."""
        pass

    @abstractmethod
    async def update_product(self, product_id: str, product: ProductData) -> bool:
        """Update an existing product."""
        pass

    @abstractmethod
    async def delete_product(self, product_id: str) -> bool:
        """Delete a product."""
        pass


class PIMConnector(APIConnector):
    """
    Connector for Product Information Management (PIM) systems.

    Supports common PIM systems like Akeneo, Pimcore, inRiver, and others
    with standardized product data operations.
    """

    def __init__(self, config: APIConfig, sync_config: Optional[SyncConfig] = None):
        """Initialize PIM connector."""
        super().__init__(config, sync_config)
        self.product_endpoint = '/api/rest/v1/products'
        self.category_endpoint = '/api/rest/v1/categories'
        self.attribute_endpoint = '/api/rest/v1/attributes'

    async def get_products(
        self, filters: Optional[dict[str, Any]] = None
    ) -> list[ProductData]:
        """
        Get products from PIM system.

        Args:
            filters: Optional filters for product query

        Returns:
            List of ProductData objects
        """
        products = []
        page = 1
        page_size = self.sync_config.batch_size

        while True:
            params = {'page': page, 'limit': page_size}

            if filters:
                params.update(filters)

            endpoint = f'{self.product_endpoint}?{urlencode(params)}'

            try:
                response = await self._make_request('GET', endpoint)

                if '_embedded' in response and 'items' in response['_embedded']:
                    items = response['_embedded']['items']

                    for item in items:
                        product = self._convert_pim_to_product(item)
                        if product:
                            products.append(product)

                    # Check if there are more pages
                    if len(items) < page_size:
                        break

                    page += 1
                else:
                    break

            except Exception as e:
                logger.error(f'Error fetching products from PIM: {e}')
                break

        logger.info(f'Retrieved {len(products)} products from PIM')
        return products

    async def get_product(self, product_id: str) -> Optional[ProductData]:
        """
        Get a specific product from PIM system.

        Args:
            product_id: Product identifier

        Returns:
            ProductData object or None
        """
        try:
            endpoint = f'{self.product_endpoint}/{product_id}'
            response = await self._make_request('GET', endpoint)
            return self._convert_pim_to_product(response)

        except Exception as e:
            logger.error(f'Error fetching product {product_id} from PIM: {e}')
            return None

    async def create_product(self, product: ProductData) -> str:
        """
        Create a new product in PIM system.

        Args:
            product: ProductData object

        Returns:
            Created product ID
        """
        try:
            pim_data = self._convert_product_to_pim(product)
            response = await self._make_request(
                'POST', self.product_endpoint, json=pim_data
            )

            # Extract product ID from response
            if 'identifier' in response:
                return response['identifier']
            elif 'id' in response:
                return str(response['id'])
            else:
                return product.id

        except Exception as e:
            logger.error(f'Error creating product in PIM: {e}')
            raise

    async def update_product(self, product_id: str, product: ProductData) -> bool:
        """
        Update an existing product in PIM system.

        Args:
            product_id: Product identifier
            product: ProductData object

        Returns:
            True if successful
        """
        try:
            pim_data = self._convert_product_to_pim(product)
            endpoint = f'{self.product_endpoint}/{product_id}'
            await self._make_request('PATCH', endpoint, json=pim_data)
            return True

        except Exception as e:
            logger.error(f'Error updating product {product_id} in PIM: {e}')
            return False

    async def delete_product(self, product_id: str) -> bool:
        """
        Delete a product from PIM system.

        Args:
            product_id: Product identifier

        Returns:
            True if successful
        """
        try:
            endpoint = f'{self.product_endpoint}/{product_id}'
            await self._make_request('DELETE', endpoint)
            return True

        except Exception as e:
            logger.error(f'Error deleting product {product_id} from PIM: {e}')
            return False

    def _convert_pim_to_product(
        self, pim_data: dict[str, Any]
    ) -> Optional[ProductData]:
        """Convert PIM data format to ProductData."""
        try:
            product_id = pim_data.get('identifier') or pim_data.get('id')
            if not product_id:
                return None

            # Extract values from PIM structure
            values = pim_data.get('values', {})

            # Get localized values (prefer English, fallback to first available)
            def get_localized_value(
                field_name: str, default_locale: str = 'en_US'
            ) -> Optional[str]:
                if field_name not in values:
                    return None

                field_data = values[field_name]
                if isinstance(field_data, list) and field_data:
                    # Try default locale first
                    for item in field_data:
                        if item.get('locale') == default_locale:
                            return item.get('data')
                    # Fallback to first available
                    return field_data[0].get('data')
                elif isinstance(field_data, dict):
                    return field_data.get('data')

                return None

            title = get_localized_value('name') or get_localized_value('title')
            description = get_localized_value('description') or get_localized_value(
                'long_description'
            )
            price_data = get_localized_value('price')
            price = float(price_data) if price_data else None

            # Extract other fields
            category = pim_data.get('family') or get_localized_value('category')
            brand = get_localized_value('brand') or get_localized_value('manufacturer')
            sku = pim_data.get('identifier') or get_localized_value('sku')

            # Extract images
            images = []
            image_data = values.get('images', []) or values.get('pictures', [])
            for img in image_data:
                if isinstance(img, dict) and 'data' in img:
                    images.append(img['data'])

            # Extract additional attributes
            attributes = {}
            for key, value in values.items():
                if key not in [
                    'name',
                    'title',
                    'description',
                    'long_description',
                    'price',
                    'images',
                    'pictures',
                ]:
                    attr_value = get_localized_value(key)
                    if attr_value:
                        attributes[key] = attr_value

            return ProductData(
                id=str(product_id),
                title=title,
                description=description,
                price=price,
                category=category,
                brand=brand,
                sku=sku,
                attributes=attributes,
                images=images,
            )

        except Exception as e:
            logger.error(f'Error converting PIM data to ProductData: {e}')
            return None

    def _convert_product_to_pim(self, product: ProductData) -> dict[str, Any]:
        """Convert ProductData to PIM format."""
        pim_data = {'identifier': product.id, 'values': {}}

        # Add basic fields
        if product.title:
            pim_data['values']['name'] = [
                {'locale': 'en_US', 'scope': None, 'data': product.title}
            ]

        if product.description:
            pim_data['values']['description'] = [
                {'locale': 'en_US', 'scope': None, 'data': product.description}
            ]

        if product.price:
            pim_data['values']['price'] = [
                {'locale': None, 'scope': None, 'data': product.price}
            ]

        if product.brand:
            pim_data['values']['brand'] = [
                {'locale': None, 'scope': None, 'data': product.brand}
            ]

        # Add images
        if product.images:
            pim_data['values']['images'] = [
                {'locale': None, 'scope': None, 'data': img} for img in product.images
            ]

        # Add additional attributes
        if product.attributes:
            for key, value in product.attributes.items():
                pim_data['values'][key] = [
                    {'locale': None, 'scope': None, 'data': value}
                ]

        return pim_data

    async def sync_categories(self) -> list[dict[str, Any]]:
        """Sync categories from PIM system."""
        try:
            response = await self._make_request('GET', self.category_endpoint)

            categories = []
            if '_embedded' in response and 'items' in response['_embedded']:
                categories = response['_embedded']['items']

            logger.info(f'Synced {len(categories)} categories from PIM')
            return categories

        except Exception as e:
            logger.error(f'Error syncing categories from PIM: {e}')
            return []

    async def sync_attributes(self) -> list[dict[str, Any]]:
        """Sync attributes from PIM system."""
        try:
            response = await self._make_request('GET', self.attribute_endpoint)

            attributes = []
            if '_embedded' in response and 'items' in response['_embedded']:
                attributes = response['_embedded']['items']

            logger.info(f'Synced {len(attributes)} attributes from PIM')
            return attributes

        except Exception as e:
            logger.error(f'Error syncing attributes from PIM: {e}')
            return []


class ERPConnector(APIConnector):
    """
    Connector for Enterprise Resource Planning (ERP) systems.

    Supports common ERP systems like SAP, Oracle, Microsoft Dynamics,
    and others for inventory, pricing, and operational data synchronization.
    """

    def __init__(self, config: APIConfig, sync_config: Optional[SyncConfig] = None):
        """Initialize ERP connector."""
        super().__init__(config, sync_config)
        self.product_endpoint = '/api/products'
        self.inventory_endpoint = '/api/inventory'
        self.pricing_endpoint = '/api/pricing'
        self.order_endpoint = '/api/orders'

    async def get_products(
        self, filters: Optional[dict[str, Any]] = None
    ) -> list[ProductData]:
        """
        Get products from ERP system.

        Args:
            filters: Optional filters for product query

        Returns:
            List of ProductData objects
        """
        products = []

        try:
            params = filters or {}
            endpoint = f'{self.product_endpoint}?{urlencode(params)}'
            response = await self._make_request('GET', endpoint)

            # Handle different ERP response formats
            items = response.get(
                'data', response.get('items', response.get('products', []))
            )

            for item in items:
                product = self._convert_erp_to_product(item)
                if product:
                    products.append(product)

            logger.info(f'Retrieved {len(products)} products from ERP')
            return products

        except Exception as e:
            logger.error(f'Error fetching products from ERP: {e}')
            return []

    async def get_product(self, product_id: str) -> Optional[ProductData]:
        """
        Get a specific product from ERP system.

        Args:
            product_id: Product identifier

        Returns:
            ProductData object or None
        """
        try:
            endpoint = f'{self.product_endpoint}/{product_id}'
            response = await self._make_request('GET', endpoint)
            return self._convert_erp_to_product(response)

        except Exception as e:
            logger.error(f'Error fetching product {product_id} from ERP: {e}')
            return None

    async def create_product(self, product: ProductData) -> str:
        """
        Create a new product in ERP system.

        Args:
            product: ProductData object

        Returns:
            Created product ID
        """
        try:
            erp_data = self._convert_product_to_erp(product)
            response = await self._make_request(
                'POST', self.product_endpoint, json=erp_data
            )

            return response.get('id', response.get('product_id', product.id))

        except Exception as e:
            logger.error(f'Error creating product in ERP: {e}')
            raise

    async def update_product(self, product_id: str, product: ProductData) -> bool:
        """
        Update an existing product in ERP system.

        Args:
            product_id: Product identifier
            product: ProductData object

        Returns:
            True if successful
        """
        try:
            erp_data = self._convert_product_to_erp(product)
            endpoint = f'{self.product_endpoint}/{product_id}'
            await self._make_request('PUT', endpoint, json=erp_data)
            return True

        except Exception as e:
            logger.error(f'Error updating product {product_id} in ERP: {e}')
            return False

    async def delete_product(self, product_id: str) -> bool:
        """
        Delete a product from ERP system.

        Args:
            product_id: Product identifier

        Returns:
            True if successful
        """
        try:
            endpoint = f'{self.product_endpoint}/{product_id}'
            await self._make_request('DELETE', endpoint)
            return True

        except Exception as e:
            logger.error(f'Error deleting product {product_id} from ERP: {e}')
            return False

    def _convert_erp_to_product(
        self, erp_data: dict[str, Any]
    ) -> Optional[ProductData]:
        """Convert ERP data format to ProductData."""
        try:
            product_id = (
                erp_data.get('id') or erp_data.get('product_id') or erp_data.get('sku')
            )
            if not product_id:
                return None

            title = (
                erp_data.get('name')
                or erp_data.get('product_name')
                or erp_data.get('title')
            )
            description = erp_data.get('description') or erp_data.get(
                'product_description'
            )
            price = (
                erp_data.get('price')
                or erp_data.get('unit_price')
                or erp_data.get('cost')
            )
            category = erp_data.get('category') or erp_data.get('product_category')
            brand = erp_data.get('brand') or erp_data.get('manufacturer')
            sku = erp_data.get('sku') or erp_data.get('product_code')

            # Convert price to float if needed
            if price and not isinstance(price, (int, float)):
                try:
                    price = float(str(price).replace(',', '').replace('$', ''))
                except (ValueError, TypeError):
                    price = None

            # Extract additional attributes
            attributes = {}
            excluded_fields = {
                'id',
                'product_id',
                'name',
                'product_name',
                'title',
                'description',
                'product_description',
                'price',
                'unit_price',
                'cost',
                'category',
                'product_category',
                'brand',
                'manufacturer',
                'sku',
                'product_code',
            }

            for key, value in erp_data.items():
                if key not in excluded_fields and value is not None:
                    attributes[key] = str(value)

            return ProductData(
                id=str(product_id),
                title=title,
                description=description,
                price=price,
                category=category,
                brand=brand,
                sku=sku,
                attributes=attributes,
                images=[],  # ERP systems typically don't store images
            )

        except Exception as e:
            logger.error(f'Error converting ERP data to ProductData: {e}')
            return None

    def _convert_product_to_erp(self, product: ProductData) -> dict[str, Any]:
        """Convert ProductData to ERP format."""
        erp_data = {
            'id': product.id,
            'name': product.title,
            'description': product.description,
            'price': product.price,
            'category': product.category,
            'brand': product.brand,
            'sku': product.sku or product.id,
        }

        # Add additional attributes
        if product.attributes:
            erp_data.update(product.attributes)

        # Remove None values
        return {k: v for k, v in erp_data.items() if v is not None}

    async def get_inventory_levels(self, product_ids: list[str]) -> dict[str, int]:
        """
        Get inventory levels for products.

        Args:
            product_ids: List of product IDs

        Returns:
            Dictionary mapping product IDs to inventory levels
        """
        try:
            params = {'product_ids': ','.join(product_ids)}
            endpoint = f'{self.inventory_endpoint}?{urlencode(params)}'
            response = await self._make_request('GET', endpoint)

            inventory = {}
            items = response.get('data', response.get('items', []))

            for item in items:
                product_id = item.get('product_id') or item.get('id')
                quantity = item.get('quantity') or item.get('stock_level') or 0
                if product_id:
                    inventory[str(product_id)] = int(quantity)

            return inventory

        except Exception as e:
            logger.error(f'Error fetching inventory levels from ERP: {e}')
            return {}

    async def update_inventory(self, product_id: str, quantity: int) -> bool:
        """
        Update inventory level for a product.

        Args:
            product_id: Product identifier
            quantity: New inventory quantity

        Returns:
            True if successful
        """
        try:
            data = {'product_id': product_id, 'quantity': quantity}
            await self._make_request(
                'PUT', f'{self.inventory_endpoint}/{product_id}', json=data
            )
            return True

        except Exception as e:
            logger.error(
                f'Error updating inventory for product {product_id} in ERP: {e}'
            )
            return False

    async def get_pricing_data(
        self, product_ids: list[str]
    ) -> dict[str, dict[str, Any]]:
        """
        Get pricing data for products.

        Args:
            product_ids: List of product IDs

        Returns:
            Dictionary mapping product IDs to pricing information
        """
        try:
            params = {'product_ids': ','.join(product_ids)}
            endpoint = f'{self.pricing_endpoint}?{urlencode(params)}'
            response = await self._make_request('GET', endpoint)

            pricing = {}
            items = response.get('data', response.get('items', []))

            for item in items:
                product_id = item.get('product_id') or item.get('id')
                if product_id:
                    pricing[str(product_id)] = {
                        'base_price': item.get('base_price'),
                        'sale_price': item.get('sale_price'),
                        'cost': item.get('cost'),
                        'margin': item.get('margin'),
                        'currency': item.get('currency', 'USD'),
                    }

            return pricing

        except Exception as e:
            logger.error(f'Error fetching pricing data from ERP: {e}')
            return {}
