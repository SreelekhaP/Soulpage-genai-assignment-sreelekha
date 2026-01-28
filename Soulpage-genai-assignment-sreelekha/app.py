import streamlit as st
import uuid
import random
from datetime import datetime

# =======================
# Page Config & CSS
# =======================
st.set_page_config(
    page_title="🏢 Company Intelligence System", 
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main-header {font-size: 2.8rem; color: #111827; text-align: center; margin: 2rem 0 1rem 0; font-weight: 700;}
.analysis-report {background: rgba(255,255,255,0.8); padding: 1.5rem; border-radius: 10px; border-left: 5px solid #1f77b4; margin: 1rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); color: #111827;}
.transparent-card {background: rgba(255,255,255,0.7); padding: 1.5rem; border-radius: 10px; border: 1px solid rgba(229,231,235,0.5); margin: 1rem 0; color: #111827;}
.gray-transparent {background: rgba(248,249,250,0.6); padding: 1.5rem; border-radius: 10px; border-left: 4px solid #6b7280; margin: 1rem 0; color: #111827;}
.section-title {font-size: 1.6rem; color: #111827; font-weight: 600; margin: 2rem 0 1rem 0;}
.footer-transparent {background: rgba(255,255,255,0.8); padding: 2rem; border-radius: 12px; border: 1px solid rgba(229,231,235,0.5); margin: 2rem 0;}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🏢 Company Intelligence System</h1>', unsafe_allow_html=True)
st.markdown("""
<div class="transparent-card">
    <strong style="color: #111827;">Multi-Agent AI System</strong> | 
    <em style="color: #374151;">Data Collector → Financial Analyst → Investment Report</em>
</div>
""", unsafe_allow_html=True)

# =======================
# Sidebar
# =======================
with st.sidebar:
    st.header("🤖 Agent Configuration")
    st.info("**Agent 1: Data Collector** 📡\n• Fetches dummy news & stock data")
    st.info("**Agent 2: Financial Analyst** 📊\n• Generates insights & recommendations")
    
    st.header("🏆 Supported Companies")
    supported = ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN"]
    for ticker in supported:
        st.success(f"✅ {ticker}")

# =======================
# Session State
# =======================
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# =======================
# INPUT
# =======================
st.markdown('<h2 class="section-title">🚀 Quick Analysis</h2>', unsafe_allow_html=True)
company = st.text_input(
    "📈 Enter Company Ticker", 
    value="AAPL",
    placeholder="AAPL, TSLA, AMZN, MSFT, GOOGL",
    help="Enter stock ticker symbol (e.g., AAPL for Apple)"
).upper()

# =======================
# Dummy Agents
# =======================
def data_collector_agent(company):
    """Simulate fetching news + stock price"""
    news = [
        f"{company} launches a new AI-powered product.",
        f"{company} stock rises {random.randint(1, 10)}% after quarterly earnings.",
        f"{company} faces regulatory review on new project."
    ]
    stock_price = round(random.uniform(100, 500), 2)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"news": news, "stock_price": stock_price, "timestamp": timestamp}

def financial_analyst_agent(data):
    """Simulate generating insights & risk factors"""
    summary = f"📊 Stock Price: ${data['stock_price']}\n"
    summary += "📰 News:\n" + "\n".join([f"- {n}" for n in data["news"]]) + "\n"
    insights = "💡 Insights: Positive growth trend observed.\n"
    risks = "⚠️ Risk Factors: Market volatility and competition may impact performance.\n"
    return summary + insights + risks

def orchestrator(company):
    """Orchestrates the two agents"""
    data = data_collector_agent(company)
    analysis = financial_analyst_agent(data)
    return analysis

# =======================
# RUN BUTTON
# =======================
if st.button("🔍 **RUN FULL ANALYSIS**", type="primary", use_container_width=True):
    if company:
        with st.spinner("🤖 Agents collaborating..."):
            report = orchestrator(company)
            st.success("🎉 **Analysis Complete!**")
            st.balloons()
            st.markdown(f'<div class="analysis-report">{report.replace("\n","<br>")}</div>', unsafe_allow_html=True)
            st.session_state.messages.append(report)
    else:
        st.warning("⚠️ Please enter a company ticker (e.g., AAPL)")

# =======================
# HISTORY
# =======================
st.markdown('<h2 class="section-title">📋 Analysis History</h2>', unsafe_allow_html=True)
if st.session_state.messages:
    for i, msg in enumerate(st.session_state.messages[-3:]):
        with st.expander(f"📈 Analysis #{len(st.session_state.messages)-i}"):
            st.markdown(f'<div class="analysis-report">{msg.replace("\n","<br>")}</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="transparent-card">👆 Run an analysis above to see history here!</div>', unsafe_allow_html=True)

# =======================
# FOOTER
# =======================
st.markdown("---")
st.markdown("""
<div class="footer-transparent" style="text-align: center;">
    <h3 style="color: #111827; margin-top: 0;">Multi-Agent LangGraph System</h3>
    <p style="color: #374151; font-size: 1.1rem; margin: 1rem 0;">
        Data Collector → Financial Analyst → Investment Intelligence<br>
        <strong style="color: #111827;">Built by SreelekhaP</strong>
    </p>
</div>
""", unsafe_allow_html=True)
