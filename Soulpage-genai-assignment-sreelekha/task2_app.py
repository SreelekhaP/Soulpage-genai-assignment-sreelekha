import streamlit as st
from langchain.agents import Tool, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun

# ========================
# Page Config
# ========================
st.set_page_config(
    page_title="🤖 Conversational Knowledge Bot",
    page_icon="💬",
    layout="wide"
)

st.title("🤖 Conversational Knowledge Bot")

# ========================
# Memory
# ========================
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# ========================
# Static Knowledge Base
# ========================
knowledge_base = {
    "who is the ceo of openai": "The CEO of OpenAI is Sam Altman.",
    "when was python created": "Python was created in 1991 by Guido van Rossum.",
    "what is langchain": "LangChain is a framework for building applications with LLMs using agents and memory."
}

def query_knowledge_base(question: str):
    return knowledge_base.get(question.lower().strip("?"), None)

# ========================
# DuckDuckGo Search Tool
# ========================
search_tool = Tool(
    name="DuckDuckGo Search",
    func=DuckDuckGoSearchRun().run,
    description="Search the web for factual information."
)

# ========================
# Conversational Agent
# ========================
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

chat_agent = initialize_agent(
    tools=[search_tool],
    llm=llm,
    agent="conversational-react-description",
    memory=memory,
    verbose=False
)

# ========================
# Session State
# ========================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ========================
# User Input
# ========================
user_input = st.text_input("Ask a question:", placeholder="Type your question here...")

if st.button("Send"):
    if user_input:
        # Save user message
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Step 1: Check static knowledge base
        answer = query_knowledge_base(user_input)

        # Step 2: If not found, use agent
        if not answer:
            with st.spinner("🤖 Searching..."):
                answer = chat_agent.run(user_input)

        # Save bot response
        st.session_state.messages.append({"role": "bot", "content": answer})

# ========================
# Display Conversation
# ========================
st.subheader("Conversation History")
for msg in st.session_state.messages[-10:]:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Bot:** {msg['content']}")
