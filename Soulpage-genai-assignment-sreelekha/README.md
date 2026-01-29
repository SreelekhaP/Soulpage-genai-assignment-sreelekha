# 🏢 Company Intelligence Multi-Agent System

A production-ready multi-agent AI system built with **LangGraph** and **LangChain** that performs comprehensive company analysis using collaborative AI agents.

## 🎯 Project Overview

This system demonstrates advanced agentic AI workflows where multiple specialized agents collaborate to gather data, analyze information, and generate investment insights.

### **Key Features:**
- ✅ **LangGraph State Machine**: Proper orchestration with state management
- ✅ **LangChain Agents**: Real agents with tool usage and LLM reasoning
- ✅ **Real Data Collection**: Live stock prices (yfinance) and news (web scraping)
- ✅ **Memory & Context**: Shared state between agents for coherent analysis
- ✅ **Streamlit UI**: Interactive web interface
- ✅ **No API Keys Required** (except OpenAI for LLM)

---

## 🏗️ Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                               │
│                   (Company Ticker: AAPL)                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   LANGGRAPH ORCHESTRATOR                         │
│                    (State Management)                            │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Shared State:                                           │   │
│  │  • company_name                                          │   │
│  │  • news_articles                                         │   │
│  │  • stock_price, market_cap                              │   │
│  │  • summary, insights, risks                             │   │
│  │  • messages (conversation history)                      │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────────────┬───────────────────┬─────────────────────┘
                        │                   │
        ┌───────────────┘                   └───────────────┐
        ▼                                                     ▼
┌──────────────────────┐                         ┌──────────────────────┐
│   AGENT 1:           │                         │   AGENT 2:           │
│   DATA COLLECTOR     │────────Data Flow───────▶│   ANALYST            │
│                      │                         │                      │
│  LangChain ReAct     │                         │  LangChain GPT-4     │
│  Agent with Tools:   │                         │  with Reasoning:     │
│                      │                         │                      │
│  🔧 Tools:           │                         │  🧠 Analysis:        │
│  • fetch_stock_data  │                         │  • Executive Summary │
│  • fetch_news        │                         │  • Key Insights      │
│  • calc_metrics      │                         │  • Risk Assessment   │
│                      │                         │  • Recommendation    │
│  📡 Data Sources:    │                         │                      │
│  • yfinance API      │                         │  📊 Output:          │
│  • Google News RSS   │                         │  • Structured JSON   │
│  • Yahoo Finance     │                         │  • Investment Report │
│  • Web Scraping      │                         │                      │
└──────────────────────┘                         └──────────────────────┘
        │                                                     │
        └───────────────────┐               ┐───────────────┘
                            ▼               ▼
                    ┌────────────────────────────┐
                    │    FINAL OUTPUT            │
                    │  • Stock Data              │
                    │  • News Articles           │
                    │  • Analysis Report         │
                    │  • Recommendation          │
                    └────────────────────────────┘
                                │
                                ▼
                    ┌────────────────────────────┐
                    │    STREAMLIT UI            │
                    │  • Interactive Display     │
                    │  • History Tracking        │
                    │  • Professional Report     │
                    └────────────────────────────┘
```

### Workflow Sequence

```
1. User Input → "AAPL"
2. Orchestrator creates initial state
3. LangGraph routes to Data Collector Agent
4. Agent 1 uses tools to fetch:
   - Stock price from yfinance
   - News from Google News RSS
   - Financial metrics
5. Agent 1 updates shared state
6. LangGraph routes to Analyst Agent
7. Agent 2 receives data from state
8. Agent 2 uses GPT-4 to:
   - Analyze trends
   - Generate insights
   - Assess risks
   - Create recommendation
9. Agent 2 updates state with analysis
10. Orchestrator returns final state
11. Streamlit displays results
```

---

## 📁 Project Structure

```
Soulpage-genai-assignment-sreelekha/
│
├── agents/
│   ├── __init__.py
│   ├── data_collector.py       # Agent 1: LangChain agent with tools
│   └── analyst.py              # Agent 2: LangChain analyst with LLM
│
├── orchestrator.py             # LangGraph state machine
├── app.py                      # Streamlit UI
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── README.md                   # This file
│
├── notebooks/
│   └── demo.ipynb             # Jupyter notebook for testing
│
└── docs/
    └── architecture.png        # Architecture diagram
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- OpenAI API key (for LLM reasoning)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/SreelekhaP/Soulpage-genai-assignment-sreelekha.git
cd Soulpage-genai-assignment-sreelekha
```

2. **Create virtual environment**
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Create .env file
cp .env.example .env

# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=sk-your-key-here
```

### Running the Application

#### Option 1: Streamlit UI (Recommended)
```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

#### Option 2: Python Script
```python
from orchestrator import orchestrator

# Run analysis
result = orchestrator("AAPL")

print(result['analysis']['summary'])
print(result['analysis']['recommendation'])
```

#### Option 3: Jupyter Notebook
```bash
jupyter notebook notebooks/demo.ipynb
```

---

## 💡 Usage Examples

### Basic Analysis
```python
from orchestrator import orchestrator

# Analyze Apple
result = orchestrator("AAPL")

# Access results
print(f"Stock Price: ${result['stock_data']['price']}")
print(f"Recommendation: {result['analysis']['recommendation']}")
```

### With Streamlit
1. Enter company ticker (e.g., AAPL, TSLA, MSFT)
2. Click "RUN FULL ANALYSIS"
3. View comprehensive report with:
   - Real-time stock data
   - Recent news articles
   - AI-generated insights
   - Risk assessment
   - Investment recommendation

---

## 🔧 Technical Details

### LangGraph Implementation

The orchestrator uses LangGraph's `StateGraph` to manage agent workflows:

```python
from langgraph.graph import StateGraph, END

# Define shared state
class CompanyIntelligenceState(TypedDict):
    company_name: str
    news_articles: list
    stock_price: float
    summary: str
    insights: list
    # ... more fields

# Create workflow
workflow = StateGraph(CompanyIntelligenceState)
workflow.add_node("data_collector", data_collector_node)
workflow.add_node("analyst", analyst_node)
workflow.add_edge("data_collector", "analyst")
workflow.add_edge("analyst", END)
```

### LangChain Agents

**Agent 1** uses LangChain's ReAct agent pattern:
```python
from langchain.agents import create_react_agent, AgentExecutor

agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)
```

**Agent 2** uses structured output with Pydantic:
```python
from langchain.output_parsers import PydanticOutputParser

parser = PydanticOutputParser(pydantic_object=FinancialAnalysis)
response = llm.invoke(prompt)
analysis = parser.parse(response.content)
```

### Tools (No API Keys Required!)

1. **Stock Data**: `yfinance` library (free, no key needed)
2. **News**: Google News RSS + web scraping (free)
3. **Backup**: Yahoo Finance news API (free)

---

## 📊 Sample Output

```
Company: AAPL
Stock Price: $185.50 (+2.3%)
Market Cap: $2.9T

Executive Summary:
Apple demonstrates strong momentum with recent price gains...

Key Insights:
• Strong quarterly earnings beat expectations
• AI features driving investor confidence
• Market cap solidly above $2.5T

Risk Factors:
• Regulatory scrutiny in EU markets
• Competition in smartphone segment
• Supply chain dependencies

Recommendation: BUY
Confidence: HIGH
Rationale: Positive fundamentals with manageable risks...
```

---

## 🎓 Key Learning Outcomes

This project demonstrates:

1. ✅ **LangGraph State Management**: Proper state machine implementation
2. ✅ **Multi-Agent Orchestration**: Coordinating specialized agents
3. ✅ **Tool Integration**: Real-world API and web scraping
4. ✅ **LangChain Agents**: ReAct pattern with tools
5. ✅ **Structured Outputs**: Using Pydantic for reliable parsing
6. ✅ **Context Preservation**: Shared state and memory
7. ✅ **Production UI**: Professional Streamlit interface

---

## 🐛 Troubleshooting

### Common Issues

**1. "Module not found: langgraph"**
```bash
pip install langgraph langchain langchain-openai
```

**2. "No OpenAI API key"**
- Create `.env` file in project root
- Add: `OPENAI_API_KEY=sk-your-key-here`

**3. "Stock data fetch failed"**
- Check internet connection
- Verify ticker symbol is correct
- yfinance may have rate limits (wait a few seconds)

**4. "News fetch failed"**
- Google News RSS may be temporarily unavailable
- Falls back to Yahoo Finance automatically
- Check if ticker symbol exists

---

## 💰 Cost Estimate

- **OpenAI API**: ~$0.50-$2.00 for typical testing
  - Each analysis uses 2-3 API calls
  - GPT-4: ~$0.01-0.03 per call
- **Data APIs**: $0 (using free services)
- **Total per 100 analyses**: ~$2-5

### Cost Optimization
- Use GPT-3.5-turbo instead of GPT-4 (10x cheaper)
- Cache results for same company
- Batch multiple analyses

---

## 🚧 Future Enhancements

- [ ] Add more data sources (SEC filings, earnings calls)
- [ ] Implement sentiment analysis on news
- [ ] Add technical analysis indicators
- [ ] Support multiple companies comparison
- [ ] Add database for historical tracking
- [ ] Deploy to cloud (Streamlit Cloud, AWS, etc.)
- [ ] Add email/Slack notifications
- [ ] Implement streaming responses

---

## 📚 References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Agents Guide](https://python.langchain.com/docs/modules/agents/)
- [yfinance Documentation](https://pypi.org/project/yfinance/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

## 👤 Author

**Sreelekha P**
- GitHub: [@SreelekhaP](https://github.com/SreelekhaP)
- Project: Soulpage GenAI Assignment

---

## 📄 License

This project is created for educational purposes as part of a technical assignment.

---

## 🙏 Acknowledgments

- LangChain team for the excellent framework
- OpenAI for GPT-4 API
- Streamlit for the UI framework
- yfinance contributors for free stock data

---

## ✅ Assignment Checklist

- [x] Two or more LangChain/LangGraph agents
- [x] Each agent has specific role and tool access
- [x] Orchestrator that triggers and combines responses
- [x] Context and memory between agent calls
- [x] Streamlit UI for interaction
- [x] GitHub repository with source code
- [x] README with architecture diagram
- [x] Setup and run instructions
- [x] Bonus: Jupyter notebook included

**Status: ✅ ALL REQUIREMENTS MET**
