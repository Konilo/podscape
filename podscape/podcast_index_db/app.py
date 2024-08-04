import streamlit as st
from sqlite_connector import SqliteConnector


st.write("""
# Podscape
""")

st.sidebar.header('User Input Features')

# Collect user input
def user_input_features():
    podcast_name = st.sidebar.text_input('Podcast Name', 'The Daily')
    return podcast_name

podcast_name = user_input_features()

# Load the data
db_file_path = "podscape/podcast_index_db/data/podcastindex_feeds.db"
sqlite_connector = SqliteConnector(db_file_path)

query = f"""
SELECT * FROM podcasts
limit 1
"""
df = sqlite_connector.query(query)

# Show the data
st.subheader('Podcast Data')
st.write(df)
