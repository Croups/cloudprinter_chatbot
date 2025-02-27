import os
import json
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI
import uuid

from models import (
    Product, ProductInfo, ProductOption, ProductSpec,
    QuoteRequest, QuoteResponse, QuoteItem, ItemOption,
    ShippingLevel, ShippingCountry, ShippingState, UserIntent
)
from cloudprinter_api import CloudprinterAPIClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # Default to GPT-4o but allow override

# Initialize Cloudprinter API client
cloudprinter_client = CloudprinterAPIClient()

# Create a global conversation context to track what we've learned about the user's request
conversation_context = {
    "product_type": None,
    "product_reference": None,
    "quantity": None,
    "paper_type": None,
    "paper_weight": None,
    "laminate": None,
    "country": None,
    "state": None, 
    "city": None,
    "delivery_speed": None,
    "quote_result": None,
    "selected_options": []
}

# Add token usage tracking
token_usage = {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
}

# --------------------------------------------------------------
# Tool definitions for OpenAI API
# --------------------------------------------------------------

tools = [
    {
        "type": "function",
        "function": {
            "name": "list_all_products",
            "description": "Get a list of all available print products with basic information",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Filter products by category (e.g., 'Business Cards', 'Textbook BW')"
                    }
                },
                "required": [],
            },
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "get_product_info",
            "description": "Get detailed information about a specific product including options and specifications",
            "parameters": {
                "type": "object",
                "properties": {
                    "reference": {
                        "type": "string",
                        "description": "The unique product reference code"
                    }
                },
                "required": ["reference"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_shipping_countries",
            "description": "Get a list of all countries where shipping is available",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_shipping_states",
            "description": "Get a list of all states/regions for a specific country",
            "parameters": {
                "type": "object",
                "properties": {
                    "country_reference": {
                        "type": "string",
                        "description": "The country code (ISO 3166-1 alpha-2)"
                    }
                },
                "required": ["country_reference"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_shipping_levels",
            "description": "Get a list of all available shipping options",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_quote",
            "description": "Get a price quote for an order",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_reference": {
                        "type": "string",
                        "description": "The reference code of the product"
                    },
                    "quantity": {
                        "type": "string",
                        "description": "The quantity of products to order"
                    },
                    "country": {
                        "type": "string",
                        "description": "The country code (ISO 3166-1 alpha-2) for delivery"
                    },
                    "state": {
                        "type": "string",
                        "description": "The state code for delivery (required for some countries)",
                        "default": None
                    },
                    "options": {
                        "type": "array",
                        "description": "List of product options",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "description": "The option type"
                                },
                                "count": {
                                    "type": "string",
                                    "description": "The count or quantity for this option"
                                }
                            }
                        },
                        "default": []
                    }
                },
                "required": ["product_reference", "quantity", "country"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_conversation_context",
            "description": "Update the conversation context with new information gathered from the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_type": {
                        "type": "string",
                        "description": "The type of product (e.g., 'business cards', 'book', 'flyer')"
                    },
                    "product_reference": {
                        "type": "string",
                        "description": "The reference code for the selected product"
                    },
                    "quantity": {
                        "type": "string",
                        "description": "The quantity requested by the user"
                    },
                    "paper_type": {
                        "type": "string",
                        "description": "The type of paper (e.g., 'glossy', 'matte', 'offset')"
                    },
                    "paper_weight": {
                        "type": "string",
                        "description": "The weight of paper (e.g., '250gsm', '300gsm')"
                    },
                    "laminate": {
                        "type": "string",
                        "description": "The laminate finish (e.g., 'glossy', 'matte', 'none')"
                    },
                    "country": {
                        "type": "string",
                        "description": "The delivery country"
                    },
                    "state": {
                        "type": "string",
                        "description": "The delivery state/region (for countries requiring it)"
                    },
                    "city": {
                        "type": "string",
                        "description": "The delivery city"
                    },
                    "delivery_speed": {
                        "type": "string",
                        "description": "The preferred delivery speed (e.g., 'fast', 'standard')"
                    },
                    "selected_options": {
                        "type": "array",
                        "description": "List of selected product options",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string"
                                },
                                "count": {
                                    "type": "string"
                                }
                            }
                        }
                    }
                },
                "required": [],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_option_selection",
            "description": "Select a specific option for the product",
            "parameters": {
                "type": "object",
                "properties": {
                    "option_type": {
                        "type": "string",
                        "description": "The type of option (e.g., 'type_product_material', 'type_sheet_product_finish')"
                    },
                    "option_reference": {
                        "type": "string",
                        "description": "The reference code of the selected option (e.g., 'paper_300ecb', 'product_finish_gloss')"
                    }
                },
                "required": ["option_type", "option_reference"],
            },
        }
    }
]

# --------------------------------------------------------------
# Tool implementations
# --------------------------------------------------------------

def list_all_products(category: Optional[str] = None) -> List[Dict]:
    """
    Get a list of all available products from the Cloudprinter API.
    Uses LLM to intelligently filter products based on user's request.
    
    Args:
        category: Optional category to filter products by
        
    Returns:
        A list of Product objects as dictionaries.
    """
    try:
        # Get all products from the API
        all_products = cloudprinter_client.get_products()
        logger.info(f"Retrieved {len(all_products)} total products")
        
        # Create a simplified list with just name and category for LLM processing
        simplified_products = []
        for p in all_products:
            simplified_products.append({
                "name": p.name,
                "category": p.category
            })
            
        logger.info(f"Simplified products: {simplified_products[:20]}")
        
        # Determine what user is looking for
        search_term = category 
        if not search_term:
            logger.info("No search term available, returning limited product set")
        
        logger.info(f"Using LLM to find products relevant to: {search_term}")
        
        # Prepare prompt for the LLM to find relevant products
        llm_prompt = f"""
        You received a list of products with their names and categories.
        {json.dumps(simplified_products, indent=2)}
        
        Return the names of the products that categories matches or synonyms of: "{search_term}
        Return the product names as a simple comma-separated list, with no additional text or explanations.
        Be sure you give the exact name of the product as listed, not a synonym.
        """
        
        # Call the LLM to get relevant products
        messages = [
            {"role": "system", "content": "You are a helpful product matching assistant that returns only the requested information with no extra text."},
            {"role": "user", "content": llm_prompt}
        ]
        
        logger.info("Calling GPT-4o-mini to identify matching products")
        llm_response = client.chat.completions.create(
            model=model,  # Using GPT-4o as requested
            messages=messages,
            temperature=0.3,  # Lower temperature for more consistent results
        )
        
        matching_names = llm_response.choices[0].message.content.strip()
        logger.info(f"LLM identified these product names: {matching_names}")
        
        # Parse the list of names
        name_list = [name.strip() for name in matching_names.split(',')]
        
        # Filter the products based on names returned by the LLM
        filtered_products = []
        for product in all_products:
            if any(name.lower() in product.name.lower() for name in name_list):
                filtered_products.append(product)
                     
        # Log the results
        logger.info(f"Found {len(filtered_products)} products matching '{search_term}'")
        for i, product in enumerate(filtered_products):
            logger.info(f"Match {i+1}: {product.name} - Category: {product.category}")      # Return the filtered products
        return [product.model_dump() for product in filtered_products]
    
    except Exception as e:
        logger.error(f"Error finding products: {e}")
        return [{"error": str(e)}]

def get_product_info(reference: str) -> Dict:
    """
    Get detailed information about a specific product from the Cloudprinter API.
    
    Args:
        reference: The product reference code.
        
    Returns:
        Product information with options and specifications.
    """
    try:
        # Get product info from the API
        product_info = cloudprinter_client.get_product_info(reference)
        
        # Update the conversation context with the product reference
        update_conversation_context(product_reference=reference)
        
        # Store available options in the context for future reference
        if hasattr(product_info, 'options') and product_info.options:
            # Group options by type for easier selection later
            option_groups = {}
            for option in product_info.options:
                if option.type not in option_groups:
                    option_groups[option.type] = []
                option_groups[option.type].append({
                    "reference": option.reference,
                    "note": option.note,
                    "default": option.default
                })
            
            # Store the grouped options in the context
            update_conversation_context(available_options=option_groups)
            logger.info(f"Stored {len(option_groups)} option groups in context")
            
        return product_info.model_dump()
    except Exception as e:
        logger.error(f"Error getting product info: {e}")
        return {"error": str(e)}

def get_shipping_countries() -> List[Dict]:
    """
    Get a list of all available shipping countries.
    
    Returns:
        List of shipping countries as dictionaries.
    """
    try:
        countries = cloudprinter_client.get_shipping_countries()
        return [country.model_dump() for country in countries]
    except Exception as e:
        logger.error(f"Error getting shipping countries: {e}")
        return [{"error": str(e)}]

def get_shipping_states(country_reference: str) -> List[Dict]:
    """
    Get a list of all available shipping states for a specific country.
    
    Args:
        country_reference: The country code (ISO 3166-1 alpha-2).
    
    Returns:
        List of shipping states as dictionaries.
    """
    try:
        states = cloudprinter_client.get_shipping_states(country_reference)
        return [state.model_dump() for state in states]
    except Exception as e:
        logger.error(f"Error getting shipping states: {e}")
        return [{"error": str(e)}]

def get_shipping_levels() -> List[Dict]:
    """
    Get a list of all available shipping levels.
    
    Returns:
        List of shipping levels as dictionaries.
    """
    try:
        levels = cloudprinter_client.get_shipping_levels()
        return [level.model_dump() for level in levels]
    except Exception as e:
        logger.error(f"Error getting shipping levels: {e}")
        return [{"error": str(e)}]

def get_quote(product_reference: str, quantity: str, country: str, state: Optional[str] = None, 
              options: Optional[List[Dict[str, str]]] = None) -> Dict:
    """
    Get a price quote for a product with the specified options and shipping details.
    """
    try:
        # Create a unique reference for the quote item
        item_reference = f"quote_{uuid.uuid4().hex[:8]}"
        
        # Format the options correctly using the stored selections
        item_options = []
        
        # Use the selected options from the conversation context
        if conversation_context.get("selected_options"):
            for option in conversation_context["selected_options"]:
                if "type" in option and "reference" in option:
                    item_options.append(ItemOption(
                        type=option["reference"],  # The reference is the option identifier
                        count="1"  # Most options use count=1 for selection
                    ))
                    logger.info(f"Adding option from context: {option['reference']}")
        
        # Add any additional options provided directly
        if options:
            for option in options:
                if "reference" in option:
                    # Check if this option is already included
                    if not any(o.type == option["reference"] for o in item_options):
                        item_options.append(ItemOption(
                            type=option["reference"],
                            count="1"
                        ))
                        logger.info(f"Adding additional option: {option['reference']}")
        
        # Create the quote request
        quote_request = QuoteRequest(
            apikey=cloudprinter_client.api_key,
            country=country,
            state=state,
            items=[
                QuoteItem(
                    reference=item_reference,
                    product=product_reference,
                    count=quantity,
                    options=item_options
                )
            ]
        )
        
        logger.info(f"Sending quote request: {quote_request.model_dump_json()}")
        
        # Get the quote from the API
        quote_response = cloudprinter_client.get_quote(quote_request)
        
        # Update the conversation context with the quote result
        update_conversation_context(quote_result=quote_response.model_dump())
        
        return quote_response.model_dump()
    
    except Exception as e:
        logger.error(f"Error getting quote: {e}")
        return {"error": str(e)}

def update_conversation_context(**kwargs) -> Dict:
    """
    Update the conversation context with new information.
    
    Args:
        **kwargs: Key-value pairs to update in the context.
    
    Returns:
        The updated context.
    """
    global conversation_context
    
    # Update only the keys that are provided
    for key, value in kwargs.items():
        if key == "selected_options" and value:
            # If this is an update to selected_options, append rather than replace
            if not conversation_context.get("selected_options"):
                conversation_context["selected_options"] = []
                
            # Format options correctly for API use
            for option in value:
                if option not in conversation_context["selected_options"]:
                    conversation_context["selected_options"].append(option)
                    logger.info(f"Added option to context: {option}")
        elif value is not None:
            # For other fields, just update the value
            conversation_context[key] = value
    
    # Log the updated context
    logger.info(f"Updated conversation context: {json.dumps(conversation_context, indent=2)}")
    
    return conversation_context

def update_option_selection(option_type: str, option_reference: str) -> Dict:
    """
    Update the selected option for a specific option type.
    
    Args:
        option_type: The type of option being selected (e.g., 'type_product_material')
        option_reference: The reference code of the selected option
        
    Returns:
        The updated conversation context
    """
    global conversation_context
    
    # Initialize selected options if not already present
    if "selected_options" not in conversation_context:
        conversation_context["selected_options"] = []
    
    # Remove any existing options of the same type
    conversation_context["selected_options"] = [
        opt for opt in conversation_context["selected_options"] 
        if isinstance(opt, dict) and opt.get("type") != option_type
    ]
    
    # Add the new option
    conversation_context["selected_options"].append({
        "type": option_type,
        "reference": option_reference
    })
    
    logger.info(f"Updated option selection: {option_type} = {option_reference}")
    
    return conversation_context

def call_function(name, arguments):
    """
    Call the appropriate function based on the function name and arguments.
    
    Args:
        name: The name of the function to call.
        arguments: The arguments to pass to the function.
    
    Returns:
        The result of the function call.
    """
    function_map = {
        "list_all_products": list_all_products,
        "get_product_info": get_product_info,
        "get_shipping_countries": get_shipping_countries,
        "get_shipping_states": get_shipping_states,
        "get_shipping_levels": get_shipping_levels,
        "get_quote": get_quote,
        "update_conversation_context": update_conversation_context,
        "update_option_selection": update_option_selection
    }
    
    if name not in function_map:
        raise ValueError(f"Unknown function: {name}")
    
    logger.info(f"Calling function {name} with args: {json.dumps(arguments, indent=2)}")
    result = function_map[name](**arguments)
    
    # For large results, log a summary instead of the full result
    if name == "list_all_products":
        logger.info(f"Function {name} returned {len(result)} products")
    elif name == "get_quote":
        if "error" in result:
            logger.info(f"Function {name} returned error: {result['error']}")
        else:
            logger.info(f"Function {name} returned quote: {result.get('price', 'unknown')} {result.get('currency', '')}")
    else:
        logger.info(f"Function {name} returned result")
    
    return result

# --------------------------------------------------------------
# Chat loop
# --------------------------------------------------------------

def run_chat_loop():
    """
    Run an interactive chat loop that handles user input, API calls, and responses.
    """
    global token_usage
    
    # Initialize the conversation
    messages = [
        {"role": "system", "content": """
        You are a helpful and friendly chatbot for Cloudprinter.com. Your role is to assist users in getting accurate price information 
        for print products. Engage in natural conversation to gather the necessary details like product type, paper specifications, 
        quantity, and delivery location.

        Always maintain a conversational, helpful, and friendly tone. Ask for one piece of information at a time, and guide the user 
        through the process step by step.

        When helping users select a product:
        1. First determine what type of product they want (business cards, books, etc.)
        2. Use list_all_products to find matching products
        3. When a product is selected, use get_product_info to fetch details and available options
        4. For each option type (paper, finish, etc.):
           - Present the exact available options to the user
           - When they make a selection, use update_option_selection to record their choice
        5. Ask for quantity and delivery location
        6. Use get_quote to get pricing with all selected options

        Make sure to use the exact option references from the API when selecting options. Never make up option references.
        """}
    ]
    
    print("\nCloudprinter.com Chat Assistant")
    print("Type 'exit' or 'quit' to end the conversation\n")
    
    while True:
        # Get user input
        user_input = input("You: ")
        
        # Check if user wants to exit
        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye! Thank you for using Cloudprinter.com Chat Assistant.")
            # Display token usage statistics before exiting
            print(f"\nToken Usage Statistics:")
            print(f"Model: {model}")
            print(f"Input tokens: {token_usage['prompt_tokens']}")
            print(f"Output tokens: {token_usage['completion_tokens']}")
            print(f"Total tokens: {token_usage['total_tokens']}")
            break
        
        # Add the user's message to the conversation
        messages.append({"role": "user", "content": user_input})
        
        try:
            # Log the current conversation state
            logger.info(f"Current conversation context: {json.dumps(conversation_context, indent=2)}")
            logger.info(f"Sending {len(messages)} messages to OpenAI")
            
            # Get a response from the AI with tool calls if needed
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
            )
            
            # Track token usage
            if hasattr(completion, 'usage') and completion.usage:
                token_usage['prompt_tokens'] += completion.usage.prompt_tokens
                token_usage['completion_tokens'] += completion.usage.completion_tokens
                token_usage['total_tokens'] += completion.usage.total_tokens
                logger.info(f"Token usage: +{completion.usage.prompt_tokens} prompt, +{completion.usage.completion_tokens} completion")
            
            # Extract the assistant's message
            assistant_message = completion.choices[0].message
            
            # Log the assistant's response
            if assistant_message.tool_calls:
                logger.info(f"Assistant requested {len(assistant_message.tool_calls)} tool calls")
            else:
                logger.info(f"Assistant response: {assistant_message.content}")
            
            # Add to the conversation history
            messages.append(assistant_message.model_dump())
            
            # Check if the AI wants to call tools
            if assistant_message.tool_calls:
                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Call the function
                    function_response = call_function(function_name, function_args)
                    
                    # Add the function response to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(function_response)
                    })
                
                # Get a new response that takes into account the function results
                logger.info(f"Getting final response after tool calls")
                second_completion = client.chat.completions.create(
                    model=model,
                    messages=messages,
                )
                
                # Track token usage for the second completion
                if hasattr(second_completion, 'usage') and second_completion.usage:
                    token_usage['prompt_tokens'] += second_completion.usage.prompt_tokens
                    token_usage['completion_tokens'] += second_completion.usage.completion_tokens
                    token_usage['total_tokens'] += second_completion.usage.total_tokens
                    logger.info(f"Token usage: +{second_completion.usage.prompt_tokens} prompt, +{second_completion.usage.completion_tokens} completion")
                
                final_response = second_completion.choices[0].message.content
                logger.info(f"Final response: {final_response}")
                
                messages.append({"role": "assistant", "content": final_response})
                print(f"Assistant: {final_response}")
            else:
                # If no tool calls, just print the assistant's response
                print(f"Assistant: {assistant_message.content}")
                
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            logger.error(error_message)
            print(f"Assistant: I'm sorry, I encountered an error. {error_message}")
            
            # Add the error message to the conversation
            messages.append({"role": "assistant", "content": error_message})

        # Print a divider for readability
        print("\n" + "-" * 10 + "\n")

if __name__ == "__main__":
    run_chat_loop() 