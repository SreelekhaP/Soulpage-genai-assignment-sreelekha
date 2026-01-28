from agents.data_collector import data_collector_agent
from agents.analyst import analyst_agent

def orchestrator(company_name):
    """Runs the multi-agent workflow"""
    # Step 1: Collect data
    company_data = data_collector_agent.run(company_name)
    
    # Step 2: Analyze data
    analysis = analyst_agent.run(company_data)
    
    return analysis
