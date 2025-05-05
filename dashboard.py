import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# Function to load data from the database
def load_data():
    engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
		    .format(host='localhost:3306', db='newsletters', user='root', pw='rckanalytics'))
    with engine.connect() as conn, conn.begin():  # doctest: +SKIP
        df = pd.read_sql_query("SELECT * FROM monkey_insider", conn)
    return df

# --- App Layout ---
st.set_page_config(page_title="📚 Substack Article Dashboard", layout="wide")
#st.title("📚 Substack Article Dashboard")

# --------------------------------------------
# STYLING
# --------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
        font-size: 14px;
    }
    .block-container {
        padding-top: 2rem;
    }
    .logo {
        display: flex;
        align-items: center;
        padding-bottom: 1rem;
    }
    .logo img {
        height: 50px;
        margin-right: 10px;
        padding-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Logo and Header
from datetime import datetime

# Last Refreshed Date
last_refreshed = datetime.now().strftime("%B %d, %Y")

# Header styling
st.markdown("""
    <style>
        .header-container {
            display: flex;
            flex-direction: row;
            width: 100%;
            margin-bottom: 20px;
        }

        .logo-column {
            width: 20%;
            background-color: #ffffff;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .logo-column svg {
            width: 120px;
            height: auto;
        }

        .title-column {
            width: 80%;
            background-color: #0f74ba;
            color: white;
            padding: 20px 30px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .title-column h1 {
            font-family: 'Poppins', sans-serif;
            font-size: 2.2rem;
            margin: 0;
        }

        .title-column p {
            font-family: 'Poppins', sans-serif;
            font-size: 1rem;
            margin: 5px 0 0;
            opacity: 0.85;
        }
    </style>
""", unsafe_allow_html=True)

# Render the custom header with logo and content
st.markdown(f"""
<div class="header-container">
    <div class="logo-column">
        <img class="logo" src="https://img1.wsimg.com/isteam/ip/17320431-7cfa-4926-88af-4213f685e269/Add%20a%20heading%20(6)%209.png/:/rs=h:86,cg:true,m/qt=q:100/ll" alt="RCK Analytics">
    </div>
    <div class="title-column">
        <h1>📚 Substack Article Dashboard</h1>
        <p>Last updated: {last_refreshed}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Load data
df = load_data()
df['pubDate'] = pd.to_datetime(df['pubDate'])

# --- Sidebar Configuration ---
st.sidebar.header("🗓️ Filter by Date")

# Date range for the default view (last 4 days)
latest_date = df['pubDate'].max()
default_start_date = latest_date - pd.Timedelta(days=4)
default_end_date = latest_date

# Streamlit date pickers for start and end date
start_date = st.sidebar.date_input(
    "Select Start Date", 
    default_start_date.date(), 
    min_value=df['pubDate'].min().date(), 
    max_value=latest_date.date()
)

end_date = st.sidebar.date_input(
    "Select End Date", 
    default_end_date.date(), 
    min_value=start_date,  # Ensures that end_date is always after start_date
    max_value=latest_date.date()
)

# Filter articles based on selected date range
filtered_df = df[(df['pubDate'].dt.date >= start_date) & (df['pubDate'].dt.date <= end_date)]

# --- Data Manipulation ---
# Convert links into clickable format
def make_clickable(url):
    return f'<a href="{url}" target="_blank">Read Here</a>'

filtered_df['link'] = filtered_df['link'].apply(make_clickable)
filtered_df['pubDate'] = filtered_df['pubDate'].dt.strftime("%b %d, %Y")  # Change to readable date format

# Sort articles by Date of Publishing in descending order
filtered_df = filtered_df.sort_values(by='pubDate', ascending=False)
filtered_df = filtered_df.rename(columns={
    'title': 'Blog Title', 
    'substack': 'Substack', 
    'pubDate': 'Date of Publishing', 
    'link': 'Link'
})

filtered_df = filtered_df[['Blog Title', 'Substack', 'Date of Publishing', 'Link']]
styles = [
    {'selector': 'thead th', 'props': [
        ('background-color', '#F5F5F5'), 
        ('color', '#333'), 
        ('font-weight', 'bold'),
        ('position', 'sticky'),
        ('top', '0'),
        ('z-index', '1'),
        ('text-align', 'left')
    ]},
    {'selector': 'tbody td', 'props': [
        ('padding', '8px'), 
        ('text-align', 'left')  # <- Align body text to left
    ]},
    {'selector': 'tr:nth-child(odd)', 'props': [('background-color', '#f9f9f9')]},
    {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#ffffff')]},
    {'selector': 'tbody tr:hover', 'props': [('background-color', '#e1e1e1')]}
]

# --- Display Filtered Articles ---
st.subheader(f"📝 Found {len(filtered_df)} articles in the time range **{start_date}** to **{end_date}**")
styled_df=filtered_df.style.set_properties(**{'text-align': 'left'}).set_table_styles(styles)

st.write(styled_df.to_html(index=False), unsafe_allow_html=True)
