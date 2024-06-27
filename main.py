import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import requests
import pickle
from dotenv import load_dotenv
import os

load_dotenv()

# Access a variable
api_key = os.getenv("API_KEY")


# Function to format text input into a list of unique keywords
def format_text_to_list(string):
    # Split the input string by comma, remove any surrounding whitespace, and filter out empty strings
    the_list = [word.strip() for word in string.split(",") if word.strip()]

    # Remove duplicates by converting to a set and then back to a list
    final_list = list(set(the_list))

    return final_list


# Function to fetch synonyms using an external API (Datamuse)
def get_synonyms(keyword):
    api_url = f'https://api.api-ninjas.com/v1/thesaurus?word={keyword}'
    response = requests.get(api_url, headers={'X-Api-Key': api_key})

    return response.json()


# Initialize Streamlit app
st.set_page_config(page_title="Keyword Processor", layout="centered")

# Hide the default Streamlit menu and footer
hide_menu = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_menu, unsafe_allow_html=True)

# Page title and instructions
st.markdown("## ***Enter All Keywords***")
st.markdown("###### Please enter your keywords separated by commas:")

# Text area for inputting keywords
all_keywords = st.text_area("Enter keywords here...", height=100)

keyword_list = []


# Function to process keywords with categories
def process_keywords_with_categories():
    categories = st.multiselect("Select or create categories:", ["Category 1", "Category 2"], ["Category 1"])
    keyword_category_map = {category: [] for category in categories}

    if all_keywords:
        keyword_list = format_text_to_list(all_keywords)
        for keyword in keyword_list:
            category = st.selectbox(f"Select category for '{keyword}':", categories)
            keyword_category_map[category].append(keyword)

        st.markdown("### Categorized Keywords:")
        for category, keywords in keyword_category_map.items():
            st.markdown(f"#### {category}:")
            st.write(", ".join(keywords))
    else:
        st.error("Please enter some keywords before processing.")


# Function to export keywords to a CSV file
def export_keywords():
    if keyword_list:
        df = pd.DataFrame(keyword_list, columns=["Keywords"])
        df.to_csv("keywords.csv", index=False)
        st.success("Keywords exported to 'keywords.csv'.")
    else:
        st.error("No keywords to export.")


# Function to visualize keyword frequency using a bar chart and word cloud
def visualize_keywords():
    if keyword_list:
        # Word cloud
        wordcloud = WordCloud().generate(" ".join(keyword_list))
        st.image(wordcloud.to_array())
    else:
        st.error("No keywords to visualize.")


# Function to save and load keyword sessions using pickle
def save_session():
    with open("session.pkl", "wb") as f:
        pickle.dump(keyword_list, f)
    st.success("Session saved.")


def load_session():
    try:
        with open("session.pkl", "rb") as f:
            keyword_list = pickle.load(f)
        st.markdown("### Loaded Keywords:")
        st.write(", ".join(keyword_list))
    except FileNotFoundError:
        st.error("No saved session found.")


# Function to suggest synonyms for keywords using an external API
def suggest_synonyms():
    if keyword_list:
        synonyms = {keyword: get_synonyms(keyword) for keyword in keyword_list}
        st.write(synonyms)
        st.markdown("### Synonym Suggestions:")
    else:
        st.error("No keywords to suggest synonyms for.")


# Button to process keywords
if st.button("Process Keywords"):
    if all_keywords:
        keyword_list = format_text_to_list(all_keywords)
        keyword_string = ", ".join(keyword_list)
        st.markdown("### Processed Keywords:")
        st.write(keyword_string)
    else:
        st.error("Please enter some keywords before processing.")

# Buttons for additional features
if st.button("Process Keywords with Categories"):
    process_keywords_with_categories()

if st.button("Export Keywords"):
    export_keywords()

if st.button("Visualize Keywords"):
    visualize_keywords()

if st.button("Save Session"):
    save_session()

if st.button("Load Session"):
    load_session()

if st.button("Suggest Synonyms"):
    suggest_synonyms()
