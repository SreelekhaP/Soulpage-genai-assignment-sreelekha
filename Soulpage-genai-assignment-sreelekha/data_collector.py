from langchain.agents import Tool, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI  # Optional if you want LLM later
from utils.dummy_data import fetch_company_data

# Memory for the agent
data_collector_memory = ConversationBufferMemory(memory_key="data_collector_memory", return_messages=True)

# Tool to fetch company data
data_collector_tool = Tool(
    name="Fetch Company Data",
    func=fetch_company_data,
    description="Fetches latest company news and stock price for a given company."
)

# Initialize DataCollector Agent
data_collector_agent = initialize_agent(
    tools=[data_collector_tool],
    llm=None,  # Use None for offline logic or ChatOpenAI for LLM
    agent="conversational-react-description",
    memory=data_collector_memory,
    verbose=True
)
