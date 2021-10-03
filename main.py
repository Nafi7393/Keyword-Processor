import streamlit as st


def format_text_to_list(string):
    the_list = string.split()
    final_list = []
    for word in the_list:
        if word not in final_list:
            final_list.append(word)
    return final_list


st.set_page_config(page_title="Keyword Processor")
hide_menu = """
<style>#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>"""
st.markdown(hide_menu, unsafe_allow_html=True)

st.markdown("## ***Enter All Keywords***")
all_keywords = st.text_area("", height=25)

if st.button("Make Keywords"):
    keyword_string = ""
    keyword_list = format_text_to_list(all_keywords)
    for wrd in keyword_list:
        keyword_string += wrd + " "
    st.write(keyword_string)

















