import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities import ArxivAPIWrapper
from langchain.agents import initialize_agent, Tool, AgentType
from langchain_core.messages import SystemMessage
import PyPDF2 


load_dotenv()

# --- 1. LANGUAGE & API CONFIGURATION ---
with st.sidebar:
    st.header("Settings / הגדרות")
    lang = st.radio("Choose Language / בחר שפה:", ("Hebrew", "English"))
    
    st.divider()
    env_openai = os.getenv("OPENAI_API_KEY", "")
    env_tavily = os.getenv("TAVILY_API_KEY", "")
    
    OPENAI_KEY = st.text_input("OpenAI Key", type="password", value=env_openai)
    TAVILY_KEY = st.text_input("Tavily Key", type="password", value=env_tavily)


if not OPENAI_KEY or not TAVILY_KEY:
    st.warning("Please provide API keys in the sidebar or .env file to continue.")
    st.stop()

# Dynamic UI Text based on language selection
if lang == "Hebrew":
    title = "🔬 סוכן מחקר"
    topic_label = "נושא המחקר:"
    focus_label = "דגשים טכניים:"
    button_label = "התחל מחקר"
    spinner_msg = "...הסוכן סורק מקורות"
    direction = "RTL"
    align = "right"
else:
    title = "🔬 Research Agent"
    topic_label = "Research Topic:"
    focus_label = "Technical Focus:"
    button_label = "Start Research"
    spinner_msg = "Agent is researching..."
    direction = "LTR"
    align = "left"

# --- 2. UI & RTL/LTR SUPPORT ---
st.set_page_config(page_title="Research Agent", page_icon="🔬", layout="wide")

st.markdown(f"""
    <style>
    .stMarkdown, .stTextInput, .stTextArea {{
        direction: {direction};
        text-align: {align};
    }}
    h1, h2, h3 {{ text-align: {align}; }}
    </style>
    """, unsafe_allow_html=True)

st.title(title)

# --- 3. AI ENGINES (Shared) ---
llm = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=OPENAI_KEY)
search_engine = TavilySearchResults(max_results=5, tavily_api_key=TAVILY_KEY)
arxiv_engine = ArxivAPIWrapper(top_k_results=3, load_max_docs=3)

tools = [
    Tool(name="Internet_Search", func=search_engine.run, description="Web specs/news"),
    Tool(name="Academic_Search", func=arxiv_engine.run, description="arXiv papers")
]

# --- 4. USER INTERFACE ---
st.divider()
col1, col2 = st.columns([2, 1])

with col1:
    main_topic = st.text_input(topic_label, placeholder="e.g. ReRAM Reliability, GNN Scaling", key="topic_input")
    technical_focus = st.text_input(focus_label, placeholder="e.g. Sneak-path current, Memory wall", key="focus_input")

with col2:
    uploaded_file = st.file_uploader("Upload PDF / העלה קובץ PDF", type="pdf", help="Add a specific paper or datasheet to the research context")

st.divider()

# --- 5. EXECUTION LOGIC ---
if st.button(button_label):
    if main_topic:
        pdf_context = ""
        if uploaded_file is not None:
            try:
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                for i in range(min(len(pdf_reader.pages), 10)):
                    page_text = pdf_reader.pages[i].extract_text()
                    if page_text:
                        pdf_context += page_text + "\n"
                
                if pdf_context:
                    st.info("✅ PDF content integrated into research context.")
            except Exception as e:
                st.warning(f"Could not read PDF: {e}")

        if lang == "Hebrew":
            sys_msg = """You are a Senior Research Assistant.
            1. Language: Write the ENTIRE report in HEBREW (Right-to-Left).
            2. Technical Terms: Keep all technical terms and units in English.
            3. REFERENCES: You MUST include a 'References' section at the end with clickable URLs for all sources."""
            force_msg = SystemMessage(content="You MUST respond in HEBREW. Translate all findings but keep tech terms in English.")
            prompt_lang_instruction = "ענה בעברית בלבד."
        else:
            sys_msg = """You are a Senior Research Assistant.
            1. Language: Write the ENTIRE report in professional academic ENGLISH.
            2. REFERENCES: Include a 'References' section at the end with URLs."""
            force_msg = SystemMessage(content="You must respond in professional English.")
            prompt_lang_instruction = "Answer in English only."

        agent = initialize_agent(
            tools, 
            llm, 
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=15,
            agent_kwargs={"system_message": sys_msg}
        )
        
        pdf_prompt_addition = f"\n\nCONTEXT FROM UPLOADED PDF:\n{pdf_context[:4000]}" if pdf_context else ""
        
        prompt_content = f"""
        {prompt_lang_instruction}
        Research Topic: {main_topic}
        Technical Focus: {technical_focus}
        {pdf_prompt_addition}

        Task: Provide a professional review, research gap analysis, and a future proposal. 
        If a PDF context is provided, prioritize its technical data while complementing it with search results. 
        Include citations and references.
        """

        with st.status(spinner_msg, expanded=True) as status:
            try:
                result = agent.invoke({
                    "input": prompt_content,
                    "chat_history": [force_msg]
                })
                
                final_report = str(result["output"]) if isinstance(result, dict) and "output" in result else str(result)
                
                status.update(label="Done!" if lang=="English" else "!המחקר הושלם", state="complete", expanded=False)
                st.success("Success!" if lang=="English" else "הדו\"ח מוכן!")
                st.markdown(f'<div style="direction: {direction}; text-align: {align};">{final_report}</div>', unsafe_allow_html=True)
                
                st.download_button(
                    label="Download Report" if lang=="English" else "הורד דו\"ח",
                    data=final_report,
                    file_name=f"report_{main_topic.replace(' ', '_')}.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                status.update(label="Error", state="error")
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter a topic." if lang=="English" else ".נא להזין נושא")
