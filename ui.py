import streamlit as st
import requests

# ✅ FastAPI Backend URL
API_URL = "http://localhost:8000/fetch_news"

# ✅ Streamlit UI Setup
st.title("📰 AI Research Assistant")
st.subheader("Enter a topic to fetch and summarize news")

# ✅ User Input
topic = st.text_input("Enter a topic:", "")

# ✅ Fetch News from API when button is clicked
if st.button("Fetch News"):
    if topic:
        with st.spinner("Fetching news..."):
            response = requests.post(API_URL, json={"topic": topic})
            if response.status_code == 200:
                data = response.json()
                st.success("✅ News fetched successfully!")
                st.write(f"### 🔍 Topic: {data['topic']}")
                st.write(f"#### 📰 Article:\n{data['article']}")
                st.write(f"#### ✍ Summary:\n{data['summary']}")
            else:
                st.error("❌ Failed to fetch news. Try again!")
    else:
        st.warning("⚠️ Please enter a topic before fetching news.")

