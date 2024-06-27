import streamlit as st
import requests
from dotenv import load_dotenv
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from rake_nltk import Rake

# Load environment variables
load_dotenv()
api_key = os.getenv("API_KEY")


# Function to extract keywords using Rake
def extract_keywords(text):
    r = Rake()
    r.extract_keywords_from_text(text)
    return list(set([k.lower() for k in r.get_ranked_phrases()]))


# Function to format text into a list manually
def format_text_to_list(string):
    return list(set([word.strip().upper() for word in string.split(",") if word.strip()]))


# Function to create and display word cloud
def create_word_cloud(word_list, title, bg_color="black", width=400, height=200):
    for w in word_list:
        if w == "" or w == " ":
            ok = False
        else:
            ok = True
            break

    if ok:
        wordcloud = WordCloud(width=width, height=height, background_color='white').generate(' '.join(word_list))
        plt.figure(figsize=(width/100, height/100))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        st.pyplot(plt)
        title_html = f"""
        <div style="background-color:{bg_color}; border-radius:5px; text-align: center; padding:5px;">
            <h3 style="color:white; margin: 0;">{title}</h3>
        </div>
        """
        st.markdown(title_html, unsafe_allow_html=True)
    else:
        st.write("No data available to create word cloud.")


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
        # st.error(f"Failed to fetch synonyms and antonyms for {this_keyword}. Error: {response.status_code}")
        return [], []


# Function to fetch word definition
def get_word_definition(this_keyword):
    api_url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{this_keyword}'
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        this_definitions = [meaning['definitions'][0]['definition'] for meaning in data[0]['meanings']]
        return this_definitions
    else:
        # st.error(f"Failed to fetch definition for {this_keyword}. Error: {response.status_code}")
        return []


# Streamlit configuration
st.set_page_config(page_title="Keyword Processor", layout="centered")

# Hide the default Streamlit menu and footer
hide_menu = """
<style>
header {visibility: none;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_menu, unsafe_allow_html=True)

# Page title, instructions & Text area for inputting keywords
st.markdown("## ***Enter Text Input***")
all_keywords = st.text_area("Enter your text here...", height=100)

# Initialize session state for keyword list and keyword details if not already done
if 'keyword_list' not in st.session_state:
    st.session_state.keyword_list = []

if 'keyword_details' not in st.session_state:
    st.session_state.keyword_details = {}

# Button to process keywords
if st.button("Process Keywords"):
    if all_keywords:
        # Format and process the input keywords
        st.session_state.keyword_list = extract_keywords(all_keywords)
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
        st.session_state.keyword_details[keyword] = {'definitions': definitions,
                                                     'synonyms': synonyms,
                                                     'antonyms': antonyms}
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

    cols = st.columns(2)  # Create two columns for side-by-side display
    with cols[0]:
        if details['synonyms']:
            create_word_cloud(details['synonyms'], f"Synonyms",
                              bg_color="black", width=300, height=150)
    with cols[1]:
        if details['antonyms']:
            create_word_cloud(details['antonyms'], f"Antonyms",
                              bg_color="black", width=300, height=150)
    st.markdown("---")
