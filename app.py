import streamlit as st
import requests
import json
import time
import random
import logging
import os
from datetime import datetime
from PIL import Image
import io
import base64

# Set up logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_filename = f"{log_dir}/svomo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("svomo")

# Set page configuration
st.set_page_config(
    page_title="SVOMO RECOMMENDATION",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load API keys from secrets
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# Define API endpoints
TMDB_BASE_URL = "https://api.themoviedb.org/3"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Default image for missing posters
DEFAULT_IMAGE_URL = "https://i.ibb.co/s9ZYS5wk/45e6544ed099.jpg"

# Custom CSS for retro style UI
def load_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=VT323&family=Press+Start+2P&display=swap');
        
        * {
            font-family: 'VT323', monospace;
        }
        
        h1, h2, h3 {
            font-family: 'Press Start 2P', cursive;
            color: #39FF14;
            text-shadow: 0 0 5px #39FF14, 0 0 10px #39FF14;
        }
        
        .stButton button {
            background-color: #FF00FF;
            color: #000000;
            border: 2px solid #00FFFF;
            border-radius: 0px;
            font-family: 'Press Start 2P', cursive;
            font-size: 14px;
            padding: 10px 20px;
            margin: 10px 0px;
            cursor: pointer;
            box-shadow: 0 0 10px #FF00FF;
            transition: all 0.3s;
        }
        
        .stButton button:hover {
            background-color: #00FFFF;
            color: #000000;
            border: 2px solid #FF00FF;
            box-shadow: 0 0 20px #00FFFF;
            transform: translateY(-2px);
        }
        
        .retro-card {
            background-color: rgba(0, 0, 0, 0.7);
            border: 2px solid #39FF14;
            border-radius: 0px;
            padding: 20px;
            margin: 10px 0px;
            color: #FFFFFF;
            box-shadow: 0 0 15px rgba(57, 255, 20, 0.5);
            animation: glow 3s infinite alternate;
        }
        
        @keyframes glow {
            from {
                box-shadow: 0 0 10px rgba(57, 255, 20, 0.5);
            }
            to {
                box-shadow: 0 0 20px rgba(57, 255, 20, 0.8);
            }
        }
        
        .retro-input {
            background-color: #000000;
            color: #39FF14;
            border: 2px solid #39FF14;
            border-radius: 0px;
            padding: 10px;
            font-family: 'VT323', monospace;
            font-size: 18px;
        }
        
        .crt-effect {
            animation: textShadow 1.6s infinite;
        }
        
        @keyframes textShadow {
            0% {
                text-shadow: 0.4389924193300864px 0 1px rgba(0,30,255,0.5), -0.4389924193300864px 0 1px rgba(255,0,80,0.3), 0 0 3px;
            }
            5% {
                text-shadow: 2.7928974010788217px 0 1px rgba(0,30,255,0.5), -2.7928974010788217px 0 1px rgba(255,0,80,0.3), 0 0 3px;
            }
            10% {
                text-shadow: 0.02956275843481219px 0 1px rgba(0,30,255,0.5), -0.02956275843481219px 0 1px rgba(255,0,80,0.3), 0 0 3px;
            }
            15% {
                text-shadow: 0.40218538552878136px 0 1px rgba(0,30,255,0.5), -0.40218538552878136px 0 1px rgba(255,0,80,0.3), 0 0 3px;
            }
            20% {
                text-shadow: 3.4794037899852017px 0 1px rgba(0,30,255,0.5), -3.4794037899852017px 0 1px rgba(255,0,80,0.3), 0 0 3px;
            }
            25% {
                text-shadow: 1.6125630401149584px 0 1px rgba(0,30,255,0.5), -1.6125630401149584px 0 1px rgba(255,0,80,0.3), 0 0 3px;
            }
            30% {
                text-shadow: 0.7015590085143956px 0 1px rgba(0,30,255,0.5), -0.7015590085143956px 0 1px rgba(255,0,80,0.3), 0 0 3px;
            }
            35% {
                text-shadow: 3.896914047650351px 0 1px rgba(0,30,255,0.5), -3.896914047650351px 0 1px rgba(255,0,80,0.3), 0 0 3px;
            }
            40% {
                text-shadow: 3.870905614848819px 0 1px rgba(0,30,255,0.5), -3.870905614848819px 0 1px rgba(255,0,80,0.3), 0 0 3px;
            }
            45% {
                text-shadow: 2.231056963361899px 0 1px rgba(0,30,255,0.5), -2.231056963361899px 0 1px rgba(255,0,80,0.3), 0 0 3px;
            }
            50% {
                text-shadow: 0.08084290417898504px 0 1px rgba(0,30,255,0.5), -0.08084290417898504px 0 1px rgba(255,0,80,0.3), 0 0 3px;
            }
            55% {
                text-shadow: 2.3758461067427543px 0 1px rgba(0,30,255,0.5), -2.3758461067427543px 0 1px rgba(255,0,80,0.3), 0 0 3px;
            }
            60% {
                text-shadow: 2.202193051050636px 0 1px rgba(0,30,255,0.5), -2.202193051050636px 0 1px rgba(255,0,80,0.3), 0 0 3px;
            }
            65% {
                text-shadow: 2.8638780614874975px 0 1px rgba(0,30,255,0.5), -2.8638780614874975px 0 1px rgba(255,0,80,0.3), 0 0 3px;
            }
            70% {
                text-shadow: 0.48874025155497314px 0 1px rgba(0,30,255,0.5), -0.48874025155497314px 0 1px rgba(255,0,80,0.3), 0 0 3px;
            }
            75% {
                text-shadow: 1.8948491305757957px 0 1px rgba(0,30,255,0.5), -1.8948491305757957px 0 1px rgba(255,0,80,0.3), 0 0 3px;
            }
            80% {
                text-shadow: 0.0833037308038857px 0 1px rgba(0,30,255,0.5), -0.0833037308038857px 0 1px rgba(255,0,80,0.3), 0 0 3px;
            }
            85% {
                text-shadow: 0.09769827255241735px 0 1px rgba(0,30,255,0.5), -0.09769827255241735px 0 1px rgba(255,0,80,0.3), 0 0 3px;
            }
            90% {
                text-shadow: 3.443339761481782px 0 1px rgba(0,30,255,0.5), -3.443339761481782px 0 1px rgba(255,0,80,0.3), 0 0 3px;
            }
            95% {
                text-shadow: 2.1841838852799786px 0 1px rgba(0,30,255,0.5), -2.1841838852799786px 0 1px rgba(255,0,80,0.3), 0 0 3px;
            }
            100% {
                text-shadow: 2.6208764473832513px 0 1px rgba(0,30,255,0.5), -2.6208764473832513px 0 1px rgba(255,0,80,0.3), 0 0 3px;
            }
        }
        
        .retro-background {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, #000000, #1f0033);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
            z-index: -1;
        }
        
        @keyframes gradient {
            0% {
                background-position: 0% 50%;
            }
            50% {
                background-position: 100% 50%;
            }
            100% {
                background-position: 0% 50%;
            }
        }
        
        .retro-grid {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                linear-gradient(rgba(57, 255, 20, 0.1) 1px, transparent 1px),
                linear-gradient(90deg, rgba(57, 255, 20, 0.1) 1px, transparent 1px);
            background-size: 20px 20px;
            z-index: -1;
            perspective: 1000px;
            transform-style: preserve-3d;
            animation: grid-animation 20s infinite linear;
        }
        
        @keyframes grid-animation {
            0% {
                transform: translateZ(0) translateY(0);
            }
            100% {
                transform: translateZ(0) translateY(20px);
            }
        }
        
        .loading-animation {
            width: 50px;
            height: 50px;
            border: 5px solid rgba(57, 255, 20, 0.3);
            border-radius: 50%;
            border-top-color: #39FF14;
            animation: spin 1s ease-in-out infinite;
            margin: 20px auto;
            box-shadow: 0 0 15px #39FF14;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .credits {
            text-align: center;
            color: #39FF14;
            font-family: 'VT323', monospace;
            font-size: 16px;
            margin-top: 20px;
            padding: 5px;
            border-top: 1px solid #39FF14;
            border-bottom: 1px solid #39FF14;
            background-color: rgba(0, 0, 0, 0.5);
        }
        
        /* Scanline effect */
        .scanlines {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: repeating-linear-gradient(
                to bottom,
                rgba(0, 0, 0, 0) 0px,
                rgba(0, 0, 0, 0) 1px,
                rgba(0, 0, 0, 0.1) 1px,
                rgba(0, 0, 0, 0.1) 2px
            );
            pointer-events: none;
            z-index: 10;
        }
    </style>
    <div class="retro-background"></div>
    <div class="retro-grid"></div>
    <div class="scanlines"></div>
    """, unsafe_allow_html=True)

# Display loading animation
def loading_animation():
    with st.spinner():
        st.markdown('<div class="loading-animation"></div>', unsafe_allow_html=True)
        time.sleep(2)

# Function to call Gemini API
def call_gemini_api(prompt):
    logger.info(f"Calling Gemini API with prompt length: {len(prompt)}")
    
    if not GEMINI_API_KEY:
        error_msg = "Missing Gemini API key in secrets.toml"
        logger.error(error_msg)
        st.error(error_msg)
        return None
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    url = f"{GEMINI_BASE_URL}?key={GEMINI_API_KEY}"
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        # Log success but not the full response content (could be large)
        logger.info(f"Gemini API call successful, response length: {len(str(result))}")
        
        # Validate response structure
        if "candidates" not in result or not result["candidates"]:
            error_msg = "Gemini API returned empty candidates"
            logger.error(error_msg)
            st.error(error_msg)
            return None
            
        if "content" not in result["candidates"][0] or "parts" not in result["candidates"][0]["content"]:
            error_msg = "Unexpected Gemini API response structure"
            logger.error(error_msg)
            st.error(error_msg)
            return None
            
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except requests.exceptions.ConnectionError as e:
        error_msg = f"Connection error calling Gemini API: {e}"
        logger.error(error_msg)
        st.error(error_msg)
        return None
    except requests.exceptions.RequestException as e:
        error_msg = f"Request error calling Gemini API: {e}"
        logger.error(error_msg)
        st.error(error_msg)
        return None
    except Exception as e:
        error_msg = f"Error calling Gemini API: {e}"
        logger.error(error_msg)
        st.error(error_msg)
        return None

# Function to call TMDB API
def call_tmdb_api(endpoint, params=None):
    if not TMDB_API_KEY:
        error_msg = "Missing TMDB API key in secrets.toml"
        logger.error(error_msg)
        st.error(error_msg)
        return None
    
    if params is None:
        params = {}
    
    params["api_key"] = TMDB_API_KEY
    
    url = f"{TMDB_BASE_URL}/{endpoint}"
    logger.info(f"Calling TMDB API: {endpoint}")
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        logger.info(f"TMDB API call successful: {endpoint}")
        return data
    except requests.exceptions.ConnectionError as e:
        error_msg = f"Connection error calling TMDB API {endpoint}: {e}"
        logger.error(error_msg)
        st.error(error_msg)
        return None
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP error calling TMDB API {endpoint}: {e}"
        logger.error(error_msg)
        st.error(error_msg)
        return None
    except Exception as e:
        error_msg = f"Error calling TMDB API {endpoint}: {e}"
        logger.error(error_msg)
        st.error(error_msg)
        return None

# Function to get movie poster
def get_movie_poster(poster_path, size="w500"):
    if not poster_path:
        return DEFAULT_IMAGE_URL
    
    config = call_tmdb_api("configuration")
    if config and "images" in config:
        base_url = config["images"]["secure_base_url"]
        return f"{base_url}{size}{poster_path}"
    
    return DEFAULT_IMAGE_URL

# Function to generate questions based on user persona
def generate_questions(persona):
    logger.info(f"Generating questions for persona: {persona}")
    
    prompt = f"""
    I need to create a series of questions for a movie recommendation system.
    The user has identified as: {persona}
    
    Please generate 10 sequential questions that will help understand their movie preferences.
    Each question should have 2-4 options for the user to choose from.
    Each question should build on previous questions in a conversational way.
    
    Format your response as a JSON array of question objects, where each object has:
    1. "question": The text of the question
    2. "options": An array of possible responses
    
    Example:
    [
      {{
        "question": "Are you watching alone or with someone?",
        "options": ["Alone", "With friends", "With family", "With a partner"]
      }},
      {{
        "question": "What's your current mood?",
        "options": ["Happy", "Relaxed", "Sad", "Excited", "Thoughtful"]
      }}
    ]
    
    Make the questions engaging and relevant to the {persona} persona.
    Make sure your response is properly formatted and valid JSON.
    """
    
    response = call_gemini_api(prompt)
    if not response:
        logger.error("Failed to get response from Gemini API for questions")
        return []
    
    try:
        # Log the raw response for debugging
        logger.info(f"Raw Gemini response length: {len(response)}")
        
        # Extract JSON from the response (handling potential text before or after the JSON)
        json_start = response.find('[')
        json_end = response.rfind(']') + 1
        
        if json_start == -1 or json_end == 0:
            error_msg = "Could not find JSON array in Gemini response"
            logger.error(error_msg)
            st.error(error_msg)
            
            # Fallback to default questions if JSON extraction fails
            default_questions = [
                {
                    "question": "Are you watching alone or with someone?",
                    "options": ["Alone", "With friends", "With family", "With a partner"]
                },
                {
                    "question": "What's your current mood?",
                    "options": ["Happy", "Relaxed", "Sad", "Excited", "Thoughtful"]
                },
                {
                    "question": "Do you prefer older classics or newer releases?",
                    "options": ["Classics", "Recent releases", "Both"]
                },
                {
                    "question": "How much time do you have?",
                    "options": ["Under 2 hours", "2-3 hours", "I have all day"]
                },
                {
                    "question": "What kind of ending do you prefer?",
                    "options": ["Happy", "Thought-provoking", "Doesn't matter"]
                }
            ]
            
            logger.info("Using default questions instead")
            return default_questions
        
        json_str = response[json_start:json_end]
        logger.info(f"Extracted JSON string length: {len(json_str)}")
        
        questions = json.loads(json_str)
        logger.info(f"Successfully parsed {len(questions)} questions")
        
        # Validate question format
        for i, q in enumerate(questions):
            if "question" not in q or "options" not in q:
                logger.warning(f"Question {i} has invalid format")
            elif not q["options"]:
                logger.warning(f"Question {i} has no options")
                q["options"] = ["Yes", "No"]  # Add default options
        
        return questions
    except json.JSONDecodeError as e:
        error_msg = f"JSON decode error: {e}"
        logger.error(error_msg)
        logger.error(f"Failed JSON string: {response[:100]}...")
        st.error(error_msg)
        return []
    except Exception as e:
        error_msg = f"Error parsing questions: {e}"
        logger.error(error_msg)
        st.error(error_msg)
        return []

# Function to get movie recommendations
def get_recommendations(answers, persona):
    logger.info(f"Getting recommendations for persona: {persona} with {len(answers)} answers")
    
    # Construct a prompt for Gemini to generate movie recommendations
    answers_text = "\n".join([f"Q: {q['question']}\nA: {q['answer']}" for q in answers])
    
    prompt = f"""
    Based on the following user preferences, recommend 3 movies or shows that would be perfect for them.
    
    User persona: {persona}
    
    User responses:
    {answers_text}
    
    For each recommendation, provide:
    1. The exact title (be precise for API searching)
    2. The release year (just the year as a 4-digit number)
    3. A brief explanation of why this is a good match
    
    Format your response as a JSON array:
    [
      {{
        "title": "Movie Title",
        "year": "YYYY",
        "reason": "Brief explanation"
      }},
      ...
    ]
    
    Make sure your response is properly formatted JSON.
    Only include these three fields (title, year, reason) for each recommendation.
    Be very accurate with movie titles to ensure they can be found in the TMDB database.
    """
    
    response = call_gemini_api(prompt)
    if not response:
        logger.error("Failed to get response from Gemini API for recommendations")
        return []
    
    try:
        # Log the raw response for debugging
        logger.info(f"Raw recommendation response length: {len(response)}")
        
        # Extract JSON from the response
        json_start = response.find('[')
        json_end = response.rfind(']') + 1
        
        if json_start == -1 or json_end == 0:
            error_msg = "Could not find JSON array in recommendation response"
            logger.error(error_msg)
            st.error(error_msg)
            
            # Fallback to default recommendations if JSON extraction fails
            return [
                {
                    "title": "The Shawshank Redemption",
                    "year": "1994",
                    "reason": "A highly rated classic that appeals to most viewers"
                },
                {
                    "title": "Inception",
                    "year": "2010",
                    "reason": "A mind-bending thriller with wide appeal"
                },
                {
                    "title": "The Princess Bride",
                    "year": "1987",
                    "reason": "A beloved classic with humor, romance, and adventure"
                }
            ]
        
        json_str = response[json_start:json_end]
        logger.info(f"Extracted JSON string length: {len(json_str)}")
        
        recommendations = json.loads(json_str)
        logger.info(f"Successfully parsed {len(recommendations)} recommendations")
        
        # Validate recommendation format
        valid_recommendations = []
        for i, rec in enumerate(recommendations):
            if "title" not in rec:
                logger.warning(f"Recommendation {i} missing title")
            elif "year" not in rec:
                logger.warning(f"Recommendation {i} missing year")
                rec["year"] = ""  # Add empty year
            elif "reason" not in rec:
                logger.warning(f"Recommendation {i} missing reason")
                rec["reason"] = "Recommended based on your preferences"  # Add default reason
            
            if "title" in rec:  # Only keep recommendations with at least a title
                valid_recommendations.append(rec)
        
        return valid_recommendations
    except json.JSONDecodeError as e:
        error_msg = f"JSON decode error in recommendations: {e}"
        logger.error(error_msg)
        logger.error(f"Failed JSON string: {response[:100]}...")
        st.error(error_msg)
        return []
    except Exception as e:
        error_msg = f"Error parsing recommendations: {e}"
        logger.error(error_msg)
        st.error(error_msg)
        return []

# Function to search for movies/shows in TMDB
def search_tmdb(title, year=None):
    logger.info(f"Searching TMDB for: '{title}', year: {year}")
    
    if not title:
        logger.warning("Empty title provided to search_tmdb")
        return None
    
    params = {
        "query": title,
        "include_adult": "false",
    }
    
    # Clean up year parameter
    if year:
        try:
            # Extract just the year if it's in a date format
            if len(year) > 4 and '-' in year:
                year = year.split('-')[0]
            
            # Make sure it's a 4-digit year
            if len(year) >= 4:
                year = year[:4]
                
            params["year"] = year
            logger.info(f"Using year parameter: {year}")
        except Exception as e:
            logger.warning(f"Error processing year parameter: {e}")
    
    # First try searching for movies
    movie_results = call_tmdb_api("search/movie", params)
    
    # Then try searching for TV shows
    tv_results = call_tmdb_api("search/tv", params)
    
    results = []
    
    # Process movie results
    if movie_results and "results" in movie_results:
        logger.info(f"Found {len(movie_results['results'])} movie results")
        for movie in movie_results["results"][:3]:  # Take top 3 results
            movie["media_type"] = "movie"
            results.append(movie)
    else:
        logger.warning("No movie results found")
    
    # Process TV results
    if tv_results and "results" in tv_results:
        logger.info(f"Found {len(tv_results['results'])} TV results")
        for show in tv_results["results"][:3]:  # Take top 3 results
            show["media_type"] = "tv"
            results.append(show)
    else:
        logger.warning("No TV results found")
    
    # Sort by popularity and take top result
    if results:
        results.sort(key=lambda x: x.get("popularity", 0), reverse=True)
        logger.info(f"Top result: {results[0].get('title', results[0].get('name', 'Unknown'))} (type: {results[0].get('media_type')})")
        return results[0]
    
    # If no results with exact year, try without year
    if year and not results:
        logger.info(f"No results with year {year}, trying without year parameter")
        params.pop("year", None)
        
        # Try again for movies
        movie_results = call_tmdb_api("search/movie", params)
        if movie_results and "results" in movie_results and movie_results["results"]:
            for movie in movie_results["results"][:1]:
                movie["media_type"] = "movie"
                logger.info(f"Found movie without year filter: {movie.get('title', 'Unknown')}")
                return movie
        
        # Try again for TV
        tv_results = call_tmdb_api("search/tv", params)
        if tv_results and "results" in tv_results and tv_results["results"]:
            for show in tv_results["results"][:1]:
                show["media_type"] = "tv"
                logger.info(f"Found TV show without year filter: {show.get('name', 'Unknown')}")
                return show
    
    logger.warning(f"No results found for '{title}'")
    return None

# Function to get movie/show details with AI description
def get_media_details(item, reason):
    if not item:
        return None
    
    media_type = item.get("media_type", "movie")
    item_id = item.get("id")
    
    if media_type == "movie":
        details = call_tmdb_api(f"movie/{item_id}")
    else:
        details = call_tmdb_api(f"tv/{item_id}")
    
    if not details:
        return None
    
    # Get poster
    poster_path = details.get("poster_path")
    poster_url = get_movie_poster(poster_path)
    
    # Format release date/year
    if media_type == "movie":
        release_date = details.get("release_date", "")
        year = release_date[:4] if release_date else "Unknown"
        title = details.get("title", "Unknown")
    else:
        first_air_date = details.get("first_air_date", "")
        year = first_air_date[:4] if first_air_date else "Unknown"
        title = details.get("name", "Unknown")
    
    # Get genres
    genres = ", ".join([g.get("name", "") for g in details.get("genres", [])])
    
    # Generate AI description
    overview = details.get("overview", "")
    prompt = f"""
    Create a personalized, enthusiastic short description (max 100 words) for the {media_type} "{title}" (released in {year}).
    
    Official overview: {overview}
    
    Reason for recommendation: {reason}
    
    Genres: {genres}
    
    Make it sound exciting and explain why the viewer will enjoy it based on their preferences.
    Use a retro, enthusiastic tone that matches a nostalgic movie recommendation system.
    """
    
    ai_description = call_gemini_api(prompt) or "No description available."
    
    return {
        "title": title,
        "year": year,
        "poster_url": poster_url,
        "overview": overview,
        "genres": genres,
        "ai_description": ai_description,
        "media_type": media_type,
        "reason": reason
    }

# Function to display movie/show card
def display_media_card(media):
    if not media:
        return
    
    with st.container():
        st.markdown(f'<div class="retro-card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(media["poster_url"], width=200)
        
        with col2:
            st.markdown(f"### {media['title']} ({media['year']})")
            st.markdown(f"**Type:** {'Movie' if media['media_type'] == 'movie' else 'TV Show'}")
            st.markdown(f"**Genres:** {media['genres']}")
            st.markdown("### Why Watch This:")
            st.markdown(f"{media['ai_description']}")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Main app flow
def main():
    # Initialize session state variables
    if 'step' not in st.session_state:
        st.session_state.step = 'intro'
        logger.info("Initializing app with 'intro' step")
    if 'persona' not in st.session_state:
        st.session_state.persona = None
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'answers' not in st.session_state:
        st.session_state.answers = []
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = []
    if 'media_details' not in st.session_state:
        st.session_state.media_details = []
    if 'load_more_count' not in st.session_state:
        st.session_state.load_more_count = 0
    if 'debug_mode' not in st.session_state:
        st.session_state.debug_mode = False
        
    # Log current app state at startup
    logger.info(f"Current app state: {st.session_state.step}")
    
    # Check for API keys
    if not TMDB_API_KEY:
        logger.warning("TMDB API key not found in secrets.toml")
        st.sidebar.warning("⚠️ TMDB API key missing. Add it to .streamlit/secrets.toml")
    if not GEMINI_API_KEY:
        logger.warning("Gemini API key not found in secrets.toml")
        st.sidebar.warning("⚠️ Gemini API key missing. Add it to .streamlit/secrets.toml")
    
    # Load custom CSS
    load_custom_css()
    
    # App logo and header
    st.markdown('<h1 class="crt-effect">SVOMO RECOMMENDATION</h1>', unsafe_allow_html=True)
    
    # Credits
    st.markdown('<div class="credits">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p>Powered by Google Gemini</p>', unsafe_allow_html=True)
    with col2:
        st.markdown('<p>Movie data from TMDB</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Debug mode toggle in sidebar
    with st.sidebar:
        st.markdown("### Developer Tools")
        debug_toggle = st.checkbox("Enable Debug Mode", value=st.session_state.debug_mode)
        
        if debug_toggle != st.session_state.debug_mode:
            st.session_state.debug_mode = debug_toggle
            st.rerun()
            
        if st.session_state.debug_mode:
            st.markdown("### Debug Information")
            st.markdown(f"**Current State:** {st.session_state.step}")
            st.markdown(f"**Selected Persona:** {st.session_state.persona}")
            st.markdown(f"**Questions Count:** {len(st.session_state.questions)}")
            st.markdown(f"**Current Question:** {st.session_state.current_question}")
            st.markdown(f"**Answers Count:** {len(st.session_state.answers)}")
            st.markdown(f"**Recommendations Count:** {len(st.session_state.recommendations)}")
            st.markdown(f"**Media Details Count:** {len(st.session_state.media_details)}")
            st.markdown(f"**Log File:** {log_filename}")
            
            if st.button("View Session State"):
                st.json(st.session_state)
                
            if st.button("Reset Application"):
                st.session_state.clear()
                st.rerun()
    
    # Introduction screen
    if st.session_state.step == 'intro':
        st.markdown('<div class="retro-card crt-effect">', unsafe_allow_html=True)
        st.markdown("""
        # Welcome to SVOMO RECOMMENDATION
        
        This retro-futuristic AI will help you find the perfect movie or show to watch.
        
        First, tell us what kind of content you're interested in:
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Persona selection
        persona_options = [
            "Movie Fan - Hollywood",
            "Movie Fan - Bollywood", 
            "Movie Fan - Korean",
            "Movie Fan - Japanese",
            "Anime Enthusiast",
            "TV Series Binger",
            "Documentary Lover",
            "Indie Film Aficionado"
        ]
        
        cols = st.columns(4)
        for i, persona in enumerate(persona_options):
            with cols[i % 4]:
                if st.button(persona, key=f"persona_{i}"):
                    st.session_state.persona = persona
                    # Generate questions based on persona
                    loading_animation()
                    st.session_state.questions = generate_questions(persona)
                    st.session_state.step = 'questions'
                    st.rerun()
    
    # Questions screen
    elif st.session_state.step == 'questions':
        # Display progress
        total_questions = len(st.session_state.questions)
        current_q = st.session_state.current_question + 1
        st.progress(current_q / total_questions)
        
        st.markdown(f'<div class="retro-card crt-effect">', unsafe_allow_html=True)
        
        # Display current question
        if st.session_state.current_question < len(st.session_state.questions):
            question = st.session_state.questions[st.session_state.current_question]
            
            st.markdown(f"### Question {current_q}/{total_questions}")
            st.markdown(f"## {question['question']}")
            
            # Display options as buttons in a grid
            option_count = len(question['options'])
            cols_per_row = min(4, option_count)
            
            # Create rows with appropriate number of columns
            rows = (option_count + cols_per_row - 1) // cols_per_row
            
            for row in range(rows):
                cols = st.columns(cols_per_row)
                for col in range(cols_per_row):
                    idx = row * cols_per_row + col
                    if idx < option_count:
                        with cols[col]:
                            if st.button(question['options'][idx], key=f"option_{idx}"):
                                # Save answer
                                answer = {
                                    'question': question['question'],
                                    'answer': question['options'][idx]
                                }
                                st.session_state.answers.append(answer)
                                
                                # Move to next question
                                st.session_state.current_question += 1
                                
                                # If all questions answered, move to recommendations
                                if st.session_state.current_question >= len(st.session_state.questions):
                                    st.session_state.step = 'loading_recommendations'
                                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Loading recommendations screen
    elif st.session_state.step == 'loading_recommendations':
        st.markdown('<div class="retro-card crt-effect">', unsafe_allow_html=True)
        st.markdown("## ANALYZING YOUR PREFERENCES...")
        st.markdown('<div class="loading-animation"></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        try:
            # Log the current state
            logger.info(f"Getting recommendations for {st.session_state.persona}")
            logger.info(f"User answers: {json.dumps(st.session_state.answers)}")
            
            # Get recommendations
            recommendations = get_recommendations(st.session_state.answers, st.session_state.persona)
            logger.info(f"Received {len(recommendations)} recommendations")
            
            # Store recommendations in session state
            st.session_state.recommendations = recommendations
            
            # Display status for debugging
            status_container = st.empty()
            
            # Get details for each recommendation
            media_details = []
            for idx, rec in enumerate(recommendations):
                title = rec.get("title", "")
                year = rec.get("year", "")
                reason = rec.get("reason", "")
                
                # Show processing status
                status_container.info(f"Processing recommendation {idx+1}/{len(recommendations)}: {title} ({year})")
                logger.info(f"Searching for: {title} ({year})")
                
                # Search for the movie/show in TMDB
                result = search_tmdb(title, year)
                
                # Log search result
                if result:
                    logger.info(f"Found match for '{title}' in TMDB: {result.get('id')}")
                else:
                    logger.warning(f"No match found for '{title}' in TMDB")
                    continue
                
                # Get detailed information
                details = get_media_details(result, reason)
                if details:
                    logger.info(f"Successfully got details for '{title}'")
                    media_details.append(details)
                else:
                    logger.warning(f"Failed to get details for '{title}'")
            
            # Clear the status
            status_container.empty()
            
            logger.info(f"Processed {len(media_details)} media details")
            
            # Store in session state
            st.session_state.media_details = media_details
            
            # If no recommendations found, add debugging info
            if not media_details:
                logger.error("No media details found for any recommendations")
                if not recommendations:
                    logger.error("No recommendations returned from AI")
                else:
                    logger.error(f"Recommendations were generated but no TMDB matches found: {json.dumps(recommendations)}")
                
                # Add fallback recommendation
                fallback = {
                    "title": "The Matrix",
                    "year": "1999",
                    "poster_url": DEFAULT_IMAGE_URL,
                    "overview": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
                    "genres": "Action, Science Fiction",
                    "ai_description": "This mind-bending sci-fi action film revolutionized visual effects with its 'bullet time' sequences. It combines philosophical themes with stunning action for a perfect movie night experience.",
                    "media_type": "movie",
                    "reason": "A universally acclaimed film that appeals to most viewers"
                }
                
                media_details.append(fallback)
                st.session_state.media_details = media_details
                logger.info("Added fallback recommendation")
            
            # Move to recommendations screen
            st.session_state.step = 'recommendations'
            st.rerun()
            
        except Exception as e:
            error_msg = f"Error in recommendation processing: {e}"
            logger.error(error_msg)
            st.error(error_msg)
            # Add a fallback recommendation
            st.session_state.step = 'recommendations'
            st.rerun()
    
    # Recommendations screen
    elif st.session_state.step == 'recommendations':
        st.markdown('<div class="retro-card crt-effect">', unsafe_allow_html=True)
        st.markdown(f"# Your Personalized Recommendations")
        st.markdown(f"Based on your preferences as a {st.session_state.persona}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display recommendations
        if st.session_state.media_details:
            for media in st.session_state.media_details:
                display_media_card(media)
            
            # Load more button
            if st.button("LOAD MORE RECOMMENDATIONS"):
                st.session_state.load_more_count += 1
                st.session_state.step = 'loading_more'
                st.rerun()
        else:
            st.markdown('<div class="retro-card">', unsafe_allow_html=True)
            st.markdown("## No recommendations found. Let's try again!")
            if st.button("START OVER"):
                st.session_state.clear()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Start over button
        if st.button("START OVER", key="restart_button"):
            st.session_state.clear()
            st.rerun()
    
    # Loading more recommendations
    elif st.session_state.step == 'loading_more':
        st.markdown('<div class="retro-card crt-effect">', unsafe_allow_html=True)
        st.markdown("## FINDING MORE RECOMMENDATIONS...")
        st.markdown('<div class="loading-animation"></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Create a more specific prompt based on previous recommendations
        previous_titles = ", ".join([media["title"] for media in st.session_state.media_details])
        
        answers_text = "\n".join([f"Q: {q['question']}\nA: {q['answer']}" for q in st.session_state.answers])
        
        prompt = f"""
        Based on the following user preferences, recommend 3 MORE movies or shows that would be perfect for them.
        
        User persona: {st.session_state.persona}
        
        User responses:
        {answers_text}
        
        Previously recommended: {previous_titles}
        
        Please recommend DIFFERENT titles that are still aligned with their preferences.
        
        For each recommendation, provide:
        1. The exact title (be precise for API searching)
        2. The release year
        3. A brief explanation of why this is a good match
        
        Format your response as a JSON array:
        [
          {{
            "title": "Movie Title",
            "year": "YYYY",
            "reason": "Brief explanation"
          }},
          ...
        ]
        """
        
        more_recommendations = call_gemini_api(prompt)
        
        try:
            # Extract JSON from the response
            json_start = more_recommendations.find('[')
            json_end = more_recommendations.rfind(']') + 1
            json_str = more_recommendations[json_start:json_end]
            
            new_recommendations = json.loads(json_str)
            
            # Get details for each new recommendation
            new_media_details = []
            for rec in new_recommendations:
                title = rec.get("title", "")
                year = rec.get("year", "")
                reason = rec.get("reason", "")
                
                # Search for the movie/show in TMDB
                result = search_tmdb(title, year)
                
                # Get detailed information
                if result:
                    details = get_media_details(result, reason)
                    if details:
                        new_media_details.append(details)
            
            # Add new recommendations to existing ones
            st.session_state.media_details.extend(new_media_details)
            st.session_state.step = 'recommendations'
            st.rerun()
        except Exception as e:
            st.error(f"Error loading more recommendations: {e}")
            st.session_state.step = 'recommendations'
            st.rerun()

if __name__ == "__main__":
    main()
