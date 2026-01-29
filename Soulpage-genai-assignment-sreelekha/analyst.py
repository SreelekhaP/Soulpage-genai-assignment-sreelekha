"""
Financial Analyst Agent with LLM Reasoning
Uses LangChain for structured analysis and insights generation
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
import os


# ============================================
# STRUCTURED OUTPUT SCHEMA
# ============================================
class FinancialAnalysis(BaseModel):
    """Structured output for financial analysis"""
    executive_summary: str = Field(description="2-3 sentence overview of the company's current state")
    key_insights: List[str] = Field(description="3-5 data-driven insights about the company")
    risk_factors: List[str] = Field(description="3-5 potential risks or concerns")
    opportunities: List[str] = Field(description="2-3 growth opportunities or positive signals")
    recommendation: str = Field(description="Investment recommendation: BUY, HOLD, or SELL with justification")
    confidence_level: str = Field(description="Confidence in recommendation: HIGH, MEDIUM, or LOW")


# ============================================
# FINANCIAL ANALYST AGENT
# ============================================
class FinancialAnalystAgent:
    """
    LangChain-powered financial analyst that provides comprehensive analysis
    Uses GPT-4 for deep reasoning and structured output
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,  # Balanced for analytical yet creative insights
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Setup output parser for structured results
        self.output_parser = PydanticOutputParser(pydantic_object=FinancialAnalysis)
        
        # Create analysis prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a senior financial analyst with 15+ years of experience in equity research. 
            You provide data-driven, objective analysis based on:
            - Stock price trends and momentum
            - Recent news sentiment and impact
            - Financial metrics and ratios
            - Market conditions and sector trends
            
            Your analysis should be:
            - Specific and actionable
            - Balanced (acknowledge both positives and negatives)
            - Data-driven (reference actual numbers)
            - Professional and clear
            
            {format_instructions}"""),
            
            ("human", """Analyze the following company data and provide a comprehensive investment analysis:

COMPANY: {company}

STOCK DATA:
- Current Price: ${current_price}
- Price Change: {price_change}%
- Market Cap: {market_cap}
- P/E Ratio: {pe_ratio}
- 52-Week High: ${week_high}
- 52-Week Low: ${week_low}

RECENT NEWS:
{news_summary}

FINANCIAL METRICS:
{financial_metrics}

Provide your detailed analysis following the specified format.""")
        ])
    
    def run(self, company_data: dict) -> dict:
        """
        Analyzes company data and generates insights
        
        Args:
            company_data: Dictionary containing stock data, news, and metrics
        
        Returns:
            dict: Structured analysis with insights and recommendations
        """
        try:
            # Extract data from input
            company = company_data.get("company", "Unknown")
            stock_data = company_data.get("stock_data", {})
            news = company_data.get("news", [])
            
            # Format news summary
            news_summary = self._format_news(news)
            
            # Format financial metrics
            financial_metrics = self._format_metrics(stock_data)
            
            # Create prompt with format instructions
            format_instructions = self.output_parser.get_format_instructions()
            
            # Generate analysis using LLM
            messages = self.prompt.format_messages(
                company=company,
                current_price=stock_data.get("current_price", "N/A"),
                price_change=stock_data.get("change_percent", "N/A"),
                market_cap=self._format_market_cap(stock_data.get("market_cap", "N/A")),
                pe_ratio=stock_data.get("pe_ratio", "N/A"),
                week_high=stock_data.get("fifty_two_week_high", "N/A"),
                week_low=stock_data.get("fifty_two_week_low", "N/A"),
                news_summary=news_summary,
                financial_metrics=financial_metrics,
                format_instructions=format_instructions
            )
            
            # Get LLM response
            response = self.llm.invoke(messages)
            
            # Parse structured output
            try:
                analysis = self.output_parser.parse(response.content)
                
                return {
                    "company": company,
                    "summary": analysis.executive_summary,
                    "insights": analysis.key_insights,
                    "risks": analysis.risk_factors,
                    "opportunities": analysis.opportunities,
                    "recommendation": analysis.recommendation,
                    "confidence": analysis.confidence_level,
                    "raw_analysis": response.content
                }
            except:
                # Fallback if parsing fails
                return self._parse_fallback(response.content, company)
                
        except Exception as e:
            print(f"❌ Analyst error: {e}")
            return {
                "company": company_data.get("company", "Unknown"),
                "error": str(e),
                "summary": "Analysis failed due to an error.",
                "insights": [],
                "risks": [],
                "recommendation": "Unable to provide recommendation"
            }
    
    def _format_news(self, news: list) -> str:
        """Formats news articles for the prompt"""
        if not news or len(news) == 0:
            return "No recent news available."
        
        formatted = []
        for i, article in enumerate(news[:5], 1):
            title = article.get("title", "No title")
            date = article.get("published", "Unknown date")
            formatted.append(f"{i}. [{date}] {title}")
        
        return "\n".join(formatted)
    
    def _format_metrics(self, stock_data: dict) -> str:
        """Formats financial metrics for the prompt"""
        metrics = []
        
        if "volume" in stock_data:
            metrics.append(f"- Trading Volume: {stock_data['volume']:,}")
        if "pe_ratio" in stock_data and stock_data["pe_ratio"] != "N/A":
            metrics.append(f"- P/E Ratio: {stock_data['pe_ratio']}")
        
        return "\n".join(metrics) if metrics else "Limited financial metrics available."
    
    def _format_market_cap(self, market_cap) -> str:
        """Formats market cap for readability"""
        if isinstance(market_cap, (int, float)):
            if market_cap >= 1_000_000_000_000:
                return f"{market_cap / 1_000_000_000_000:.2f}T"
            elif market_cap >= 1_000_000_000:
                return f"{market_cap / 1_000_000_000:.2f}B"
            elif market_cap >= 1_000_000:
                return f"{market_cap / 1_000_000:.2f}M"
        return str(market_cap)
    
    def _parse_fallback(self, content: str, company: str) -> dict:
        """Fallback parser if structured parsing fails"""
        return {
            "company": company,
            "summary": content[:500],  # First 500 chars as summary
            "insights": self._extract_bullet_points(content, "insights"),
            "risks": self._extract_bullet_points(content, "risk"),
            "opportunities": self._extract_bullet_points(content, "opportunit"),
            "recommendation": self._extract_recommendation(content),
            "confidence": "MEDIUM",
            "raw_analysis": content
        }
    
    def _extract_bullet_points(self, text: str, keyword: str) -> list:
        """Extracts bullet points from text based on keyword"""
        lines = text.lower().split('\n')
        points = []
        
        capture = False
        for line in lines:
            if keyword in line:
                capture = True
                continue
            if capture and (line.strip().startswith('-') or line.strip().startswith('•')):
                points.append(line.strip().lstrip('-•').strip())
            elif capture and line.strip() and not line.strip().startswith('-'):
                capture = False
        
        return points[:5]  # Max 5 points
    
    def _extract_recommendation(self, text: str) -> str:
        """Extracts recommendation from text"""
        text_lower = text.lower()
        
        if 'buy' in text_lower and 'sell' not in text_lower:
            return "BUY - Based on positive indicators in the analysis"
        elif 'sell' in text_lower:
            return "SELL - Based on risk factors identified"
        else:
            return "HOLD - Mixed signals, recommend monitoring"


# Create singleton instance
analyst_agent = FinancialAnalystAgent()


# ============================================
# Alternative: Simple Analysis (No Structured Output)
# ============================================
def simple_analyst_agent(company_data: dict) -> dict:
    """
    Simpler version that doesn't require structured output parsing
    Good fallback if Pydantic parsing fails
    """
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.3,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a financial analyst. Provide clear, actionable investment analysis."),
        ("human", """Analyze this company data:

Company: {company}
Stock Price: ${price} (Change: {change}%)
Market Cap: {market_cap}

Recent News:
{news}

Provide:
1. Executive Summary (2-3 sentences)
2. Key Insights (3-5 points)
3. Risk Factors (3-5 points)
4. Recommendation (BUY/HOLD/SELL with justification)

Format each section clearly.""")
    ])
    
    company = company_data.get("company", "Unknown")
    stock_data = company_data.get("stock_data", {})
    news = company_data.get("news", [])
    
    news_text = "\n".join([f"- {n.get('title', '')}" for n in news[:3]])
    
    messages = prompt.format_messages(
        company=company,
        price=stock_data.get("current_price", "N/A"),
        change=stock_data.get("change_percent", "N/A"),
        market_cap=stock_data.get("market_cap", "N/A"),
        news=news_text or "No recent news"
    )
    
    response = llm.invoke(messages)
    
    return {
        "company": company,
        "analysis": response.content,
        "timestamp": stock_data.get("timestamp", "N/A")
    }


# ============================================
# Testing
# ============================================
if __name__ == "__main__":
    print("Testing Financial Analyst Agent...")
    print("="*60)
    
    # Mock data for testing
    test_data = {
        "company": "AAPL",
        "stock_data": {
            "current_price": 185.50,
            "change_percent": 2.3,
            "market_cap": 2_900_000_000_000,
            "pe_ratio": 29.5,
            "fifty_two_week_high": 199.62,
            "fifty_two_week_low": 164.08
        },
        "news": [
            {"title": "Apple announces new AI features", "published": "2024-01-28"},
            {"title": "AAPL stock rises on strong earnings", "published": "2024-01-27"}
        ]
    }
    
    result = analyst_agent.run(test_data)
    
    print("\n📊 Analysis Results:")
    print(f"Summary: {result['summary']}")
    print(f"\n💡 Insights: {result['insights']}")
    print(f"\n⚠️ Risks: {result['risks']}")
    print(f"\n📈 Recommendation: {result['recommendation']}")
    
    print("\n✅ Analyst test complete!")
