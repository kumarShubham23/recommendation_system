import streamlit as st
import pickle
import pandas as pd
import requests
import bz2

# Must be the very first Streamlit command
st.set_page_config(layout="wide")

# ===== CONFIGURATION =====
TMDB_API_KEY = "00aa6edaaab30dca9f2b72e59f58e851"
OMDB_API_KEY = "a455bd9"

# ===== DATA LOADING =====
# Load movies data
movies = pd.DataFrame(pickle.load(open('movies.pkl', 'rb')))

# Load bz2 compressed similarity matrix
with bz2.BZ2File('similarity.pkl.bz2', 'rb') as f:
    similarity = pickle.load(f)

# ===== POSTER FETCHER =====
def fetch_poster(movie_id, movie_title):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('poster_path'):
                return f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
    except:
        pass
    try:
        url = f"http://www.omdbapi.com/?t={movie_title}&apikey={OMDB_API_KEY}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('Poster') and data['Poster'] != "N/A":
                return data['Poster']
    except:
        pass
    return None

# ===== RECOMMENDATION SYSTEM =====
def recommend(movie):
    if movie not in movies['title'].values:
        return []
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]
    return [(movies.iloc[i[0]].title, movies.iloc[i[0]].id) for i in movie_list]

# ===== STREAMLIT UI =====
st.title("🎬 Movie Recommender Pro")

selected_movie = st.selectbox("Select a movie:", movies['title'].values, index=0)

if st.button('Get Recommendations'):
    with st.spinner('Finding recommendations...'):
        recommendations = recommend(selected_movie)

    if not recommendations:
        st.error("No recommendations found. Try another movie.")
    else:
        st.success("Top 10 Recommendations:")

        for row in range(2):  # Two rows
            cols = st.columns(5)  # Five columns per row
            for col in range(5):  # Five items per row
                idx = row * 5 + col
                if idx < len(recommendations):
                    with cols[col]:
                        title, movie_id = recommendations[idx]
                        poster_url = fetch_poster(movie_id, title)
                        if poster_url:
                            st.image(poster_url, width=220, caption=title)
                        st.markdown(f"<div style='text-align: center; font-weight: bold;'>{title}</div>",
                                    unsafe_allow_html=True)

# Custom CSS styling
st.markdown("""
<style>
    .stImage img {
        border-radius: 12px;
        transition: transform 0.3s ease;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        margin-bottom: 10px;
    }
    .stImage img:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        padding: 10px 24px;
        border-radius: 8px;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.02);
    }
    .stSelectbox>div>div>select {
        font-size: 16px;
        padding: 10px;
    }
    .stMarkdown div {
        margin-top: 5px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)
