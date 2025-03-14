from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


import requests

# Fetch News from NewsAPI
def fetch_news(topic: str):
    API_KEY = os.getenv('NEWSAPI_KEY')  # 🔹 Replace with your actual NewsAPI key
    url = f"https://newsapi.org/v2/everything?q={topic}&sortBy=publishedAt&apiKey={API_KEY}"
    
    response = requests.get(url)
    data = response.json()
    
    if "articles" in data and len(data["articles"]) > 0:
        # Get the first news article
        article = data["articles"][0]
        return {
            "title": article["title"],
            "content": article["content"],
            "url": article["url"]
        }
    else:
        return {"title": "No news found", "content": "Try another topic.", "url": ""}


llm = ChatOllama(model="llama3",temperature=0.7)

class ResearchState(TypedDict):
    topic: str
    article: str
    summary: str
    sentiment: str
    fact_check: str
    final_report: str

graph = StateGraph(ResearchState)

# research agent
def research(state: ResearchState):
    news_data = fetch_news(state["topic"])
    
    return {
        "article": news_data["content"],
        "article_title": news_data["title"],
        "article_url": news_data["url"]
    }


# summary agent 
def summarize_article(state: ResearchState):
    response = llm.invoke(f"Summarize the article: {state['article']} ")
    return {"summary": response.content}

# sentiment analysis agent 
def analyze_sentiment(state: ResearchState):
    response = llm.invoke(f"Analyze the sentiment of the article {state['article']}")
    return {"sentiment": response.content}

# fact check the article
def fact_check(state: ResearchState):
    response = llm.invoke(f"Check if this article contains misinformation. Provide a fact-check summary: {state['article']}")
    return {"fact_check": response.content} 

# generate a report 
def generate_report(state: ResearchState):
    summary_prompt = f"""
    Topic: {state['topic']}
    Summary: {state['summary']}
    Sentiment: {state['sentiment']}
    Fact-check: {state['fact_check']}
    Provide a final research report
    """
    # generate a summary report 
    response = llm.invoke(summary_prompt)
    return {"final_report": response.content}

# create the graph by adding the nodes
graph.add_node("research",research)
graph.add_node("summarize_article",summarize_article)
graph.add_node("analyze_sentiment",analyze_sentiment)
graph.add_node("fact_checker", fact_check)
graph.add_node("generate_report",generate_report)

# graph execution
# layer 1
graph.add_edge(START,"research")
# layer 2
graph.add_edge("research","summarize_article")
graph.add_edge("research","analyze_sentiment")
graph.add_edge("research","fact_checker")
# layer 3
graph.add_edge("summarize_article", "generate_report")
graph.add_edge("analyze_sentiment", "generate_report")
graph.add_edge("fact_checker", "generate_report")
# layer 4
graph.add_edge("generate_report", END)

# compile
research_assistant = graph.compile()

# ✅ Compile and Get the Graph Structure
compiled_graph = research_assistant.get_graph()

# ✅ Print Nodes
print("\n🔗 Nodes in the Graph:")
for node in compiled_graph.nodes:
    print(f"• {node}")

# ✅ Print Edges
print("\n➡️ Edges in the Graph:")
for edge in compiled_graph.edges:
    print(f"{edge[0]} → {edge[1]}")

# print the graph
# compiled_graph = research_assistant.get_graph()
# print("Nodes: ",compiled_graph.nodes)
# print("Edges: ",compiled_graph.edges)

# ✅ Run a test input
test_state = {"topic": "SpaceX"}
result = research_assistant.invoke(test_state)

# ✅ Print the output to verify execution
print("🔍 Research Output:", result.get("article", "No article found"))
print("✍ Summary Output:", result.get("summary", "No summary generated"))
print("📊 Sentiment Analysis:", result.get("sentiment", "No sentiment detected"))
print("✅ Fact-Check:", result.get("fact_check", "No fact-check performed"))
print("📃 Final Report:", result.get("final_report", "No report generated"))

