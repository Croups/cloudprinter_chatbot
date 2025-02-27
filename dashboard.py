import streamlit as st
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from v2 import list_all_products, get_product_info, system_prompt, tools

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4o"

# Page configuration
st.set_page_config(
    page_title="Customer Support Assistant (MVP Product List, and Info)",
    page_icon="📚",
    layout="wide",
)



# Custom CSS for better appearance
st.markdown("""
<style>
    .chat-message {
        padding: 1.5rem; 
        border-radius: 0.5rem; 
        margin-bottom: 1rem; 
        display: flex;
    }
    .chat-message.user {
        background-color: #e6f7ff;
        border-left: 5px solid #2196F3;
        margin-left: 2rem;
        margin-right: 0.5rem;
    }
    .chat-message.assistant {
        background-color: #f0f0f0;
        border-left: 5px solid #4CAF50;
        margin-right: 2rem;
        margin-left: 0.5rem;
    }
    .message {
        width: 100%;
    }
    .stTextInput {
        padding-bottom: 1rem;
    }
    .stButton button {
        border-radius: 20px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .submit-button button {
        background-color: #4CAF50;
        color: white;
    }
    .clear-button button {
        background-color: #f44336;
        color: white;
    }
    .new-chat-button button {
        background-color: #2196F3;
        color: white;
    }
    .title-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 2rem;
    }
    .title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #333;
    }
    .user-label, .assistant-label {
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .user-label {
        color: #2196F3;
    }
    .assistant-label {
        color: #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="title-container"><div class="title">📚 Customer Support Assistant (MVP Product List, and Info) Assistant</div></div>', unsafe_allow_html=True)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt}
    ]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Initialize action flags
if "should_clear_chat" not in st.session_state:
    st.session_state.should_clear_chat = False

def call_function(name, args):
    """Call the appropriate function based on the name and arguments."""
    if name == "list_all_products":
        return [p.model_dump() for p in list_all_products()]
    elif name == "get_product_info":
        return get_product_info(**args).model_dump()

def submit_message(user_input):
    """Process user input, call OpenAI API, and update chat history."""
    if not user_input.strip():
        return
    
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    with st.spinner("Thinking..."):
        try:
            # Call OpenAI API with tools
            completion = client.chat.completions.create(
                model=model,
                messages=st.session_state.messages,
                tools=tools,
            )
            
            # Add assistant's response to messages
            assistant_message = completion.choices[0].message
            st.session_state.messages.append(assistant_message.model_dump())
            
            # Handle any tool calls
            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    
                    # Call the function
                    result = call_function(name, args)
                    
                    # Add the function response to messages
                    st.session_state.messages.append(
                        {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)}
                    )
                
                # Get a new response from the assistant with the tool results
                completion_2 = client.chat.completions.create(
                    model=model,
                    messages=st.session_state.messages,
                )
                
                # Add the final response to messages
                final_message = completion_2.choices[0].message
                st.session_state.messages.append(final_message.model_dump())
                st.session_state.chat_history.append({"role": "assistant", "content": final_message.content})
            else:
                # If no tool calls, just display the assistant's message
                st.session_state.chat_history.append({"role": "assistant", "content": assistant_message.content})
                
        except Exception as e:
            st.error(f"Error: {e}")
            st.session_state.chat_history.append({"role": "assistant", "content": f"Sorry, I encountered an error: {str(e)}"})

def clear_chat():
    """Clear the entire chat history"""
    st.session_state.messages = [
        {"role": "system", "content": system_prompt}
    ]
    st.session_state.chat_history = []
    st.session_state.should_clear_chat = True
    st.rerun()

# Display chat history
chat_container = st.container()
with chat_container:
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message user"><div class="message"><div class="user-label">You</div>{message["content"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message assistant"><div class="message"><div class="assistant-label">Assistant</div>{message["content"]}</div></div>', unsafe_allow_html=True)

# Input area at the bottom
input_container = st.container()
with input_container:
    # Create a form to better control input submission
    with st.form(key="message_form", clear_on_submit=True):
        user_input = st.text_input("Message:", key="user_message")
        
        # Create columns for the form buttons
        col1, col2 = st.columns([1, 3])
        
        with col1:
            submit_button = st.form_submit_button("Submit")
        
        # Process the form submission
        if submit_button and user_input:
            submit_message(user_input)
            st.rerun()
    
    # Create a row for the action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("New Chat", key="new_chat"):
            clear_chat()
            
    with col2:
        st.button("Clear Input", key="clear", on_click=lambda: None)  # This button now clears automatically due to the form

# Sidebar with information
with st.sidebar:
    st.title("About")
    st.markdown("""
    
    ### Features:
    - Get a list of all available products
    - Get detailed information about specific products
    - Ask questions about product specifications
    
    ### Sample Questions:
    - What products are available?
    - Tell me about the Textbook CW A6 P BW
    - What are the specifications of the Textbook CW A5 P BW?
    """)
    
    # Display available products in the sidebar
    st.subheader("Available Products")
    products = list_all_products()
    for product in products:
        st.markdown(f"**{product.name}** - {product.reference}")
