"""
Data Collector Agent with Real Tools
Uses LangChain tools for fetching stock data and news
"""

from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os


# ============================================
# TOOL 1: Stock Data Fetcher (Real API - No Key Needed!)
# ============================================
@tool
def fetch_stock_data(ticker: str) -> dict:
    """
    Fetches real-time stock data for a given ticker using yfinance.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
    
    Returns:
        dict: Stock price, change, market cap, and other metrics
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        previous_close = info.get('previousClose', current_price)
        
        if previous_close and previous_close > 0:
            change_percent = ((current_price - previous_close) / previous_close) * 100
        else:
            change_percent = 0
        
        return {
            "ticker": ticker,
            "current_price": round(current_price, 2),
            "change_percent": round(change_percent, 2),
            "market_cap": info.get('marketCap', 'N/A'),
            "volume": info.get('volume', 'N/A'),
            "pe_ratio": info.get('trailingPE', 'N/A'),
            "fifty_two_week_high": info.get('fiftyTwoWeekHigh', 'N/A'),
            "fifty_two_week_low": info.get('fiftyTwoWeekLow', 'N/A'),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {
            "ticker": ticker,
            "error": f"Failed to fetch stock data: {str(e)}",
            "current_price": 0,
            "change_percent": 0
        }


# ============================================
# TOOL 2: News Scraper (Real Web Scraping - No Key Needed!)
# ============================================
@tool
def fetch_company_news(company: str, max_articles: int = 5) -> list:
    """
    Fetches recent news articles about a company using web scraping.
    
    Args:
        company: Company name or ticker
        max_articles: Maximum number of articles to return
    
    Returns:
        list: Recent news headlines and summaries
    """
    try:
        # Method 1: Google News RSS (No API key needed)
        url = f"https://news.google.com/rss/search?q={company}+stock&hl=en-US&gl=US&ceid=US:en"
        
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'xml')
        
        articles = []
        for item in soup.find_all('item')[:max_articles]:
            title = item.title.text if item.title else "No title"
            pub_date = item.pubDate.text if item.pubDate else "Unknown date"
            link = item.link.text if item.link else ""
            
            articles.append({
                "title": title,
                "published": pub_date,
                "url": link
            })
        
        # If Google News fails, try Yahoo Finance
        if not articles:
            articles = fetch_yahoo_news(company, max_articles)
        
        return articles if articles else [{"title": f"No recent news found for {company}", "published": "N/A"}]
        
    except Exception as e:
        return [{"title": f"Error fetching news: {str(e)}", "published": "N/A"}]


def fetch_yahoo_news(ticker: str, max_articles: int = 5) -> list:
    """Backup news fetcher using Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)
        news = stock.news[:max_articles]
        
        articles = []
        for item in news:
            articles.append({
                "title": item.get('title', 'No title'),
                "published": datetime.fromtimestamp(item.get('providerPublishTime', 0)).strftime("%Y-%m-%d"),
                "url": item.get('link', '')
            })
        
        return articles
    except:
        return []


# ============================================
# TOOL 3: Financial Metrics Calculator
# ============================================
@tool
def calculate_financial_metrics(ticker: str) -> dict:
    """
    Calculates key financial metrics and ratios.
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        dict: Financial metrics like P/E ratio, debt-to-equity, etc.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return {
            "pe_ratio": info.get('trailingPE', 'N/A'),
            "forward_pe": info.get('forwardPE', 'N/A'),
            "peg_ratio": info.get('pegRatio', 'N/A'),
            "price_to_book": info.get('priceToBook', 'N/A'),
            "debt_to_equity": info.get('debtToEquity', 'N/A'),
            "return_on_equity": info.get('returnOnEquity', 'N/A'),
            "revenue_growth": info.get('revenueGrowth', 'N/A')
        }
    except Exception as e:
        return {"error": str(e)}


# ============================================
# LANGCHAIN AGENT: Data Collector
# ============================================
def create_data_collector_agent():
    """
    Creates a LangChain ReAct agent with data collection tools
    This is the proper LangChain agent implementation
    """
    # Initialize LLM
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Define tools available to this agent
    tools = [
        fetch_stock_data,
        fetch_company_news,
        calculate_financial_metrics
    ]
    
    # Create ReAct agent prompt
    template = """You are a financial data collection specialist. Your job is to gather comprehensive data about companies.

You have access to the following tools:
{tools}

Tool Names: {tool_names}

When given a company ticker or name:
1. First, fetch the current stock data
2. Then, gather recent news articles
3. Finally, calculate financial metrics

Use this format:
Question: the input question you must answer
Thought: think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Question: {input}
{agent_scratchpad}"""
    
    prompt = PromptTemplate.from_template(template)
    
    # Create the agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )
    
    return agent_executor


# ============================================
# Simple Interface (for backwards compatibility)
# ============================================
class DataCollectorAgent:
    """Wrapper class for the LangChain agent"""
    
    def __init__(self):
        self.agent = create_data_collector_agent()
    
    def run(self, company_name: str) -> dict:
        """
        Runs the data collection agent
        
        Args:
            company_name: Company ticker or name
        
        Returns:
            dict: Collected data
        """
        try:
            # Run the LangChain agent
            result = self.agent.invoke({
                "input": f"Collect comprehensive data for {company_name}. Get stock price, news, and financial metrics."
            })
            
            # Also get raw data for guaranteed results
            stock_data = fetch_stock_data.invoke(company_name)
            news_data = fetch_company_news.invoke(company_name)
            
            return {
                "company": company_name,
                "stock_data": stock_data,
                "news": news_data,
                "agent_analysis": result.get("output", "")
            }
            
        except Exception as e:
            # Fallback to direct tool calls if agent fails
            print(f"Agent failed, using direct tools: {e}")
            return {
                "company": company_name,
                "stock_data": fetch_stock_data.invoke(company_name),
                "news": fetch_company_news.invoke(company_name),
                "error": str(e)
            }


# Create singleton instance
data_collector_agent = DataCollectorAgent()


# ============================================
# Testing
# ============================================
if __name__ == "__main__":
    print("Testing Data Collector Agent...")
    print("="*60)
    
    # Test with Apple
    result = data_collector_agent.run("AAPL")
    
    print("\n📊 Stock Data:")
    print(result["stock_data"])
    
    print("\n📰 News:")
    for article in result["news"][:3]:
        print(f"  - {article['title']}")
    
    print("\n✅ Agent test complete!")
