# Import the necessary libraries
import os  # For environment variable management
import streamlit as st  # For creating the web app interface
from langchain_google_genai import ChatGoogleGenerativeAI  # For interacting with Google Gemini via LangChain
from langgraph.prebuilt import create_react_agent  # For creating a ReAct agent
from langchain_core.messages import HumanMessage, AIMessage  # For message formatting
from langchain_exa.tools import ExaSearchResults # For web search capabilities
from dotenv import load_dotenv # For loading environment variables


# --- 1. Page Configuration and Title ---

# Set the title and a caption for the web page
st.title("🔍 Cek Fakta & Berita")
st.caption("Asisten verifikasi berita cerdas menggunakan Google Gemini & Exa")

# --- 2. API Key and Agent Initialization ---

# Load environment variables from .env file
# google api key 
load_dotenv()
# google_api_key = "Your-Google-API-Key-Here"
google_api_key = os.getenv("GOOGLE_API_KEY")

#add exa tools for web search
load_dotenv()
# exa_tool = ExaSearchResults(exa_api_key="Your-EXA-API-Key-Here")  
exa_api_key = os.getenv("EXA_API_KEY")
exa_tool = ExaSearchResults(exa_api_key=exa_api_key)

# This block of code handles the creation of the LangGraph agent.
# It's designed to be efficient: it only creates a new agent if one doesn't exist
# or if the user has changed the API key in the sidebar.


# Replace with your actual EXA API key


# We use `st.session_state` which is Streamlit's way of "remembering" variables
# between user interactions (like sending a message or clicking a button).
if "agent" not in st.session_state:
    try:
        # Initialize the LLM with the API key
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=google_api_key,
            temperature=0.7
        )
        
        # Create a simple ReAct agent with the LLM
        st.session_state.agent = create_react_agent(
            model=llm,
            tools=[exa_tool],
            prompt="""Role: News Verifier
            Action: Search via EXA to cross-reference facts. Classify the input into exactly one category:

            1. VALID: Factual & confirmed by credible sources.
            2. HOAX: False, fabricated, or manipulated content.
            3. CLICKBAIT: Misleading title/caption but content is real.
            4. SATIRE: Humor/Parody, not meant to be factual.
            5. OPINION: Subjective views/commentary, not news reports.
            6. UNVERIFIED: Lacking credible evidence to confirm/deny.
            
            Output Format:
            [CATEGORY]
            [Concise Explanation (max 3 sentences)]
            [List of Trusted Source Links]
            ”"""
        )
        
        # Store the new key in session state to compare against later.
        st.session_state._last_key = google_api_key
        # Since the key changed, we must clear the old message history.
        st.session_state.pop("messages", None)
    except Exception as e:
        # If the key is invalid, show an error and stop.
        st.error(f"Invalid API Key or configuration error: {e}")
        st.stop()

# --- 4. Chat History Management ---

# Initialize the message history (as a list) if it doesn't exist.
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. Display Past Messages ---

# Loop through every message currently stored in the session state.
for msg in st.session_state.messages:
    # For each message, create a chat message bubble with the appropriate role ("user" or "assistant").
    with st.chat_message(msg["role"]):
        # Display the content of the message using Markdown for nice formatting.
        st.markdown(msg["content"])

# --- 6. Handle User Input and Agent Communication ---

# Create a chat input box at the bottom of the page.
# The user's typed message will be stored in the 'prompt' variable.
prompt = st.chat_input("Type your message here...")

# Check if the user has entered a message.
if prompt:
    # 1. Add the user's message to our message history list.
    st.session_state.messages.append({"role": "user", "content": prompt})
    # 2. Display the user's message on the screen immediately for a responsive feel.
    with st.chat_message("user"):
        st.markdown(prompt)

    # 3. Get the assistant's response.
    # Use a 'try...except' block to gracefully handle potential errors (e.g., network issues, API errors).
    try:
        # Convert the message history to the format expected by the agent
        messages = []
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        # Send the user's prompt to the agent
        response = st.session_state.agent.invoke({"messages": messages})
        
        # Extract the answer from the response
        if "messages" in response and len(response["messages"]) > 0:
            raw = response["messages"][-1].content

            if isinstance(raw, list):
                answer = "\n".join([
                    item.get("text", "") 
                    for item in raw
                    if isinstance(item, dict) and "text" in item
                ])
            else:
                answer = str(raw)

            answer = answer.strip()

        else:
            answer = "I'm sorry, I couldn't generate a response."

    except Exception as e:
        # If any error occurs, create an error message to display to the user.
        answer = f"An error occurred: {e}"

    # 4. Display the assistant's response.
    with st.chat_message("assistant"):
        st.write(answer)
    # 5. Add the assistant's response to the message history list.
    st.session_state.messages.append({"role": "assistant", "content": answer})