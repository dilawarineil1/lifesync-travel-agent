import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import io

# --- CONFIGURATION ---
SYSTEM_INSTRUCTION = """
# ROLE
You are LifeSync, a sophisticated Travel Agentic Assistant. Your goal is to turn "messy" user travel vibes into high-utility, verified itineraries.

# OPERATIONAL PIPELINE
1. RESEARCH: Use the Google Search tool to find 3-5 specific venues that exist and are currently open.
2. FILTER: Cross-reference findings with user "vibes" (e.g., hidden gems vs tourist traps).
3. WEATHER: Briefly check current conditions to provide a clothing tip.

# OUTPUT FORMAT
- Start with a "Vibe Summary."
- Present the itinerary in a clean Markdown Table.
- Include a section for "Clothing & Packing Tip" based on current weather.
- End with a "Sources & Verification" section listing the URLs used.
"""

# Initialize Gemini Client
client = genai.Client(api_key="AIzaSyAzIRT9U_pzqxrRTEKEA9WMslpUOVm1MDM")

# --- HELPER FUNCTIONS ---
# def display_interactive_itinerary(response):
#     text = response.text
    
#     if "|" in text:
#         try:
#             # 1. Clean the text: Remove all double asterisks from the raw string
#             # This handles the **Venue** issue before it even hits pandas
#             clean_text = text.replace("**", "")
            
#             # 2. Extract the table lines
#             table_lines = [line for line in clean_text.split('\n') if "|" in line]
#             table_str = "\n".join(table_lines)
            
#             # 3. Read the table, skipping the Markdown alignment row
#             # skiprows=[1] removes that pesky second row of dashes
#             df = pd.read_csv(
#                 io.StringIO(table_str), 
#                 sep="|", 
#                 skipinitialspace=True,
#                 skiprows=[1] 
#             ).dropna(axis=1, how='all')
            
#             # 4. Clean up column names and whitespace
#             df.columns = df.columns.str.strip()
#             df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

#             # ... rest of your link-making code ...
#             def make_google_maps_link(venue):
#                 query = str(venue).replace(" ", "+")
#                 return f"https://www.google.com/maps/search/?api=1&query={query}"

#             df['Maps Link'] = df['Venue'].apply(make_google_maps_link)

#             st.subheader("📍 Verified Itinerary & Navigation")
#             st.dataframe(
#                 df,
#                 column_config={
#                     "Maps Link": st.column_config.LinkColumn("Navigate", display_text="Open 🗺️"),
#                 },
#                 hide_index=True,
#                 use_container_width=True
#             )
            
#         except Exception as e:
#             st.markdown(text) # Fallback
#     else:
#         st.markdown(text)

# --- STREAMLIT UI ---
st.set_page_config(page_title="LifeSync Agent", page_icon="✈️", layout="wide")

with st.sidebar:
    st.title("Settings")
    model_choice = st.selectbox("Intelligence Engine", ["Gemini 3 Flash"])
    st.info("Agent is currently grounded with Google Search.")
    st.divider()
    st.image("https://upload.wikimedia.org/wikipedia/commons/d/da/Google_Travel_logo.png", width=100)
    
st.title("✈️ LifeSync: Smart Itinerary Agent")
st.markdown("Convert your travel 'vibes' into a verified plan using real-time search data.")

# User Input Section
user_vibe = st.text_area(
    "Where are you going and what's the vibe?",
    placeholder="Example: 3 days in London, love Harry Potter and cheap pasta, hate tourist traps."
)

if st.button("Build My Verified Itinerary", type="primary"):
    if not user_vibe:
        st.warning("Please enter your travel details first!")
    else:
        with st.spinner("🕵️ Agent is researching live locations and weather..."):
            try:
                # API Call with Grounding Enabled
                response = client.models.generate_content(
                    model="gemini-3-flash-preview",
                    contents=user_vibe,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        tools=[types.Tool(google_search=types.GoogleSearch())],
                        temperature=0.7
                    )
                )

                # Display Results
                st.markdown("### Your Custom Itinerary")
                st.write(response.text)

                # Dev Mode: Grounding Proof for Resume
                metadata = response.candidates[0].grounding_metadata
                if metadata and metadata.search_entry_point:
                    with st.expander("🛠️ View Grounding Metadata (Dev Mode)"):
                        st.json(metadata.web_search_queries)
                        st.write("Full Grounding Metadata Object:", metadata)

            except Exception as e:
                st.error(f"An error occurred: {e}")