import streamlit as st
import requests
import json

# Retrieve API keys from Streamlit secrets
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]

# Function to call Gemini API
def call_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    else:
        st.error("Error calling Gemini API")
        return None

# Generate the next question based on conversation history
def generate_question(history):
    history_str = ""
    for item in history:
        history_str += f"Assistant: {item['question']}\nUser: {item['answer']}\n"
    prompt = (
        f"You are a movie recommendation assistant. Generate the next question to understand the user's preferences and mood. "
        f"Provide the question and options in this format:\n"
        f"Question: <question text>\nOptions: <option1>, <option2>, <option3>, ...\n"
        f"Limit options to 2-4 choices. Base the question on the user's persona and previous answers.\n\n"
        f"Conversation so far:\n{history_str}"
    )
    response = call_gemini(prompt)
    if response:
        lines = response.split("\n")
        question = lines[0].replace("Question: ", "")
        options = lines[1].replace("Options: ", "").split(", ")
        return question, options
    return None, None

# Generate movie recommendations
def generate_recommendation(history):
    history_str = ""
    for item in history:
        history_str += f"Assistant: {item['question']}\nUser: {item['answer']}\n"
    prompt = (
        f"Based on the following conversation, recommend 3 movies that best match the user's preferences and mood. "
        f"Provide each recommendation in this format:\n"
        f"1. Title: <title>\nDescription: <short description (2-3 sentences)>\n\n"
        f"2. Title: <title>\nDescription: <short description (2-3 sentences)>\n\n"
        f"3. Title: <title>\nDescription: <short description (2-3 sentences)>\n\n"
        f"Conversation:\n{history_str}"
    )
    response = call_gemini(prompt)
    if response:
        movies = []
        for block in response.split("\n\n"):
            lines = block.split("\n")
            title = lines[0].split(": ")[1]
            description = lines[1].split(": ")[1]
            movies.append({"title": title, "description": description})
        return movies
    return None

# Streamlit app configuration
st.set_page_config(page_title="SVOMO RECOMMENDATION", layout="wide")

# Retro-futuristic CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
.stApp {
    background-color: #000000;
    color: #FFFFFF;
    font-family: 'Orbitron', sans-serif;
}
h1 {
    color: #00FF00;
    text-align: center;
}
.stButton>button {
    background-color: #00FF00;
    color: #000000;
    border: 2px solid #FFFFFF;
    font-family: 'Orbitron', sans-serif;
}
.stRadio label {
    color: #FFFFFF;
}
</style>
""", unsafe_allow_html=True)

st.title("SVOMO RECOMMENDATION")

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'step' not in st.session_state:
    st.session_state.step = 0

# Sequential questioning (10 questions total: ~4-5 persona + ~5-6 mood)
if st.session_state.step < 10:
    if f'question_{st.session_state.step}' not in st.session_state:
        with st.spinner("Loading your next question..."):
            question, options = generate_question(st.session_state.history)
            if question and options:
                st.session_state[f'question_{st.session_state.step}'] = question
                st.session_state[f'options_{st.session_state.step}'] = options
            else:
                st.error("Failed to generate question. Please try again.")
    else:
        question = st.session_state[f'question_{st.session_state.step}']
        options = st.session_state[f'options_{st.session_state.step}']
        st.write(question)
        answer = st.radio("Choose one:", options, key=f"radio_{st.session_state.step}")
        if st.button("Next"):
            st.session_state.history.append({
                "question": question,
                "options": options,
                "answer": answer
            })
            st.session_state.step += 1

# Display recommendations after 10 questions
else:
    if 'recommendations' not in st.session_state:
        with st.spinner("Finding the perfect movies for you..."):
            movies = generate_recommendation(st.session_state.history)
            if movies:
                st.session_state.recommendations = movies
            else:
                st.error("Failed to generate recommendations. Please try again.")
    else:
        movies = st.session_state.recommendations
        st.subheader("Your Movie Recommendations")
        cols = st.columns(3)
        for i, movie in enumerate(movies):
            with cols[i]:
                # Fetch movie details from TMDB
                search_url = f"https://api.themoviedb.org/3/search/movie?query={movie['title']}&api_key={TMDB_API_KEY}"
                response = requests.get(search_url)
                if response.status_code == 200 and response.json()["results"]:
                    result = response.json()["results"][0]
                    poster_path = result.get("poster_path")
                    image_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://i.ibb.co/s9ZYS5wk/45e6544ed099.jpg"
                    year = result.get("release_date", "")[:4] or "N/A"
                else:
                    image_url = "https://i.ibb.co/s9ZYS5wk/45e6544ed099.jpg"
                    year = "N/A"
                st.image(image_url, width=200, caption=f"{movie['title']} ({year})")
                st.write(f"**{movie['title']} ({year})**")
                st.write(movie['description'])

# Credits section
st.markdown("---")
st.write("Powered by:")
col1, col2 = st.columns(2)
with col1:
    # Placeholder for Google Gemini logo (replace with actual URL)
    st.image("https://via.placeholder.com/100?text=Gemini", width=100, caption="Google Gemini")
with col2:
    # TMDB official logo
    st.image("https://www.themoviedb.org/assets/2/v4/logos/v2/blue_short-8e7b30f73a4020692ccca9c88bafe5dcb6f8a62a4c6bc55cd9ba82bb2cd95f6c.svg", width=100, caption="The Movie Database")
