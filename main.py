import streamlit as st
import requests
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY")

# Function to fetch synonyms and antonyms
def get_synonyms_and_antonyms(this_keyword):
    api_url = f'https://api.api-ninjas.com/v1/thesaurus?word={this_keyword}'
    headers = {'X-Api-Key': api_key}
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        word_synonyms = data.get('synonyms', [])
        word_antonyms = data.get('antonyms', [])
        return word_synonyms, word_antonyms
    else:
        st.error(f"Failed to fetch synonyms and antonyms for {this_keyword}. Error: {response.status_code}")
        return [], []

# Function to fetch word definition
def get_word_definition(this_keyword):
    api_url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{this_keyword}'
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        definitions = [meaning['definitions'][0]['definition'] for meaning in data[0]['meanings']]
        return definitions
    else:
        st.error(f"Failed to fetch definition for {this_keyword}. Error: {response.status_code}")
        return []

# Function to format text into a list
def format_text_to_list(string):
    the_list = [word.strip() for word in string.split(",") if word.strip()]
    return list(set(the_list))

# Streamlit configuration
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

# Initialize session state for keyword list and keyword details if not already done
if 'keyword_list' not in st.session_state:
    st.session_state.keyword_list = []

if 'keyword_details' not in st.session_state:
    st.session_state.keyword_details = {}

# Button to process keywords
if st.button("Process Keywords"):
    if all_keywords:
        # Format and process the input keywords
        st.session_state.keyword_list = format_text_to_list(all_keywords)
        keyword_string = ", ".join(st.session_state.keyword_list)

        # Clear previous keyword details
        st.session_state.keyword_details = {}

# Always display the processed keywords
if st.session_state.keyword_list:
    st.markdown("### Processed Keywords:")
    keyword_string = ", ".join(st.session_state.keyword_list)
    st.write(keyword_string)

    st.markdown("##")
    # Display synonyms and antonyms section
    st.markdown("### Word list to get Details")

# Display the synonyms and antonyms if they exist in the session state
cols = st.columns(3)  # the number of columns for synonyms & antonyms buttons
col_idx = 0

for keyword in st.session_state.keyword_list:
    if cols[col_idx].button(f"Get details for: {keyword.upper()}"):
        synonyms, antonyms = get_synonyms_and_antonyms(keyword)
        definitions = get_word_definition(keyword)
        st.session_state.keyword_details[keyword] = {'definitions': definitions, 'synonyms': synonyms, 'antonyms': antonyms}
    col_idx = (col_idx + 1) % len(cols)  # Move to the next column

st.markdown("##")

# Display fetched details
for keyword, details in st.session_state.keyword_details.items():
    definitions_str = "; ".join(details['definitions']) if details['definitions'] else "No definition found."
    synonyms_str = ", ".join(details['synonyms']) if details['synonyms'] else "No synonyms found."
    antonyms_str = ", ".join(details['antonyms']) if details['antonyms'] else "No antonyms found."

    # Display definitions, synonyms, and antonyms
    st.write(f'### Details for the word ***"{keyword.upper()}"***')
    st.write(f"**Definition for '{keyword.upper()}':** {definitions_str}")
    st.write(f"**Synonyms for '{keyword.upper()}':** {synonyms_str}")
    st.write(f"**Antonyms for '{keyword.upper()}':** {antonyms_str}")
    st.markdown("---")
