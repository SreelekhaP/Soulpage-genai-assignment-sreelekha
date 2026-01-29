"""
Proper LangGraph Orchestrator for Multi-Agent Company Intelligence System
This implements the required LangGraph state machine with proper memory and context
"""

from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
import os

# ============================================
# 1. DEFINE SHARED STATE (Required for LangGraph)
# ============================================
class CompanyIntelligenceState(TypedDict):
    """
    Shared state that flows between agents
    This maintains context and memory across the workflow
    """
    company_name: str
    # News data collected by Agent 1
    news_articles: Annotated[list, operator.add]
    # Stock data collected by Agent 1
    stock_price: float
    stock_change_percent: float
    market_cap: str
    # Analysis from Agent 2
    summary: str
    insights: list
    risk_factors: list
    recommendation: str
    # Conversation history for memory
    messages: Annotated[list, operator.add]
    # Workflow control
    next_step: str


# ============================================
# 2. AGENT 1: DATA COLLECTOR NODE
# ============================================
def data_collector_node(state: CompanyIntelligenceState) -> CompanyIntelligenceState:
    """
    Agent 1: Data Collector
    - Fetches company news using web scraping/APIs
    - Fetches stock data using yfinance
    - Uses LLM to decide what data to collect
    """
    from agents.data_collector import fetch_stock_data, fetch_company_news
    
    company = state["company_name"]
    
    print(f"🔍 Agent 1 (Data Collector): Gathering data for {company}...")
    
    # Initialize LLM for decision making
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # LLM decides what data sources to prioritize
    decision_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a data collection strategist. Given a company name, decide what data sources are most important."),
        ("human", "What data should I collect for {company}? Respond with: news, stock, financials, or all")
    ])
    
    decision = llm.invoke(decision_prompt.format_messages(company=company))
    
    # Fetch actual data using tools
    try:
        stock_data = fetch_stock_data(company)
        news_data = fetch_company_news(company)
        
        # Update state with collected data
        state["stock_price"] = stock_data.get("current_price", 0)
        state["stock_change_percent"] = stock_data.get("change_percent", 0)
        state["market_cap"] = stock_data.get("market_cap", "N/A")
        state["news_articles"] = news_data  # Uses operator.add to append
        
        # Add to conversation memory
        state["messages"] = [
            HumanMessage(content=f"Collect data for {company}"),
            SystemMessage(content=f"Collected {len(news_data)} news articles and stock data")
        ]
        
        state["next_step"] = "analyst"
        
        print(f"✅ Data collected: {len(news_data)} articles, Stock: ${state['stock_price']}")
        
    except Exception as e:
        print(f"❌ Error in data collection: {e}")
        state["next_step"] = "error"
    
    return state


# ============================================
# 3. AGENT 2: FINANCIAL ANALYST NODE
# ============================================
def analyst_node(state: CompanyIntelligenceState) -> CompanyIntelligenceState:
    """
    Agent 2: Financial Analyst
    - Analyzes data collected by Agent 1
    - Generates insights using LLM reasoning
    - Produces risk assessment and recommendations
    """
    print(f"📊 Agent 2 (Financial Analyst): Analyzing data for {state['company_name']}...")
    
    # Initialize LLM for analysis
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.3,  # Slightly higher for creative insights
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Create comprehensive analysis prompt
    analysis_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a senior financial analyst. Analyze the provided company data and generate:
        1. Executive Summary (2-3 sentences)
        2. Key Insights (3-5 bullet points)
        3. Risk Factors (3-5 bullet points)
        4. Investment Recommendation (Buy/Hold/Sell with justification)
        
        Be specific, data-driven, and professional."""),
        ("human", """Company: {company}
        
Stock Data:
- Current Price: ${price}
- Change: {change}%
- Market Cap: {market_cap}

Recent News:
{news}

Provide your comprehensive analysis.""")
    ])
    
    # Format news for prompt
    news_summary = "\n".join([f"- {article}" for article in state["news_articles"][:5]])
    
    # Get LLM analysis
    try:
        response = llm.invoke(analysis_prompt.format_messages(
            company=state["company_name"],
            price=state["stock_price"],
            change=state["stock_change_percent"],
            market_cap=state["market_cap"],
            news=news_summary
        ))
        
        analysis_text = response.content
        
        # Parse LLM response (simplified - you can use structured output)
        state["summary"] = analysis_text.split("Executive Summary:")[-1].split("Key Insights:")[0].strip()
        
        # Extract insights (simplified parsing)
        insights_section = analysis_text.split("Key Insights:")[-1].split("Risk Factors:")[0]
        state["insights"] = [line.strip() for line in insights_section.split("\n") if line.strip().startswith("-")]
        
        # Extract risks
        risks_section = analysis_text.split("Risk Factors:")[-1].split("Investment Recommendation:")[0]
        state["risk_factors"] = [line.strip() for line in risks_section.split("\n") if line.strip().startswith("-")]
        
        # Extract recommendation
        state["recommendation"] = analysis_text.split("Investment Recommendation:")[-1].strip()
        
        # Add to conversation memory
        state["messages"] = [
            SystemMessage(content=f"Analysis complete for {state['company_name']}")
        ]
        
        state["next_step"] = "end"
        
        print(f"✅ Analysis complete: {state['recommendation'][:50]}...")
        
    except Exception as e:
        print(f"❌ Error in analysis: {e}")
        state["summary"] = f"Error analyzing data: {e}"
        state["next_step"] = "error"
    
    return state


# ============================================
# 4. BUILD LANGGRAPH WORKFLOW
# ============================================
def create_workflow() -> StateGraph:
    """
    Creates the LangGraph state machine that orchestrates agents
    This is the required LangGraph implementation
    """
    # Initialize the graph with our state schema
    workflow = StateGraph(CompanyIntelligenceState)
    
    # Add agent nodes
    workflow.add_node("data_collector", data_collector_node)
    workflow.add_node("analyst", analyst_node)
    
    # Define the flow
    workflow.set_entry_point("data_collector")  # Start with data collection
    workflow.add_edge("data_collector", "analyst")  # Then analyze
    workflow.add_edge("analyst", END)  # Then finish
    
    # Compile the graph
    app = workflow.compile()
    
    return app


# ============================================
# 5. ORCHESTRATOR FUNCTION (Main Entry Point)
# ============================================
def orchestrator(company_name: str) -> dict:
    """
    Main orchestrator that runs the LangGraph workflow
    
    Args:
        company_name: Stock ticker or company name (e.g., "AAPL", "Apple")
    
    Returns:
        dict: Complete analysis results with all agent outputs
    """
    print(f"\n{'='*60}")
    print(f"🚀 Starting Multi-Agent Analysis for: {company_name}")
    print(f"{'='*60}\n")
    
    # Create the LangGraph workflow
    app = create_workflow()
    
    # Initialize state
    initial_state = {
        "company_name": company_name.upper(),
        "news_articles": [],
        "stock_price": 0.0,
        "stock_change_percent": 0.0,
        "market_cap": "",
        "summary": "",
        "insights": [],
        "risk_factors": [],
        "recommendation": "",
        "messages": [],
        "next_step": "data_collector"
    }
    
    # Run the workflow (LangGraph executes the state machine)
    try:
        final_state = app.invoke(initial_state)
        
        print(f"\n{'='*60}")
        print(f"✅ Analysis Complete!")
        print(f"{'='*60}\n")
        
        # Return structured results
        return {
            "company": final_state["company_name"],
            "stock_data": {
                "price": final_state["stock_price"],
                "change": final_state["stock_change_percent"],
                "market_cap": final_state["market_cap"]
            },
            "news": final_state["news_articles"],
            "analysis": {
                "summary": final_state["summary"],
                "insights": final_state["insights"],
                "risks": final_state["risk_factors"],
                "recommendation": final_state["recommendation"]
            },
            "conversation_history": final_state["messages"]
        }
        
    except Exception as e:
        print(f"❌ Workflow error: {e}")
        return {
            "error": str(e),
            "company": company_name
        }


# ============================================
# 6. TESTING / MAIN
# ============================================
if __name__ == "__main__":
    # Test the orchestrator
    result = orchestrator("AAPL")
    
    print("\n" + "="*60)
    print("FINAL RESULTS:")
    print("="*60)
    print(f"\nCompany: {result['company']}")
    print(f"Stock Price: ${result['stock_data']['price']}")
    print(f"\nSummary: {result['analysis']['summary']}")
    print(f"\nRecommendation: {result['analysis']['recommendation']}")
