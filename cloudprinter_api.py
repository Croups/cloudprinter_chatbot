import requests
import json
import logging
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

from models import (
    Product, ProductInfo, ProductOption, ProductSpec, 
    QuoteRequest, QuoteResponse, UserIntent,
    ShippingLevel, ShippingCountry, ShippingState
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

class CloudprinterAPIClient:
    """
    Client for interacting with the Cloudprinter API.
    """
    
    BASE_URL = "https://api.cloudprinter.com/cloudcore/1.0"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the API client with the API key.
        
        Args:
            api_key: The API key for authenticating with the Cloudprinter API.
                    If None, the API key is loaded from the CLOUDPRINTER_API_KEY
                    environment variable.
        """
        self.api_key = api_key or os.getenv("CLOUDPRINTER_API_KEY")
        if not self.api_key:
            raise ValueError("API key not provided and not found in environment variables.")
        
        self.headers = {'Content-Type': 'application/json'}
    
    def _make_request(self, endpoint: str, payload: Dict = None) -> Dict:
        """
        Makes a POST request to the Cloudprinter API.
        
        Args:
            endpoint: The API endpoint to call.
            payload: The payload to send with the request. If None, a payload with only
                    the API key is sent.
        
        Returns:
            The JSON response from the API.
        
        Raises:
            requests.exceptions.RequestException: If the request fails.
            json.JSONDecodeError: If the response is not valid JSON.
            ValueError: If the API returns an error status code.
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Add API key to payload
        if payload is None:
            payload = {}
        payload["apikey"] = self.api_key
        
        # Convert payload to JSON
        payload_json = json.dumps(payload)
        
        # Log request details
        logger.info(f"Sending request to {url}")
        logger.debug(f"Request payload: {payload_json}")
        
        # Make the request
        response = requests.post(url, headers=self.headers, data=payload_json)
        
        # Log response details
        logger.info(f"Received response from {url} with status code: {response.status_code}")
        
        # Check for successful response
        if response.status_code not in [200, 201]:
            logger.error(f"API returned error status code: {response.status_code}")
            logger.error(f"Response text: {response.text}")
            raise ValueError(f"API request failed with status code {response.status_code}: {response.text}")
        
        # Parse response JSON
        try:
            response_json = response.json()
            logger.debug(f"Response JSON: {json.dumps(response_json, indent=2)}")
            return response_json
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response: {e}")
            logger.error(f"Response text: {response.text}")
            raise
    
    def get_products(self) -> List[Product]:
        """
        Gets a list of all products available to the account.
        
        Returns:
            A list of Product objects.
        """
        response = self._make_request("products")
        
        # Convert response to Product objects
        products = [Product(**product) for product in response]
        logger.info(f"Retrieved {len(products)} products")
        return products
    
    def get_product_info(self, reference: str) -> ProductInfo:
        """
        Gets detailed information about a specific product.
        
        Args:
            reference: The reference of the product.
        
        Returns:
            A ProductInfo object with detailed product information.
        """
        payload = {"reference": reference}
        response = self._make_request("products/info", payload)
        
        # Process options and specs to ensure they match our model
        if "options" in response:
            for i, option in enumerate(response["options"]):
                if not isinstance(option.get("default"), int):
                    # Convert to int if necessary
                    try:
                        response["options"][i]["default"] = int(option.get("default", 0))
                    except (ValueError, TypeError):
                        response["options"][i]["default"] = 0
        
        # Convert response to ProductInfo object
        product_info = ProductInfo(**response)
        logger.info(f"Retrieved product info for {reference}")
        return product_info
    
    def get_quote(self, quote_request: QuoteRequest) -> QuoteResponse:
        """
        Gets a price quote for an order.
        
        Args:
            quote_request: A QuoteRequest object containing the details of the order.
        
        Returns:
            A QuoteResponse object with the price quote.
        """
        # Convert QuoteRequest to dict and remove apikey (will be added by _make_request)
        payload = quote_request.model_dump()
        if "apikey" in payload:
            del payload["apikey"]
        
        response = self._make_request("orders/quote", payload)
        
        # Convert response to QuoteResponse object
        quote_response = QuoteResponse(**response)
        logger.info(f"Retrieved quote with price {quote_response.price} {quote_response.currency}")
        return quote_response

    def get_shipping_levels(self) -> List[ShippingLevel]:
        """
        Gets a list of available shipping levels for the account.
        
        Returns:
            A list of ShippingLevel objects.
        """
        response = self._make_request("shipping/levels")
        
        # Convert response to ShippingLevel objects
        shipping_levels = [ShippingLevel(**level) for level in response]
        logger.info(f"Retrieved {len(shipping_levels)} shipping levels")
        return shipping_levels

    def get_shipping_countries(self) -> List[ShippingCountry]:
        """
        Gets a list of available shipping countries for the account.
        
        Returns:
            A list of ShippingCountry objects.
        """
        response = self._make_request("shipping/countries")
        
        # Convert response to ShippingCountry objects
        shipping_countries = [ShippingCountry(**country) for country in response]
        logger.info(f"Retrieved {len(shipping_countries)} shipping countries")
        return shipping_countries

    def get_shipping_states(self, country_reference: str) -> List[ShippingState]:
        """
        Gets a list of available shipping states/regions for a specific country.
        
        Args:
            country_reference: The country reference code (ISO 3166-1 alpha-2).
        
        Returns:
            A list of ShippingState objects.
        """
        payload = {"country_reference": country_reference}
        response = self._make_request("shipping/states", payload)
        
        # Convert response to ShippingState objects
        shipping_states = [ShippingState(**state) for state in response]
        logger.info(f"Retrieved {len(shipping_states)} shipping states for {country_reference}")
        return shipping_states

# Example usage
if __name__ == "__main__":
    # Create an API client
    client = CloudprinterAPIClient()
    
    # Get a list of products
    try:
        products = client.get_products()
        for product in products:
            print(f"Product: {product.name} ({product.reference})")
    except Exception as e:
        print(f"Error getting products: {e}")
        
        for product in products:
            print(f"Product:{product}")
    
    # Get detailed information for a specific product
    try:
        reference = "calendar_desk_us_850x375_p_12_single_fc_tnr"  # Example product reference
        product_info = client.get_product_info(reference)
        print(f"Product Info for {reference}:")
        print(f"  Name: {product_info.name}")
        print(f"  Note: {product_info.note}")
        print(f"  Options: {(product_info.options)}")
        print(f"  Specs: {(product_info.specs)}")
    except Exception as e:
        print(f"Error getting product info: {e}")
    
    # Get a price quote
    try:
        # Create a quote request
        from models import ItemOption, QuoteItem
        
        quote_request = QuoteRequest(
            apikey=client.api_key,
            country="NL",
            items=[
                QuoteItem(
                    reference="ref_id_1234567",
                    product="textbook_pb_a4_p_bw",
                    count="1",
                    options=[
                        ItemOption(type="pageblock_80off", count="120"),
                        ItemOption(type="total_pages", count="120")
                    ]
                )
            ]
        )
        
        quote_response = client.get_quote(quote_request)
        print(f"Quote: {quote_response.price} {quote_response.currency}")
        print(f"Expires: {quote_response.expire_date}")
        print(f"Shipping Options:")
        for shipment in quote_response.shipments:
            for quote in shipment.quotes:
                print(f"  {quote.shipping_option}: {quote.price} {quote.currency}")
    except Exception as e:
        print(f"Error getting quote: {e}")

    # Get available shipping levels
    try:
        shipping_levels = client.get_shipping_levels()
        print("\nShipping Levels:")
        for level in shipping_levels:
            print(f"  {level.name}: {level.note}")
    except Exception as e:
        print(f"Error getting shipping levels: {e}")

    # Get available shipping countries
    try:
        shipping_countries = client.get_shipping_countries()
        print("\nShipping Countries:")
        for i, country in enumerate(shipping_countries):
            if i < 5:  # Show just the first 5 for brevity
                print(f"  {country.country_reference}: {country.note}")
            elif i == 5:
                print(f"  ... and {len(shipping_countries) - 5} more countries")
    except Exception as e:
        print(f"Error getting shipping countries: {e}")

    # Get available states for a specific country
    try:
        country_reference = "US"  # Example: United States
        shipping_states = client.get_shipping_states(country_reference)
        print(f"\nStates for {country_reference}:")
        for i, state in enumerate(shipping_states):
            
            if i < 5:  # Show just the first 5 for brevity
                print(f"  {state.state_reference}: {state.name}")
            elif i == 5:
                print(f"  ... and {len(shipping_states) - 5} more states")
    except Exception as e:
        print(f"Error getting shipping states: {e}") 