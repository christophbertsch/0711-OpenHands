"""
CSV data processor for product information and content enrichment.

This module handles CSV data ingestion, parsing, and transformation
for various product data formats including standard e-commerce exports,
PIM system data, and custom CSV schemas.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union

import pandas as pd

from openhands.core.logger import openhands_logger as logger

from .xml_processor import ProductData


@dataclass
class CSVConfig:
    """Configuration for CSV processing."""

    delimiter: str = ','
    quotechar: str = '"'
    encoding: str = 'utf-8'
    has_header: bool = True
    skip_rows: int = 0
    column_mapping: dict[str, str] = None
    data_types: dict[str, str] = None
    required_columns: list[str] = None

    def __post_init__(self):
        if self.column_mapping is None:
            self.column_mapping = {}
        if self.data_types is None:
            self.data_types = {}
        if self.required_columns is None:
            self.required_columns = ['id']


class CSVProcessor:
    """
    CSV processor for product data ingestion and transformation.

    Supports various CSV formats including:
    - Standard e-commerce product exports
    - PIM system data exports
    - Custom CSV schemas with flexible column mapping
    - Multi-language product data
    - Bulk product updates and imports
    """

    def __init__(self, config: Optional[CSVConfig] = None):
        """
        Initialize CSV processor with configuration.

        Args:
            config: CSV processing configuration
        """
        self.config = config or CSVConfig()
        self.processed_count = 0
        self.error_count = 0
        self.validation_errors = []

    def process_csv_file(self, file_path: Union[str, Path]) -> list[ProductData]:
        """
        Process CSV file and extract product data.

        Args:
            file_path: Path to CSV file

        Returns:
            List of ProductData objects
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f'CSV file not found: {file_path}')

        logger.info(f'Processing CSV file: {file_path}')

        try:
            # Read CSV file with pandas for better handling
            df = pd.read_csv(
                file_path,
                delimiter=self.config.delimiter,
                quotechar=self.config.quotechar,
                encoding=self.config.encoding,
                skiprows=self.config.skip_rows,
                dtype=str,  # Read all as strings initially
            )

            products = self._process_dataframe(df)

            logger.info(
                f'Successfully processed {len(products)} products from {file_path}'
            )
            return products

        except Exception as e:
            logger.error(f'Error processing CSV file {file_path}: {e}')
            raise

    def process_csv_string(self, csv_content: str) -> list[ProductData]:
        """
        Process CSV content from string.

        Args:
            csv_content: CSV content as string

        Returns:
            List of ProductData objects
        """
        try:
            from io import StringIO

            df = pd.read_csv(
                StringIO(csv_content),
                delimiter=self.config.delimiter,
                quotechar=self.config.quotechar,
                skiprows=self.config.skip_rows,
                dtype=str,
            )

            products = self._process_dataframe(df)

            logger.info(
                f'Successfully processed {len(products)} products from CSV string'
            )
            return products

        except Exception as e:
            logger.error(f'Error processing CSV string: {e}')
            raise

    def _process_dataframe(self, df: pd.DataFrame) -> list[ProductData]:
        """
        Process pandas DataFrame and extract product data.

        Args:
            df: Pandas DataFrame with product data

        Returns:
            List of ProductData objects
        """
        products = []

        # Apply column mapping if provided
        if self.config.column_mapping:
            df = df.rename(columns=self.config.column_mapping)

        # Validate required columns
        missing_columns = [
            col for col in self.config.required_columns if col not in df.columns
        ]
        if missing_columns:
            raise ValueError(f'Missing required columns: {missing_columns}')

        # Process each row
        for index, row in df.iterrows():
            try:
                product = self._extract_product_from_row(row, index)
                if product:
                    products.append(product)
                    self.processed_count += 1
            except Exception as e:
                logger.warning(f'Error processing row {index}: {e}')
                self.error_count += 1
                self.validation_errors.append(f'Row {index}: {e}')
                continue

        return products

    def _extract_product_from_row(
        self, row: pd.Series, row_index: int
    ) -> Optional[ProductData]:
        """
        Extract product data from DataFrame row.

        Args:
            row: Pandas Series representing a row
            row_index: Row index for error reporting

        Returns:
            ProductData object or None if extraction fails
        """
        try:
            # Extract basic product information
            product_id = self._get_field_value(row, 'id')

            if not product_id or pd.isna(product_id):
                logger.warning(f'Row {row_index}: Product missing ID, skipping')
                return None

            title = self._get_field_value(row, 'title')
            description = self._get_field_value(row, 'description')
            price_str = self._get_field_value(row, 'price')
            category = self._get_field_value(row, 'category')
            brand = self._get_field_value(row, 'brand')
            sku = self._get_field_value(row, 'sku')

            # Parse price
            price = self._parse_price(price_str)

            # Extract images
            images = self._extract_images_from_row(row)

            # Extract additional attributes
            attributes = self._extract_attributes_from_row(row)

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
            logger.error(f'Error extracting product data from row {row_index}: {e}')
            return None

    def _get_field_value(self, row: pd.Series, field_name: str) -> Optional[str]:
        """
        Get field value from row with fallback options.

        Args:
            row: Pandas Series representing a row
            field_name: Field name to extract

        Returns:
            Field value or None
        """
        # Try exact field name
        if field_name in row.index and not pd.isna(row[field_name]):
            return str(row[field_name]).strip()

        # Try common variations
        variations = self._get_field_variations(field_name)
        for variation in variations:
            if variation in row.index and not pd.isna(row[variation]):
                return str(row[variation]).strip()

        return None

    def _get_field_variations(self, field_name: str) -> list[str]:
        """
        Get common variations of field names.

        Args:
            field_name: Base field name

        Returns:
            List of field name variations
        """
        variations = []

        # Common field name mappings
        field_mappings = {
            'id': ['product_id', 'item_id', 'sku', 'product_code', 'ID', 'Id'],
            'title': [
                'name',
                'product_name',
                'item_name',
                'product_title',
                'Title',
                'Name',
            ],
            'description': [
                'desc',
                'product_description',
                'long_description',
                'Description',
                'Desc',
            ],
            'price': ['cost', 'amount', 'price_amount', 'unit_price', 'Price', 'Cost'],
            'category': ['cat', 'product_category', 'category_name', 'Category', 'Cat'],
            'brand': ['manufacturer', 'brand_name', 'Brand', 'Manufacturer'],
            'sku': ['product_code', 'item_code', 'SKU', 'Sku'],
        }

        if field_name in field_mappings:
            variations.extend(field_mappings[field_name])

        # Add case variations
        variations.extend(
            [
                field_name.upper(),
                field_name.lower(),
                field_name.capitalize(),
                field_name.replace('_', ' '),
                field_name.replace(' ', '_'),
            ]
        )

        return list(set(variations))

    def _parse_price(self, price_str: Optional[str]) -> Optional[float]:
        """
        Parse price string to float.

        Args:
            price_str: Price as string

        Returns:
            Price as float or None
        """
        if not price_str or pd.isna(price_str):
            return None

        try:
            # Remove currency symbols and formatting
            price_clean = re.sub(r'[^\d.,]', '', str(price_str))
            price_clean = price_clean.replace(',', '')

            if price_clean:
                return float(price_clean)
        except (ValueError, TypeError):
            logger.warning(f'Could not parse price: {price_str}')

        return None

    def _extract_images_from_row(self, row: pd.Series) -> list[str]:
        """
        Extract image URLs from row.

        Args:
            row: Pandas Series representing a row

        Returns:
            List of image URLs
        """
        images = []

        # Common image field names
        image_fields = [
            'image',
            'images',
            'image_url',
            'image_urls',
            'main_image',
            'product_image',
            'photo',
            'photos',
            'picture',
            'pictures',
        ]

        for field in image_fields:
            value = self._get_field_value(row, field)
            if value:
                # Handle multiple images separated by delimiters
                if ',' in value:
                    images.extend([img.strip() for img in value.split(',')])
                elif ';' in value:
                    images.extend([img.strip() for img in value.split(';')])
                elif '|' in value:
                    images.extend([img.strip() for img in value.split('|')])
                else:
                    images.append(value.strip())

        # Filter out empty strings and validate URLs
        valid_images = []
        for img in images:
            if img and (img.startswith('http') or img.startswith('/')):
                valid_images.append(img)

        return list(set(valid_images))  # Remove duplicates

    def _extract_attributes_from_row(self, row: pd.Series) -> dict[str, Any]:
        """
        Extract additional attributes from row.

        Args:
            row: Pandas Series representing a row

        Returns:
            Dictionary of attributes
        """
        attributes = {}

        # Standard fields to exclude from attributes
        standard_fields = {
            'id',
            'title',
            'description',
            'price',
            'category',
            'brand',
            'sku',
            'image',
            'images',
            'image_url',
            'image_urls',
            'main_image',
        }

        # Add field variations to exclusion list
        excluded_fields = set()
        for field in standard_fields:
            excluded_fields.update(self._get_field_variations(field))

        # Extract all other fields as attributes
        for column in row.index:
            if column.lower() not in [f.lower() for f in excluded_fields]:
                value = row[column]
                if not pd.isna(value) and str(value).strip():
                    attributes[column] = str(value).strip()

        return attributes

    def validate_csv_file(self, file_path: Union[str, Path]) -> dict[str, Any]:
        """
        Validate CSV file structure and content.

        Args:
            file_path: Path to CSV file

        Returns:
            Validation results
        """
        file_path = Path(file_path)

        try:
            # Read first few rows for validation
            df_sample = pd.read_csv(
                file_path,
                delimiter=self.config.delimiter,
                quotechar=self.config.quotechar,
                encoding=self.config.encoding,
                skiprows=self.config.skip_rows,
                nrows=10,
                dtype=str,
            )

            # Read full file for statistics
            df_full = pd.read_csv(
                file_path,
                delimiter=self.config.delimiter,
                quotechar=self.config.quotechar,
                encoding=self.config.encoding,
                skiprows=self.config.skip_rows,
                dtype=str,
            )

            validation_results = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'row_count': len(df_full),
                'column_count': len(df_full.columns),
                'columns': list(df_full.columns),
                'sample_data': df_sample.head().to_dict('records'),
                'statistics': {},
            }

            # Check required columns
            missing_columns = [
                col
                for col in self.config.required_columns
                if col not in df_full.columns
            ]
            if missing_columns:
                validation_results['errors'].append(
                    f'Missing required columns: {missing_columns}'
                )
                validation_results['valid'] = False

            # Check for empty required fields
            for col in self.config.required_columns:
                if col in df_full.columns:
                    empty_count = df_full[col].isna().sum()
                    if empty_count > 0:
                        validation_results['warnings'].append(
                            f"Column '{col}' has {empty_count} empty values"
                        )

            # Generate statistics
            validation_results['statistics'] = {
                'total_rows': len(df_full),
                'columns_with_data': sum(
                    1 for col in df_full.columns if not df_full[col].isna().all()
                ),
                'completely_empty_rows': df_full.isna().all(axis=1).sum(),
                'duplicate_rows': df_full.duplicated().sum(),
            }

            return validation_results

        except Exception as e:
            return {
                'valid': False,
                'errors': [f'Validation error: {e}'],
                'warnings': [],
                'row_count': 0,
                'column_count': 0,
                'columns': [],
                'sample_data': [],
                'statistics': {},
            }

    def export_to_csv(
        self, products: list[ProductData], output_path: Union[str, Path]
    ) -> None:
        """
        Export processed products to CSV file.

        Args:
            products: List of ProductData objects
            output_path: Output file path
        """
        output_path = Path(output_path)

        if not products:
            logger.warning('No products to export')
            return

        # Convert products to list of dictionaries
        rows = []
        for product in products:
            row = {
                'id': product.id,
                'title': product.title,
                'description': product.description,
                'price': product.price,
                'category': product.category,
                'brand': product.brand,
                'sku': product.sku,
                'images': '|'.join(product.images) if product.images else '',
            }

            # Add attributes as separate columns
            if product.attributes:
                row.update(product.attributes)

            rows.append(row)

        # Create DataFrame and export
        df = pd.DataFrame(rows)
        df.to_csv(
            output_path,
            index=False,
            encoding=self.config.encoding,
            sep=self.config.delimiter,
            quotechar=self.config.quotechar,
        )

        logger.info(f'Exported {len(products)} products to {output_path}')

    def merge_csv_files(
        self, file_paths: list[Union[str, Path]], output_path: Union[str, Path]
    ) -> None:
        """
        Merge multiple CSV files into one.

        Args:
            file_paths: List of CSV file paths to merge
            output_path: Output file path
        """
        all_products = []

        for file_path in file_paths:
            try:
                products = self.process_csv_file(file_path)
                all_products.extend(products)
                logger.info(f'Added {len(products)} products from {file_path}')
            except Exception as e:
                logger.error(f'Error processing {file_path}: {e}')
                continue

        if all_products:
            self.export_to_csv(all_products, output_path)
            logger.info(
                f'Merged {len(all_products)} products from {len(file_paths)} files'
            )
        else:
            logger.warning('No products found to merge')

    def get_processing_stats(self) -> dict[str, Any]:
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
            'validation_errors': self.validation_errors,
        }

    def clean_data(self, products: list[ProductData]) -> list[ProductData]:
        """
        Clean and standardize product data.

        Args:
            products: List of ProductData objects

        Returns:
            List of cleaned ProductData objects
        """
        cleaned_products = []

        for product in products:
            # Clean title
            if product.title:
                product.title = self._clean_text(product.title)

            # Clean description
            if product.description:
                product.description = self._clean_text(product.description)

            # Standardize category
            if product.category:
                product.category = self._standardize_category(product.category)

            # Clean attributes
            if product.attributes:
                cleaned_attributes = {}
                for key, value in product.attributes.items():
                    if value and str(value).strip():
                        cleaned_attributes[key] = self._clean_text(str(value))
                product.attributes = cleaned_attributes

            cleaned_products.append(product)

        return cleaned_products

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return text

        # Remove extra whitespace
        text = ' '.join(text.split())

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)

        # Fix common encoding issues
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')

        return text.strip()

    def _standardize_category(self, category: str) -> str:
        """Standardize category format."""
        if not category:
            return category

        # Convert to title case
        category = category.title()

        # Remove extra separators
        category = re.sub(r'[>|/]{2,}', '>', category)
        category = re.sub(r'^[>|/]+|[>|/]+$', '', category)

        return category.strip()
