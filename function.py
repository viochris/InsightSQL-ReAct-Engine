import streamlit as st

def init_state():
    """
    Initializes the Session State variables if they do not exist.
    This ensures the app has a stable memory structure across re-runs.
    """
    # Initialize the chat history list
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Initialize the LLM object placeholder
    if "llm" not in st.session_state:
        st.session_state.llm = None
    
    # Initialize the Database Toolkit placeholder
    if "toolkit" not in st.session_state:
        st.session_state.toolkit = None

    if "agent_memory" not in st.session_state:
        st.session_state.agent_memory = None

def change_on_api_key():
    """
    Triggered when the user modifies the API Key.
    Performs a 'Hard Reset' to ensure the new key is used for future connections.
    """
    # 1. Clear chat history to avoid context mismatch
    st.session_state.messages = []
    
    # 2. Reset the LLM and Toolkit to force re-initialization
    st.session_state.llm = None
    st.session_state.toolkit = None
    st.session_state.agent_memory = None
    
    # 3. Completely remove the Agent Executor from memory
    # Using .pop() ensures the key is deleted, forcing the app to rebuild the agent
    st.session_state.pop("agent_executor", None)
    
    # Notify the user that the system has been reset
    st.toast("API Key updated! System reset.", icon="🔄")

def reset_state():
    """
    Triggered by the 'Full System Reset' button.
    Performs a 'Hard Reset': Wipes the Chat UI, destroys the Agent's Memory, 
    and kills the Database Connection. 
    Use this to start completely fresh (Tabula Rasa).
    """
    # 1. Clear chat history (UI)
    st.session_state.messages = []
    
    # 2. Reset the LLM, Toolkit, and Brain to force re-initialization
    st.session_state.llm = None
    st.session_state.toolkit = None
    st.session_state.agent_memory = None 
    
    # 3. Kill the Executor
    st.session_state.pop("agent_executor", None)
    
    # Notify the user
    st.toast("System fully reset. Memory wiped!", icon="🔄")

def reset_chat_display():
    """
    Triggered by the 'Clear Screen Only' button.
    Performs a 'Visual Reset': Removes chat messages from the screen ONLY.
    CRITICAL: The Agent's memory is PRESERVED, so the AI still remembers 
    what you discussed previously.
    """
    # 1. Clear the message history list (Visual/UI only)
    st.session_state.messages = []
    
    # NOTE: We intentionally DO NOT touch 'agent_memory' here.
    # This keeps the context alive.
    
    # Notify the user
    st.toast("Screen cleared! Memory retained.", icon="🧹")

def change_on_lan():
    """
    Triggered when the user modifies the 'Language' selection in the sidebar.
    This performs a specific reset to ensure the new language preference is 
    injected into the Agent's system prompt.
    """
    # 1. Destroy the current Agent Executor
    # We must remove it from the session state so that the app detects it's missing
    # and rebuilds it with the new 'chosen_language' variable in the prompt.
    st.session_state.pop("agent_executor", None)
    
    # 2. Notify the user of the update
    # Provides visual feedback that the system is re-configuring its 'brain' for the new language.
    st.toast("Language preference updated! Reconfiguring AI Agent...", icon="🌐")