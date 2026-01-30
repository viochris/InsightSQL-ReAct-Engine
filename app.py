import streamlit as st
# Import LangChain community tools specifically for constructing the SQL Agent
from langchain_community.agent_toolkits.sql.base import create_sql_agent
# Import utilities for establishing database connections and managing schemas
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
# Import the Google Gemini chat model interface
from langchain_google_genai import ChatGoogleGenerativeAI
# Import the specific handler to visualize the agent's reasoning steps (thoughts/actions) in the Streamlit UI
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
# Import custom helper functions for session state management (persistence)
from function import init_state, change_on_api_key, reset_state, reset_chat_display, change_on_lan
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.memory import ConversationSummaryMemory
from langchain import hub

# Initialize session state variables (messages, llm, toolkit) immediately 
# to prevent errors during app re-runs
init_state()

# Configure the Streamlit page settings
# This sets the browser tab title, favicon, and layout mode
st.set_page_config(
    page_title="InsightSQL | Advanced Reasoning",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Display the main application header
st.title("📊 InsightSQL: ReAct Agent Engine")

# Render the introduction text using Markdown and HTML
# unsafe_allow_html=True is used here to center the subtitle text
st.markdown(
    """
    <div style="text-align: center; color: #666; font-size: 1.1rem; margin-bottom: 30px;">
        <b>Beyond simple answers. Experience the logic.</b>
    </div>
    
    Welcome to the advanced iteration of **InsightSQL**. Powered by a dedicated **ReAct Architecture**, this agent moves beyond black-box magic. 
    It provides full **transparency** by showcasing its reasoning process—analyzing your intent, strategically selecting database tools, and executing SQL queries step-by-step to deliver verifiable insights.
    
    ---
    """, 
    unsafe_allow_html=True
)

with st.sidebar:
    # Sidebar header with an emoji for better visual hierarchy
    st.header("⚙️ Page Configuration")

    st.divider()

    # Input widget for the API Key
    # 'type="password"' masks the input characters for security
    # 'on_change' triggers the cleanup function immediately if the key is modified
    st.text_input(
        "🔑 Google API Key", # Improved label with emoji
        type="password",
        key="google_api_key",
        on_change = change_on_api_key,
        help="Paste your Google Gemini API Key here. This is required to power the AI agent." # Filled help text
    )

    # Language Selection Widget
    # Allows the user to dictate the language of the final natural language response.
    # This selection is dynamically injected into the system prompt via the '{chosen_language}' variable.
    chosen_language = st.selectbox(
        "🌐 Language Preference", # Improved Label: Adds an emoji for visual cue and sounds professional.
        ["English", "Indonesian"],
        index=0,
        on_change=change_on_lan, # Callback: Forces the Agent Executor to reset/rebuild when changed.
        help="Select the language for the AI's analysis. Changing this will re-initialize the agent to apply the new persona." # Informative Help Text
    )

    st.divider()

    # Button to clear the chat history (Soft Reset)
    # This invokes 'reset_state' to clear messages without breaking the database connection
    st.button(
        "🧹 Clear Screen Only", # Improved label with emoji
        on_click=reset_chat_display,
        use_container_width=True,
        help="Clears the chat text to declutter the screen, but the AI KEEPS its memory of the conversation." # Filled help text
    )

    st.button(
        "🔄 Full System Reset", # Improved label with emoji
        on_click=reset_state,
        type="primary",
        use_container_width=True,
        help="Wipes EVERYTHING: Chat history, AI Memory, and Connections. Starts 100% fresh." # Filled help text
    )

    # Main action button to initialize the Agent
    # Changing "Load Information" to "Connect to Database" is more accurate for an SQL Agent
    connect = st.button(
        "🚀 Connect to Database", # Improved label: Clearer action
        use_container_width=True,
        help="Initializes the connection to the 'dresses.db' file and builds the AI agent." # Filled help text
    )

    st.divider()

    # --- USER GUIDE & DOCUMENTATION ---
    # These sections provide self-service support, reducing the need for external explanations.
    
    # Expandable "How To Use" Guide
    # Strict linear flow: API -> Language -> Connect -> Chat.
    # Also added a specific pointer to the FAQ for database modification.
    with st.expander("📚 How To Use"):
        st.markdown("""
        **1. 🔑 API Configuration**
        Enter your **Google Gemini API Key** in the sidebar first. This is required to power the AI engine.
        
        **2. 🌐 Select Language**
        Choose your preferred response language (**English** or **Indonesian**). 
        
        **3. 🚀 Connect to Database**
        Click the **'Connect'** button to initialize the ReAct Agent and load the default dataset.
        *(⚠️ Want to switch to your own database? Please read the **FAQ** section below for technical instructions).*
        
        **4. 💬 Start Querying**
        Once connected, type your questions naturally in the chat.
        
        ---
        **💡 Pro Tip:**
        *Want to switch languages mid-conversation?* **Just change it in the sidebar!** The agent will automatically update its settings and answer your next question in the new language. No need to reconnect.
        """)

    # Expandable "FAQ" Section
    # Anticipates common user concerns regarding security, capabilities, and performance.
    with st.expander("❓ FAQ (Frequently Asked Questions)"):
        st.markdown("""
        **Q: Can this agent modify my database?**  
        A: **No.** The agent operates under strict **Read-Only** rules. It is explicitly instructed via system prompts to avoid DML statements like `INSERT`, `UPDATE`, or `DELETE`.
        
        **Q: How do I change the database to my own?**
        A: Since this is a specialized prototype, the database is currently linked via code. To use your own data:
        1. **Prepare your file:** Ensure you have a valid SQLite database file (e.g., `my_data.db`).
        2. **Upload:** Place the file in the **same root directory** as `app.py`.
        3. **Modify Code:** Open `app.py` and locate the connection setup (approx. **Line 185**).
        4. **Update URI:** Change the code from:  
           `db = SQLDatabase.from_uri("sqlite:///dresses.db")`  
           to:  
           `db = SQLDatabase.from_uri("sqlite:///YOUR_FILENAME.db")`

        **Q: Why does it take a few seconds to respond?**  
        A: Unlike basic chatbots, this is a **Reasoning Engine (ReAct)**. It performs multiple steps: *Thinking* (planning), *Acting* (querying SQL), and *Observing* (analyzing results) before answering. This ensures accuracy over speed.
        
        **Q: Is my data sent to Google?**  
        A: The LLM receives the **Table Schema** (structure) and the specific **Rows** returned by queries to generate answers. Your entire database is **not** uploaded.
        
        **Q: What happens if I change the language mid-conversation?**  
        A: The system will automatically **re-initialize** the agent's brain to adapt to the new language persona. Your chat history will be preserved, but the next answer will switch languages.
        """)
    
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; font-size: 0.85rem; color: #888;">
            © 2026 <b>Silvio Christian, Joe</b><br>
            Powered by <b>Google Gemini</b> 🚀<br><br>
            <a href="https://www.linkedin.com/in/silvio-christian-joe/" target="_blank" style="text-decoration: none; margin-right: 10px;">🔗 LinkedIn</a>
            <a href="mailto:viochristian12@gmail.com" style="text-decoration: none;">📧 Email</a>
        </div>
        """, 
        unsafe_allow_html=True
    )

# Check if the API Key has been provided by the user
if st.session_state.google_api_key:
    # Implement a Singleton pattern: Only initialize the LLM if it hasn't been created yet.
    # This prevents unnecessary re-initialization on every app rerun, saving resources.
    if st.session_state.llm is None:
        st.session_state.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            google_api_key=st.session_state.google_api_key,
            # Set temperature to 0.3 to ensure the model outputs are deterministic and precise,
            # which is critical for generating accurate SQL queries.
            temperature=0.3 
        )
        # Notify the user that the AI model is ready to use with a Success Icon
        st.toast("AI Engine initialized successfully!", icon="🧠")
else:
    # Display a warning with an icon if the user attempts to proceed without an API Key
    st.warning("Please enter your Google API Key to proceed.", icon="⚠️")

# Check if the 'Connect' button was clicked and the LLM is already initialized
if connect and st.session_state.llm is not None:
    # Ensure we don't re-initialize the toolkit if it already exists
    if st.session_state.toolkit is None:
        try:
            # Establish a connection to the SQLite database
            # Note: For MySQL/PostgreSQL, use the format: "dialect+driver://user:pass@host/dbname"
            db = SQLDatabase.from_uri("sqlite:///dresses.db")

            # Initialize the SQL Toolkit
            # This provides the Agent with the necessary tools to inspect the schema and execute queries
            st.session_state.toolkit = SQLDatabaseToolkit(db=db, llm=st.session_state.llm)

            # Notify the user with a Success Icon
            st.toast("✅ Database Connected! System Ready.", icon="🎉")
            
        except Exception as e:
            # Catch and display any errors during connection with an Error Icon
            # Convert error to string for analysis
            error_str = str(e).lower()

            # Check for specific error types to provide better guidance
            if "argumenterror" in error_str:
                # This usually happens if the SQLAlchemy URI string is malformed
                st.error("❌ Invalid Database URI. Please check the connection string format.", icon="📝")
            
            elif "operationalerror" in error_str:
                # This often happens if the file doesn't exist or permissions are denied
                st.error("❌ Operational Error. Is 'dresses.db' in the correct folder?", icon="📂")
            
            else:
                # Catch and display any other unexpected errors
                error_msg = f"❌ Connection Failed: {str(e)}"
                st.error(error_msg, icon="🚨")
    else:
        # Inform the user if the system is already running
        st.toast("⚡ System is already active. Ready to query!", icon="🤖")

# Handle the case where the user clicks 'Connect' without providing an API Key first
elif connect and st.session_state.llm is None:
    st.toast("⚠️ API Key Missing! Please check the sidebar.", icon="🔑")

# Check if the Database Toolkit is missing (meaning the user hasn't connected yet)
if st.session_state.toolkit is None:
    st.warning("⚠️ Database not connected. Please click **'Connect to Database'** in the sidebar.", icon="🔌")

# 0. INITIALIZE PERSISTENT MEMORY (THE BRAIN STORAGE)
# We perform this check at the global scope to ensure memory exists 
# before the AgentExecutor attempts to use it.
if st.session_state.llm is not None:
    # Check if memory is uninitialized (None). 
    # If it exists (from a previous run), we SKIP creation to preserve chat history.
    if st.session_state.agent_memory is None:
        st.session_state.agent_memory = ConversationSummaryMemory(
            memory_key="chat_history", 
            llm=st.session_state.llm, 
            return_messages=True
        )        

if "agent_executor" not in st.session_state \
    and st.session_state.llm is not None \
        and st.session_state.toolkit is not None:

        # --- ADVANCED CUSTOM AGENT ARCHITECTURE ---
        try:
            # 1. RETRIEVE DATABASE TOOLS
            # Extract the raw tool functions (Schema, Query, ListTables) directly from the toolkit
            # to allow for manual orchestration within the ReAct loop.
            tools = st.session_state.toolkit.get_tools()

            # 2. LOAD BASE PROMPT TEMPLATE
            # Pull the industry-standard ReAct structure from LangChain Hub.
            # This ensures the agent adheres to the Thought -> Action -> Observation pattern.
            prompt = hub.pull("hwchase17/react-chat")

            # 3. DEFINE SYSTEM INSTRUCTIONS & PERSONA
            # Custom prompt engineering to enforce strict SQL generation rules and 
            # ensure the final output is context-aware and analytically rich.
            prefix_prompt = f"""
            You are an expert Data Analyst and SQL Analyst. 
            Your goal is to answer user questions by querying a database.

            RULES:
            1. ALWAYS start by checking the list of tables ('sql_db_list_tables').
            2. Then, check the schema of the relevant table ('sql_db_schema').
            3. Construct a syntactically correct SQL query.
            4. Execute the query using 'sql_db_query'.
            5. If you get an error, check your query and try again.
            6. DO NOT execute DML statements (INSERT, UPDATE, DELETE).
            7. CRITICAL LANGUAGE OUTPUT RULE: When you have the answer, you MUST strictly use the format: "Final Answer: [Your answer in {chosen_language}]".
               - The User's chosen output language is: "{chosen_language}".
               - IGNORE the user's language for the final output; IT MUST BE IN {chosen_language}.
               - LOGIC CHECK:
                 * IF User asks in Indonesian AND "{chosen_language}" is English -> ANSWER IN ENGLISH.
                 * IF User asks in English AND "{chosen_language}" is Indonesian -> ANSWER IN INDONESIAN.
               - You MUST perform this translation step before giving the Final Answer.
               - DO NOT mimic the user's language. STICK TO "{chosen_language}".
               - If you do not start your final response with "Final Answer:", the system will crash. 
               - Format: "Final Answer: [Your answer strictly in {chosen_language}]".
               - Provide context and reasoning in your answer, not just numbers.
            8. SPECIAL RULE FOR CASUAL CHAT (NO TOOL USED):
               - Even if you do not use a tool (e.g., greetings like "Halo", "Hi"), you MUST STILL translate your response to "{chosen_language}".
               - Example: If User says "Halo" (Indo) and target is English -> Final Answer: "Hello! How can I help you with the database?"
               - NEVER reply in the user's language just to be polite. Stick to the target language.
            """

            # 4. INJECT CUSTOM RULES
            # Prepend the system instructions to the base template.
            # This prioritizes our rules before the agent processes conversation history.
            prompt.template = prefix_prompt + "\n\n" + prompt.template

            # 5. CONSTRUCT THE REASONING ENGINE
            # Bind the LLM, Tools, and the Custom Prompt to create the agent object.
            agent_brain = create_react_agent(
                llm=st.session_state.llm,
                tools=tools,
                prompt=prompt
            )

            # 6. INITIALIZE THE RUNTIME EXECUTOR (THE BODY)
            # The AgentExecutor orchestrates the loop: Thought -> Action -> Observation.
            st.session_state.agent_executor = AgentExecutor(
                agent=agent_brain,
                tools=tools,
                # CRITICAL: We inject the persistent 'st.session_state.agent_memory' here.
                # This ensures the Agent retains context/history even if the Executor is rebuilt 
                # (e.g., when switching languages).
                memory=st.session_state.agent_memory,
                # Enable robust error handling to prevent crashes from malformed LLM outputs.
                handle_parsing_errors=True,
                verbose=True
            )

        except Exception as e:
            # Normalize error message for case-insensitive matching
            error_msg = str(e).lower()
            answer = "" # Placeholder for the final user-facing message

            # 1. Handle API Quota Limits (Common with Gemini Free Tier)
            if "429" in error_msg or "quota" in error_msg or "resource exhausted" in error_msg:
                answer = "🚨 **API Quota Exceeded**\n\nThe AI Engine is temporarily busy. Google Gemini's free tier limits have been reached. Please wait a minute and try again."
            
            # 2. Handle Invalid API Key (Authentication failed)
            elif "api_key" in error_msg or "403" in error_msg or "permission denied" in error_msg:
                 answer = "🔑 **Invalid API Key**\n\nAuthentication failed. Please check the **'🔑 Google API Key'** provided in the sidebar. Ensure it is active and has permissions."

            # 3. Handle LangChain Hub Issues (Network or Repo errors during hub.pull)
            elif "hub" in error_msg or "connection" in error_msg or "failed to establish" in error_msg:
                 answer = "🌐 **Network Connection Error**\n\nFailed to retrieve the Agent Prompt Template from LangChain Hub. Please check your internet connection."

            # 4. Handle Toolkit/Database Issues (If tools cannot be extracted)
            elif "toolkit" in error_msg or "argument" in error_msg:
                 answer = "🛠️ **Toolkit Configuration Error**\n\nThe system could not extract necessary tools from the database connection. Please verify the database path."

            # 5. Handle General/Unknown Errors (Catch-all)
            else:
                answer = f"❌ **System Initialization Failed**\n\nAn unexpected error occurred while building the Agent Engine.\n\n**Technical Details:** `{error_msg}`"

            # Finally, display the structured error message
            st.error(answer, icon="⚠️")

# Render the chat history
# We iterate through the 'messages' list in the session state to persist the conversation
# across Streamlit re-runs (which happen every time the user interacts).
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Capture user input
# The := operator assigns the input to 'prompt_text' and returns True if input exists.
if prompt_text := st.chat_input("Ask a question about your data..."):
    
    # --- Pre-flight Checks (Guardrails) ---
    # Before processing, we ensure all components (LLM, Toolkit, Agent) are ready.
    
    if st.session_state.llm is None:
        st.warning("⚠️ AI Engine is not active. Please enter your API Key in the sidebar.", icon="🚫")
        
    elif st.session_state.toolkit is None:
        st.warning("⚠️ Database Toolkit is missing. Please click 'Connect to Database'.", icon="🔌")
        
    elif not st.session_state.agent_executor:
        st.warning("⚠️ Agent is not initialized. Please reload the connection.", icon="🤖")

    else:
        # --- Process Valid Input ---
        
        # 1. Append User Message to History
        st.session_state.messages.append({"role": "human", "content": prompt_text})
        
        # 2. Display User Message immediately in the UI
        st.chat_message("human").write(prompt_text)

        # 3. Generate AI Response
        with st.chat_message("ai"):
            try:
                # Initialize the StreamlitCallbackHandler
                # This handler creates an interactive container in the UI that displays 
                # the agent's "Thought Process" (SQL generation, execution, and observation) in real-time.
                st_callback = StreamlitCallbackHandler(st.container())

                # Invoke the SQL Agent with the Callback
                # We pass 'st_callback' to the invoke method so the agent can render its 
                # intermediate steps (Thought -> Action -> Observation) directly into the Streamlit container.
                response = st.session_state.agent_executor.invoke(
                    {"input": prompt_text},
                    {"callbacks": [st_callback]}
                )

                # Validate and Display Final Output
                # Once the reasoning is complete, we display the final natural language answer.
                if "output" in response and len(response["output"]) > 0:
                    st.markdown(response["output"])

                # 4. Append AI Response to History
                st.session_state.messages.append({"role": "ai", "content": response["output"]})

            except Exception as e:
                # Handle Runtime Errors (e.g., Invalid SQL generated, Database locked, etc.)
                # Convert error object to string for analysis
                error_str = str(e).lower()

                if "429" in error_str or "resource" in error_str:
                    # Specific handling for Google API Quota limits (Resource Exhausted)
                    st.error("⏳ API Quota Exceeded. Please wait a moment or check your Google Cloud plan.", icon="🛑")

                elif "api_key" in error_str or "400" in error_str:
                    # Specific handling for Invalid API Key errors (Authentication failed)
                    st.error("🔑 Invalid API Key. Please check your Google API Key in the sidebar.", icon="🚫")

                elif "parsing" in error_str:
                    # Handling for when the LLM output cannot be parsed by the Agent
                    st.error("🧩 Parsing Error. The model response could not be interpreted. Please try again.", icon="😵‍💫")

                elif "operationalerror" in error_str:
                    # Handling for SQL syntax errors or database locking issues
                    st.error("🛠️ Database Error. The generated SQL query failed to execute.", icon="📉")

                else:
                    # Handle any other unexpected runtime errors
                    error_msg = f"❌ An error occurred: {str(e)}"
                    st.error(error_msg, icon="🚨")