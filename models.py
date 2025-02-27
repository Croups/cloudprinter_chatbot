from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field

class UserIntent(str, Enum):
    """Enum for user intents."""
    GET_PRODUCT_PRICE = "get_product_price"
    GET_PRODUCT_LIST = "get_product_list"
    GET_PRODUCT_INFO = "get_product_info"
    OTHER = "OTHER"

# Models for Product API
class Product(BaseModel):
    """Model for a product from /products API."""
    name: str
    note: Optional[str] = None
    reference: str  # Unique product identifier
    category: Optional[str] = None
    from_price: Optional[str] = None
    currency: Optional[str] = None

class ProductOption(BaseModel):
    """Model for a product option from /products/info API."""
    reference: str
    note: str
    type: str
    default: int  # 0 or 1

class ProductSpec(BaseModel):
    """Model for a product specification from /products/info API."""
    note: str
    value: str

class ProductInfo(BaseModel):
    """Model for detailed product information from /products/info API."""
    name: str
    note: Optional[str] = None
    reference: str
    prices: Optional[List[Dict]] = None  # Deprecated field
    options: List[ProductOption] = []
    specs: List[ProductSpec] = []

# Models for Quote API
class ItemOption(BaseModel):
    """Model for an option in a quote item."""
    type: str
    count: str

class QuoteItem(BaseModel):
    """Model for an item in a quote request."""
    reference: str = Field(..., description="Client item reference")
    product: str = Field(..., description="The product ID")
    count: str = Field(..., description="The product quantity")
    options: List[ItemOption] = []

class QuoteRequest(BaseModel):
    """Model for a quote request to /orders/quote API."""
    apikey: str
    currency: Optional[str] = None  # Default is EUR
    country: str = Field(..., description="The country the order will ship to (ISO 3166-1 alpha-2)")
    state: Optional[str] = None  # Required for US
    items: List[QuoteItem]

class ShipmentItem(BaseModel):
    """Model for an item in a shipment."""
    reference: str

class ShipmentQuote(BaseModel):
    """Model for a quote in a shipment."""
    quote: str
    service: str
    shipping_level: str
    shipping_option: str
    price: str
    vat: str
    currency: str

class Shipment(BaseModel):
    """Model for a shipment in a quote response."""
    total_weight: str
    items: List[ShipmentItem]
    quotes: List[ShipmentQuote]

class QuoteResponse(BaseModel):
    """Model for a quote response from /orders/quote API."""
    price: str
    vat: str
    currency: str
    expire_date: str
    subtotals: Dict[str, str]
    shipments: List[Shipment]
    invoice_currency: str
    invoice_exchange_rate: str

# Additional models for Orders API (not needed for initial quote functionality)
class File(BaseModel):
    """Model for a file in an order."""
    type: str
    url: str
    md5sum: str

class Address(BaseModel):
    """Model for an address in an order."""
    type: str
    company: Optional[str] = None
    firstname: str
    lastname: str
    street1: str
    street2: Optional[str] = None
    zip: str
    city: str
    state: Optional[str] = None
    country: str
    email: Optional[str] = None
    phone: Optional[str] = None
    customer_identification: Optional[str] = None

class OrderItem(BaseModel):
    """Model for an item in an order."""
    reference: str
    product: str
    count: str
    shipping_level: Optional[str] = None
    quote: Optional[str] = None
    title: Optional[str] = None
    files: List[File] = []
    options: List[ItemOption] = []

class Order(BaseModel):
    """Model for an order to /orders/add API."""
    apikey: str
    reference: str
    email: str
    price: Optional[str] = None
    currency: Optional[str] = None
    hc: Optional[str] = None
    meta: Optional[Dict] = None
    addresses: List[Address] = []
    files: List[File] = []
    items: List[OrderItem] = []

# Models for Shipping API
class ShippingLevel(BaseModel):
    """Model for a shipping level from /shipping/levels API."""
    shipping_level_reference: str
    shipping_level: str
    name: str
    note: str

class ShippingCountry(BaseModel):
    """Model for a shipping country from /shipping/countries API."""
    country_reference: str
    note: str
    require_state: int  # 1 = Country requires state, 0 = Country does not require state

class ShippingState(BaseModel):
    """Model for a shipping state from /shipping/states API."""
    state_reference: str
    name: str
    note: str 