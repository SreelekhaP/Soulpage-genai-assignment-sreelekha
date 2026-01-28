from langchain.agents import Tool, initialize_agent
from langchain.memory import ConversationBufferMemory

# Memory for analyst
analyst_memory = ConversationBufferMemory(memory_key="analyst_memory", return_messages=True)

# Tool to analyze company data
def analyze_company_data(data):
    news = data.get("news", [])
    stock_price = data.get("stock_price", 0)
    summary = f"Company: {data.get('company')}\nStock Price: ${stock_price}\nNews:\n"
    for n in news:
        summary += f"- {n}\n"
    insights = "Insights: Company shows positive growth trend.\n"
    risks = "Risk Factors: Market volatility and competition.\n"
    return summary + insights + risks

analyst_tool = Tool(
    name="Analyze Company Data",
    func=analyze_company_data,
    description="Analyzes company news and stock price to generate insights and risk factors."
)

# Initialize Analyst Agent
analyst_agent = initialize_agent(
    tools=[analyst_tool],
    llm=None,  # Offline logic
    agent="conversational-react-description",
    memory=analyst_memory,
    verbose=True
)
