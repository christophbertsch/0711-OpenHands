"""
XML data processor for product information and content enrichment.

This module handles XML data ingestion, parsing, and transformation
for various product data formats including standard e-commerce feeds,
PIM exports, and custom XML schemas.
"""

import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union

from openhands.core.logger import openhands_logger as logger


@dataclass
class ProductData:
    """Structured product data representation."""

    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    sku: Optional[str] = None
    attributes: dict[str, Any] = None
    images: list[str] = None

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}
        if self.images is None:
            self.images = []


class XMLProcessor:
    """
    XML processor for product data ingestion and transformation.

    Supports various XML formats including:
    - Standard e-commerce product feeds
    - PIM system exports
    - Custom XML schemas
    - Multi-language product data
    """

    def __init__(self, schema_config: Optional[dict[str, Any]] = None):
        """
        Initialize XML processor with optional schema configuration.

        Args:
            schema_config: Configuration for XML schema mapping
        """
        self.schema_config = schema_config or self._get_default_schema()
        self.processed_count = 0
        self.error_count = 0

    def _get_default_schema(self) -> dict[str, Any]:
        """Get default XML schema configuration."""
        return {
            'product_element': 'product',
            'id_field': 'id',
            'title_field': 'title',
            'description_field': 'description',
            'price_field': 'price',
            'category_field': 'category',
            'brand_field': 'brand',
            'sku_field': 'sku',
            'image_field': 'image',
            'attributes_element': 'attributes',
            'namespaces': {},
        }

    def process_xml_file(self, file_path: Union[str, Path]) -> list[ProductData]:
        """
        Process XML file and extract product data.

        Args:
            file_path: Path to XML file

        Returns:
            List of ProductData objects
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f'XML file not found: {file_path}')

        logger.info(f'Processing XML file: {file_path}')

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            products = self._extract_products_from_xml(root)

            logger.info(
                f'Successfully processed {len(products)} products from {file_path}'
            )
            return products

        except ET.ParseError as e:
            logger.error(f'XML parsing error in {file_path}: {e}')
            raise
        except Exception as e:
            logger.error(f'Error processing XML file {file_path}: {e}')
            raise

    def process_xml_string(self, xml_content: str) -> list[ProductData]:
        """
        Process XML content from string.

        Args:
            xml_content: XML content as string

        Returns:
            List of ProductData objects
        """
        try:
            root = ET.fromstring(xml_content)
            products = self._extract_products_from_xml(root)

            logger.info(
                f'Successfully processed {len(products)} products from XML string'
            )
            return products

        except ET.ParseError as e:
            logger.error(f'XML parsing error: {e}')
            raise
        except Exception as e:
            logger.error(f'Error processing XML string: {e}')
            raise

    def _extract_products_from_xml(self, root: ET.Element) -> list[ProductData]:
        """
        Extract product data from XML root element.

        Args:
            root: XML root element

        Returns:
            List of ProductData objects
        """
        products = []
        product_element = self.schema_config['product_element']
        namespaces = self.schema_config.get('namespaces', {})

        # Find all product elements
        if namespaces:
            product_elements = root.findall(f'.//{product_element}', namespaces)
        else:
            product_elements = root.findall(f'.//{product_element}')

        for element in product_elements:
            try:
                product = self._extract_product_data(element, namespaces)
                if product:
                    products.append(product)
                    self.processed_count += 1
            except Exception as e:
                logger.warning(f'Error processing product element: {e}')
                self.error_count += 1
                continue

        return products

    def _extract_product_data(
        self, element: ET.Element, namespaces: dict[str, str]
    ) -> Optional[ProductData]:
        """
        Extract product data from XML element.

        Args:
            element: Product XML element
            namespaces: XML namespaces

        Returns:
            ProductData object or None if extraction fails
        """
        try:
            # Extract basic product information
            product_id = self._get_element_text(
                element, self.schema_config['id_field'], namespaces
            )

            if not product_id:
                logger.warning('Product missing ID, skipping')
                return None

            title = self._get_element_text(
                element, self.schema_config['title_field'], namespaces
            )
            description = self._get_element_text(
                element, self.schema_config['description_field'], namespaces
            )
            price_str = self._get_element_text(
                element, self.schema_config['price_field'], namespaces
            )
            category = self._get_element_text(
                element, self.schema_config['category_field'], namespaces
            )
            brand = self._get_element_text(
                element, self.schema_config['brand_field'], namespaces
            )
            sku = self._get_element_text(
                element, self.schema_config['sku_field'], namespaces
            )

            # Parse price
            price = None
            if price_str:
                try:
                    price = float(price_str.replace(',', '').replace('$', '').strip())
                except (ValueError, AttributeError):
                    logger.warning(f'Could not parse price: {price_str}')

            # Extract images
            images = self._extract_images(element, namespaces)

            # Extract additional attributes
            attributes = self._extract_attributes(element, namespaces)

            return ProductData(
                id=product_id,
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
            logger.error(f'Error extracting product data: {e}')
            return None

    def _get_element_text(
        self, parent: ET.Element, field_name: str, namespaces: dict[str, str]
    ) -> Optional[str]:
        """
        Get text content from XML element.

        Args:
            parent: Parent XML element
            field_name: Field name to search for
            namespaces: XML namespaces

        Returns:
            Text content or None
        """
        if not field_name:
            return None

        # Try as direct child element
        if namespaces:
            element = parent.find(field_name, namespaces)
        else:
            element = parent.find(field_name)

        if element is not None:
            return element.text

        # Try as attribute
        return parent.get(field_name)

    def _extract_images(
        self, element: ET.Element, namespaces: dict[str, str]
    ) -> list[str]:
        """
        Extract image URLs from product element.

        Args:
            element: Product XML element
            namespaces: XML namespaces

        Returns:
            List of image URLs
        """
        images = []
        image_field = self.schema_config['image_field']

        if not image_field:
            return images

        # Find all image elements
        if namespaces:
            image_elements = element.findall(f'.//{image_field}', namespaces)
        else:
            image_elements = element.findall(f'.//{image_field}')

        for img_element in image_elements:
            if img_element.text:
                images.append(img_element.text.strip())
            # Also check for URL in attributes
            for attr in ['url', 'src', 'href']:
                if img_element.get(attr):
                    images.append(img_element.get(attr).strip())

        return list(set(images))  # Remove duplicates

    def _extract_attributes(
        self, element: ET.Element, namespaces: dict[str, str]
    ) -> dict[str, Any]:
        """
        Extract additional attributes from product element.

        Args:
            element: Product XML element
            namespaces: XML namespaces

        Returns:
            Dictionary of attributes
        """
        attributes = {}
        attributes_element = self.schema_config.get('attributes_element')

        # Extract all element attributes
        for key, value in element.attrib.items():
            attributes[key] = value

        # Extract from attributes element if specified
        if attributes_element:
            if namespaces:
                attr_element = element.find(attributes_element, namespaces)
            else:
                attr_element = element.find(attributes_element)

            if attr_element is not None:
                for child in attr_element:
                    tag_name = (
                        child.tag.split('}')[-1] if '}' in child.tag else child.tag
                    )
                    attributes[tag_name] = child.text

        # Extract all child elements not already processed
        processed_fields = {
            self.schema_config['id_field'],
            self.schema_config['title_field'],
            self.schema_config['description_field'],
            self.schema_config['price_field'],
            self.schema_config['category_field'],
            self.schema_config['brand_field'],
            self.schema_config['sku_field'],
            self.schema_config['image_field'],
            attributes_element,
        }

        for child in element:
            tag_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            if tag_name not in processed_fields and child.text:
                attributes[tag_name] = child.text

        return attributes

    def validate_xml_schema(self, file_path: Union[str, Path]) -> dict[str, Any]:
        """
        Validate XML file against expected schema.

        Args:
            file_path: Path to XML file

        Returns:
            Validation results
        """
        file_path = Path(file_path)

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            validation_results = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'product_count': 0,
                'schema_info': {},
            }

            # Check for product elements
            product_element = self.schema_config['product_element']
            namespaces = self.schema_config.get('namespaces', {})

            if namespaces:
                products = root.findall(f'.//{product_element}', namespaces)
            else:
                products = root.findall(f'.//{product_element}')

            validation_results['product_count'] = len(products)

            if len(products) == 0:
                validation_results['errors'].append(
                    f'No {product_element} elements found'
                )
                validation_results['valid'] = False

            # Sample first few products for schema validation
            sample_size = min(5, len(products))
            for i, product in enumerate(products[:sample_size]):
                product_id = self._get_element_text(
                    product, self.schema_config['id_field'], namespaces
                )
                if not product_id:
                    validation_results['warnings'].append(
                        f'Product {i + 1} missing ID field'
                    )

            validation_results['schema_info'] = {
                'root_element': root.tag,
                'namespaces': dict(root.attrib) if root.attrib else {},
                'sample_product_fields': self._get_sample_fields(
                    products[0] if products else None, namespaces
                ),
            }

            return validation_results

        except ET.ParseError as e:
            return {
                'valid': False,
                'errors': [f'XML parsing error: {e}'],
                'warnings': [],
                'product_count': 0,
                'schema_info': {},
            }
        except Exception as e:
            return {
                'valid': False,
                'errors': [f'Validation error: {e}'],
                'warnings': [],
                'product_count': 0,
                'schema_info': {},
            }

    def _get_sample_fields(
        self, element: Optional[ET.Element], namespaces: dict[str, str]
    ) -> list[str]:
        """Get sample fields from product element."""
        if element is None:
            return []

        fields = []
        for child in element:
            tag_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            fields.append(tag_name)

        return fields

    def export_to_json(
        self, products: list[ProductData], output_path: Union[str, Path]
    ) -> None:
        """
        Export processed products to JSON file.

        Args:
            products: List of ProductData objects
            output_path: Output file path
        """
        output_path = Path(output_path)

        # Convert products to dictionaries
        products_dict = []
        for product in products:
            product_dict = {
                'id': product.id,
                'title': product.title,
                'description': product.description,
                'price': product.price,
                'category': product.category,
                'brand': product.brand,
                'sku': product.sku,
                'attributes': product.attributes,
                'images': product.images,
            }
            products_dict.append(product_dict)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(products_dict, f, indent=2, ensure_ascii=False)

        logger.info(f'Exported {len(products)} products to {output_path}')

    def get_processing_stats(self) -> dict[str, int]:
        """Get processing statistics."""
        return {
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'success_rate': (
                self.processed_count / (self.processed_count + self.error_count)
            )
            * 100
            if (self.processed_count + self.error_count) > 0
            else 0,
        }
