import streamlit as st
from utils.sqlite_connector import SqliteConnector
from utils.utils import get_podcast_details, get_podcast_cover


# Setup
db_file_path = "podscape/podcast_index_db/data/podcastindex_feeds.db"
sqlite_connector = SqliteConnector(db_file_path)

# Page title
st.write("""
# Podscape
""")

# Sidebar
st.sidebar.header('User Input Features')

# Collect user input
def user_input_features():
    podcast_name = st.sidebar.text_input('Podcast title', 'Today, Explained')
    return podcast_name

podcast_name = user_input_features()

# Body
## Podcast details
st.subheader('Podcast Details')
df = get_podcast_details(sqlite_connector, podcast_name)
if df.shape[0] == 0:
    st.write("Podcast not found")
else:
    if df.shape[0] == 1:
        cover_url = get_podcast_cover(sqlite_connector, podcast_name)
        st.image(cover_url, width=200)
    st.dataframe(df)
