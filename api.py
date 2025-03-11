from fastapi import FastAPI
from pydantic import BaseModel
from rat import research_assistant  # Import LangGraph assistant

app = FastAPI()

# ✅ Define Request Model
class NewsRequest(BaseModel):
    topic: str

# ✅ API Endpoint to Fetch & Summarize News
@app.post("/fetch_news")
def fetch_news(request: NewsRequest):
    initial_state = {"topic": request.topic}
    result = research_assistant.invoke(initial_state)

    return {
        "topic": request.topic,
        "article": result.get("article", "No article found"),
        "summary": result.get("summary", "No summary generated"),
    }

# ✅ Run the Server (only if executed directly)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
