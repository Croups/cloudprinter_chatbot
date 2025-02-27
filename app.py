import streamlit as st
import json
import logging
from typing import List, Dict
import os
from dotenv import load_dotenv

# Import functionality from chatbot.py
from chatbot import (
    tools, client, model, CloudprinterAPIClient,
    update_conversation_context, call_function
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="streamlit_app.log",  # Log to file instead of console
    filemode="a"
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Cloudprinter.com Chat Assistant",
    page_icon="🖨️",
    layout="centered"
)

# Add custom CSS
st.markdown("""
<style>
    .chat-message {
        padding: 1.5rem; 
        border-radius: 0.5rem; 
        margin-bottom: 1rem; 
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #f0f2f6;
    }
    .chat-message.assistant {
        background-color: #e6f7ff;
    }
    .chat-message .message-content {
        display: flex;
        margin-top: 0;
    }
    .chat-message .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 1rem;
    }
    .main {
        padding-bottom: 70px;
    }
    h1 {
        color: #1E88E5;
    }
    .stButton button {
        background-color: #1E88E5;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = [
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

if "conversation_context" not in st.session_state:
    st.session_state.conversation_context = {
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

# Add a flag to track if we've processed the latest message
if "message_processed" not in st.session_state:
    st.session_state.message_processed = True

# Add token usage tracking
if "token_usage" not in st.session_state:
    st.session_state.token_usage = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0
    }

# Function to handle sending a message
def send_message():
    if st.session_state.user_message:
        # Get message text from the session state
        user_input = st.session_state.user_message
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Mark that we have a new unprocessed message
        st.session_state.message_processed = False
        
        # Clear the input by setting it to an empty string
        st.session_state.user_message = ""

# Add a welcome header
st.title("Cloudprinter.com Chat Assistant")
st.markdown("Get accurate price quotes for your print products. Ask me anything!")

# Display chat messages
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        if message["role"] != "system":  # Don't show system messages
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user">
                    <div class="message-content">
                        <img src="https://api.dicebear.com/7.x/personas/svg?seed=user" class="avatar">
                        <div>{message["content"]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant">
                    <div class="message-content">
                        <img src="https://api.dicebear.com/7.x/personas/svg?seed=cloudprinter" class="avatar">
                        <div>{message["content"]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# Input area with a form and submit button
st.markdown("---")
input_container = st.container()
with input_container:
    col1, col2 = st.columns([6, 1])
    with col1:
        st.text_input(
            "Message:",
            key="user_message",
            placeholder="Type your message here...",
            label_visibility="collapsed",
            on_change=send_message
        )
    with col2:
        st.button("Send", on_click=send_message)

# Process the latest user message and generate response, but only if it's unprocessed
if (st.session_state.messages and 
    st.session_state.messages[-1]["role"] == "user" and 
    not st.session_state.message_processed):
    
    with st.spinner("Thinking..."):
        try:
            # Mark message as being processed to prevent reprocessing
            st.session_state.message_processed = True
            
            # Log the current conversation state
            logger.info(f"Current context: {json.dumps(st.session_state.conversation_context, indent=2)}")
            logger.info(f"Sending {len(st.session_state.messages)} messages to OpenAI")
            
            # Get response from OpenAI with tool calls if needed
            completion = client.chat.completions.create(
                model=model,
                messages=st.session_state.messages,
                tools=tools,
                tool_choice="auto",
            )
            
            # Track token usage
            if hasattr(completion, 'usage') and completion.usage:
                st.session_state.token_usage['prompt_tokens'] += completion.usage.prompt_tokens
                st.session_state.token_usage['completion_tokens'] += completion.usage.completion_tokens
                st.session_state.token_usage['total_tokens'] += completion.usage.total_tokens
                logger.info(f"Token usage: +{completion.usage.prompt_tokens} prompt, +{completion.usage.completion_tokens} completion")
            
            # Extract the assistant's message
            assistant_message = completion.choices[0].message
            
            # Log the assistant's response
            if assistant_message.tool_calls:
                logger.info(f"Assistant requested {len(assistant_message.tool_calls)} tool calls")
            else:
                logger.info(f"Assistant response: {assistant_message.content}")
            
            # Add to the conversation history
            st.session_state.messages.append(assistant_message.model_dump())
            
            # Check if the AI wants to call tools
            if assistant_message.tool_calls:
                # Show a spinner while processing
                with st.spinner("Processing..."):
                    # Execute each tool call
                    for tool_call in assistant_message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        # Call the function
                        function_response = call_function(function_name, function_args)
                        
                        # Add the function response to messages
                        st.session_state.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(function_response)
                        })
                    
                    # Get a new response that takes into account the function results
                    logger.info(f"Getting final response after tool calls")
                    second_completion = client.chat.completions.create(
                        model=model,
                        messages=st.session_state.messages,
                    )
                    
                    # Track token usage for the second completion
                    if hasattr(second_completion, 'usage') and second_completion.usage:
                        st.session_state.token_usage['prompt_tokens'] += second_completion.usage.prompt_tokens
                        st.session_state.token_usage['completion_tokens'] += second_completion.usage.completion_tokens
                        st.session_state.token_usage['total_tokens'] += second_completion.usage.total_tokens
                        logger.info(f"Token usage: +{second_completion.usage.prompt_tokens} prompt, +{second_completion.usage.completion_tokens} completion")
                    
                    final_response = second_completion.choices[0].message.content
                    logger.info(f"Final response: {final_response}")
                    
                    st.session_state.messages.append({"role": "assistant", "content": final_response})
            
            # No need to rerun - Streamlit will handle it
                
        except Exception as e:
            # Handle errors
            error_message = f"I'm sorry, I encountered an error: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_message})
            logger.error(f"Error: {str(e)}")
            
        # Force a rerun to display the new messages
        st.rerun()

# Add a sidebar with additional information
with st.sidebar:
    st.header("About Cloudprinter.com")
    st.markdown("""
    **Cloudprinter.com** connects you to a global network of print facilities.
    
    This assistant helps you get accurate price quotes for various print products including:
    - Business Cards
    - Flyers
    - Brochures
    - Books
    - Calendars
    - And more!
    """)
    
    # Show the current context
    if st.checkbox("Show Conversation Context"):
        st.json(st.session_state.conversation_context)
    
    # Show token usage statistics
    if st.checkbox("Show Token Usage"):
        st.markdown(f"""
        **Token Usage Statistics:**
        - Model: {model}
        - Input tokens: {st.session_state.token_usage['prompt_tokens']}
        - Output tokens: {st.session_state.token_usage['completion_tokens']}
        - Total tokens: {st.session_state.token_usage['total_tokens']}
        """)
    
    # Add a reset button
    if st.button("Reset Conversation"):
        st.session_state.messages = [st.session_state.messages[0]]  # Keep only the system message
        st.session_state.conversation_context = {key: None for key in st.session_state.conversation_context}
        st.session_state.conversation_context["selected_options"] = []
        st.session_state.token_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
        st.session_state.message_processed = True  # Reset the processing flag
        logger.info("Conversation reset by user") 