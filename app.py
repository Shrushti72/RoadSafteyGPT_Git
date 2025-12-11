import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from PIL import Image
import io 
import hashlib 
import random 
from typing import Dict, Any, List
import requests 
import os
from dotenv import load_dotenv
load_dotenv()

# --- CONFIGURATION (MUST be the first Streamlit call) ---
st.set_page_config(
    page_title="RoadSafetyGPT: AI Assistant for Road Safety",
    page_icon="🚦",
    layout="wide"
)

# --- NEW: API Configuration (You MUST replace this placeholder key) ---
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
# --- END NEW CONFIG ---


# --- FONT AWESOME FOR ICONS ---
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
""", unsafe_allow_html=True)


# --- INLINE CSS STYLING (MODIFIED FOR HIGH-CONTRAST PURPLE/YELLOW THEME) ---
CUSTOM_CSS = """
<style>
/* Purple and Yellow Color Palette */
:root {
    --primary-purple: #6C3483; /* MODIFIED: Muted Deep Purple */
    --secondary-yellow: #FFC300; /* Vibrant Yellow/Gold */
    --accent-light: #F4D03F;    /* Light Yellow Accent */
    --background-main: #EDE7F6;  /* NEW: Light Purple (Main Dashboard Background) */
    --background-sidebar: #FFFDE7; /* NEW: Very Light Yellow (Sidebar Background) */
    --background-container: #FFFFFF; /* White for cards/containers (For readability) */
    --text-color: #2C3E50;     /* Dark text */
}

/* 1. Base Font and Background */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html, body, [class*="st-"] {
    font-family: 'Inter', sans-serif;
    color: var(--text-color);
}

/* Main app background: PURPLE */
.stApp {
    background-color: var(--background-main); 
}
/* Ensure Streamlit elements use the correct background */
.stApp > header {
    background-color: var(--background-main);
}
/* All Links/Anchors (a tags) - REMOVING BLUE COLOR */
a {
    color: var(--primary-purple) !important;
}


/* 2. Sidebar background: YELLOW */
[data-testid="stSidebar"] {
    background-color: var(--background-sidebar) !important; 
    border-right: 2px solid var(--secondary-yellow); /* Yellow separation line */
}

/* 3. Top Banner Styling (Retaining dark gradient for title banner) */
.dashboard-header {
    background: linear-gradient(135deg, var(--primary-purple) 0%, #4A235A 100%); 
    color: white;
    padding: 25px 30px; 
    border-radius: 10px;
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.3);
    margin-bottom: 20px;
    border-top: 5px solid var(--secondary-yellow); 
}

/* Headings */
h1 {
    color: white; 
    text-align: center;
    font-size: 2.5rem;
    margin: 0;
}
h2 {
    color: var(--primary-purple); 
    font-weight: 700;
    margin-top: 30px;
    padding-bottom: 10px;
    border-bottom: 2px solid var(--accent-light);
}
h3 {
    color: #555;
    font-weight: 600;
}

/* 4. Tab Styling: YELLOW BACKGROUND */
/* Tab Bar Container (Overall area holding tabs) */
[data-testid="stTabs"] {
    background-color: var(--background-sidebar); /* Light Yellow */
    border-radius: 8px;
    padding: 5px 5px 0 5px;
}

/* Tab Headers (Unselected tabs) */
.stTabs [role="tab"] {
    background-color: #FFF3CD !important; /* Slightly darker yellow for tab headers */
    color: var(--primary-purple) !important;
    border-radius: 5px 5px 0 0 !important;
    border-bottom: 1px solid var(--secondary-yellow) !important;
}

/* Tab Content Background (The area where content is displayed) */
.stTabs [role="tabpanel"] {
    background-color: var(--background-sidebar) !important; /* Very Light Yellow Content Area */
    border-radius: 0 0 8px 8px;
    padding: 20px !important;
    border: 1px solid var(--secondary-yellow);
}

/* Selected Tab Header (Active Tab) */
.stTabs [aria-selected="true"] {
    background-color: var(--background-sidebar) !important; /* Matches content background */
    border-bottom: 3px solid var(--primary-purple) !important; /* Purple underline for active tab */
    color: var(--primary-purple) !important;
}


/* 5. Status Messages - Ensuring no blue (replacing st.info) */
.stSuccess {
    background-color: #D4EDDA !important; /* Greenish success */
    border-left: 5px solid #28A745;
}
.stError {
    background-color: #F8D7DA !important; /* Reddish error */
    border-left: 5px solid #DC3545;
}
.stWarning {
    background-color: #FFF3CD !important; /* Yellow warning */
    border-left: 5px solid var(--secondary-yellow);
}
.stInfo { 
    background-color: #F7E9FF !important; /* Light Purple/Lavender instead of blue */
    border-left: 5px solid var(--primary-purple); /* Purple border */
    color: var(--text-color) !important;
}

/* Other general container styling remains similar */
.stContainer {
    background-color: var(--background-container) !important;
    border: 1px solid #E5E5E5;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    transition: box-shadow 0.3s ease-in-out;
}
.rag-output-container {
    padding: 20px;
    margin-top: 15px;
    border-radius: 10px;
    background-color: var(--background-container); 
    border: 1px solid #e0e0e0;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

/* Button Styling (Primary) */
.stButton>button {
    background-color: #B0A6CC; /* MODIFIED: Light Purple Background */
    color: #2C3E50; /* MODIFIED: Dark Text for contrast */
    font-weight: 600;
    border-radius: 5px;
    border: none;
    transition: background-color 0.3s;
    padding: 8px 15px;
}
.stButton>button:hover {
    background-color: #C6C0D9; /* MODIFIED: Even Lighter Purple for hover */
}

/* 6. Action Plan Container: Purple Theme */
.action-plan-container {
    background: #EBE5F6; /* Very light purple background */
    border: 1px solid var(--primary-purple); 
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 10px 20px rgba(125, 60, 152, 0.2); /* Deep purple shadow */
    margin-top: 20px;
}
/* Style the header for the action plan */
.action-plan-container h2 {
    color: var(--primary-purple);
    border-bottom: 2px solid var(--secondary-yellow); /* Yellow underline */
    padding-bottom: 10px;
}
/* Make the data editor stand out more */
[data-testid="stDataEditor"] {
    border: 1px solid #D1C4E9; /* Light purple border around the editor */
    border-radius: 8px;
}

/* 7. KNOWLEDGE BASE TRANSPARENCY - Data Integrity Container: Dark, Impressive Theme */
.data-integrity-container {
    /* Changed to a dark, professional gradient */
    background: linear-gradient(135deg, #4A235A 0%, var(--primary-purple) 100%); 
    border: 2px solid var(--secondary-yellow);
    padding: 20px;
    border-radius: 12px;
    /* Increased shadow for depth */
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5); 
    margin-top: 20px;
}
/* Style all H2s inside this container to be white/yellow */
.data-integrity-container h2, 
.data-integrity-container h3 {
    color: white !important; /* White text on dark background */
    border-bottom: 1px solid rgba(255, 255, 255, 0.3); /* Lighter divider */
    padding-bottom: 8px;
}
.data-integrity-container .stMarkdown p {
    color: #F0F0F0; /* Light gray for general text */
}
/* Styling the percentage text below the bar chart */
.data-integrity-container .chart-percentages span {
    color: var(--secondary-yellow) !important; /* Make the percentage numbers yellow */
    font-weight: 700;
}

</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# --- INITIALIZE SESSION STATE ---
if 'action_plan' not in st.session_state:
    st.session_state['action_plan'] = []
    st.session_state['action_plan'].append(
    {
        "ID": "MORT-001",
        "Source": "Map",
        "Issue": "Signal Jumping at Bangalore Ring Road",
        "Intervention": "Full Signal Optimization & Rumble Strips",
        "Risk": "Critical",
        "Status": "To Do"
        })
    st.session_state['action_plan'].append(
    {
        "ID": "IRC-002",
        "Source": "RAG",
        "Issue": "Faded markings on NH-19 as per audit report",
        "Intervention": "Thermoplastic re-painting of shoulder lines (IRC:67)",
        "Risk": "High",
        "Status": "In Progress"
    })

# <--- 2. NEW: Initialize weather session state --->
if 'current_weather' not in st.session_state:
    st.session_state['current_weather'] = 'Clear'
if 'last_fetch_status' not in st.session_state: # <--- ADDED FOR PERSISTENCE
    st.session_state['last_fetch_status'] = 'Initial Load'
# <--- END NEW --->


# --- HELPER FUNCTION: CLEAR COMPLETED TASKS ---
def clear_completed_tasks():
    """Filters the action plan to remove tasks marked as 'Completed'."""
    initial_count = len(st.session_state['action_plan'])
    st.session_state['action_plan'] = [
        task for task in st.session_state['action_plan'] if task['Status'] != 'Completed'
    ]
    removed_count = initial_count - len(st.session_state['action_plan'])
    if removed_count > 0:
        st.success(f"{removed_count} completed tasks cleared from the plan.")
    else:
        st.info("No completed tasks to clear.")

# --- RAG ANALYSIS FUNCTION (DUMMY IMPLEMENTATION) ---
def get_rag_answer(query: str) -> Dict[str, Any]:
    """
    Simulates a RAG database lookup and adds a task to the action plan.
    """
    
    # <--- 3. NEW: Access current weather context --->
    current_weather = st.session_state.get('current_weather', 'Clear')
    # <--- END NEW --->
    
    if not query:
        return {
            "error": True, 
            "message": "Please enter a question to query the Knowledge Base."
        }
        
    query_lower = query.lower()
    
    confidence = round(random.uniform(0.85, 0.99), 2)
    
    # <--- 4. NEW: Weather-specific intervention logic --->
    if "fog" in current_weather.lower() or "mist" in current_weather.lower() or "haze" in current_weather.lower():
        risk = "Critical"
        intervention = [
            "**IMMEDIATE FOG INTERVENTION:** Install/verify high-power, retro-reflective **Cat's Eye** road studs for lane delineation (IRC:67 compliant).",
            "Deploy highly visible **Variable Message Signs (VMS)** warning of low visibility, as per MoRTH guidelines.",
            "Enforce a temporary speed limit reduction (e.g., 40%) when visibility drops below 50 meters, citing IRC:SP-50."
        ]
        evidence = (
            f"**CONTEXT-AWARE RECOMMENDATION (Weather: {current_weather}):** IRC:67 mandates retro-reflective elements for night-time/low-visibility driving. Fog-related accidents are often high-severity pile-ups, hence the critical risk assessment. **Confidence: {confidence}**"
        )
        issue = f"High-Risk: Fog/Mist Visibility Issues (Weather: {current_weather})"
    # <--- END NEW: Weather-specific block --->
    
    # Existing logic follows, checking query content only if no critical weather is found.
    elif "zebra" in query_lower or "pedestrian" in query_lower or "crossing" in query_lower:
        risk = "High"
        intervention = [
            "Implement a clear **Zebra Crossing** (IRC:35/IRC:67) with high-visibility thermoplastic paint.",
            "Ensure a minimum of **2.5m clear visibility** distance for approaching vehicles.",
            "Add 'Pedestrian Ahead' warning signs with flashing beacons."
        ]
        evidence = (
            "IRC:67 mandates specific colors and widths for crossings. IRC:35 details pedestrian facilities and safe practices. "
            f"MoRTH data suggests high fatality rates at un-marked crossings. **Confidence: {confidence}**"
        )
        issue = "Un-marked/Faded Pedestrian Crossing (IRC:35/IRC:67 violation)"
        
    elif "speed" in query_lower or "limit" in query_lower or "enforce" in query_lower:
        risk = "Medium-to-High"
        intervention = [
            "Install **Rumble Strips** and clear speed limit signage (IRC:SP-50) on approach to high-risk zones.",
            "Deploy Automated Speed Enforcement (ASE) cameras for continuous monitoring.",
            "Conduct a **3-day speed study** to reassess the zone's design speed."
        ]
        evidence = (
            "IRC:SP-50 provides guidelines for speed breakers and zones. MoRTH circulars recommend ASE for accident blackspots. "
            f"Speeding remains the leading cause of fatal accidents in India. **Confidence: {confidence}**"
        )
        issue = "Inadequate speed control measures (IRC:SP-50 non-compliance)"

    elif "shoulder" in query_lower or "width" in query_lower or "geometry" in query_lower:
        risk = "Medium"
        intervention = [
            "Verify and reconstruct shoulder width to meet **IRC:69 standards** (typically 1.5m to 2.5m paved shoulder on NH/SH).",
            "Maintain clear recovery zones beyond the shoulder to minimize roll-over risk.",
            "Add edge line markings (thermoplastic paint) with minimum 150mm width."
        ]
        evidence = (
            "IRC:69 specifies geometric design standards, including shoulder dimensions and side slopes. "
            "Adequate shoulders reduce run-off-road accidents by providing recovery space. "
            f"Poor geometry contributes to lane departure accidents. **Confidence: {confidence}**"
        )
        issue = "Shoulder width deficiency or lack of clear recovery zone (IRC:69 violation)"
    
    else: 
        risk = "Low-to-Medium"
        random_element = random.choice(["night-time glare mitigation", "wildlife crossings design", "bus bay design compliance", "toll plaza safety procedures"])
        intervention = [
            f"Analyze the specific IRC code for **{random_element}** (IRC:SP-52/IRC:81/IRC:103).",
            "Review the last quarterly safety audit report for this general area.",
            "Conduct a full semantic search on the query to pinpoint the exact IRC clause."
        ]
        evidence = (
            f"The evidence base contains specific sections on **{random_element}** mitigation. A full semantic search across all indexed MoRTH/IRC documents is required to provide maximum precision. "
            f"General safety compliance score check initiated. **Confidence: {confidence}**"
        )
        issue = f"General query about {random_element} standards."

    if "error" not in locals():
        new_task = {
            "ID": f"RAG-{hashlib.md5(query.encode()).hexdigest()[:4].upper()}",
            "Source": "RAG",
            "Issue": issue,
            "Intervention": ", ".join(interv.replace('**', '').replace('.', '') for interv in intervention[:2]), 
            "Risk": risk.replace("-to-", "/"), 
            "Status": "To Do"
        }
        if not any(t['Issue'] == new_task['Issue'] for t in st.session_state['action_plan']):
            st.session_state['action_plan'].append(new_task)

    return {
        "intervention": intervention,
        "evidence": evidence,
        "severity": f"**{risk.replace('-to-', '/')}**"
    }


# --- AI ANALYSIS FUNCTION (DUMMY IMPLEMENTATION) ---
def analyze_road_image(uploaded_file) -> Dict[str, Any]:
    # ... (function body remains unchanged) ...

    if uploaded_file is None:
        return {
            "error": True, 
            "message": "Please upload an image for analysis."
        }

    try:
        image_data = uploaded_file.read()
        unique_file_id = hashlib.sha256(image_data).hexdigest()[:8]
        image = Image.open(io.BytesIO(image_data))
        width, height = image.size
        aspect_ratio = width / height if height > 0 else 0 
        file_size_kb = len(image_data) / 1024
        uploaded_file.seek(0)
    except Exception as e:
        return {
            "error": True, 
            "message": f"Error reading image properties: {e}. Check file format."
        }
    
    filename = uploaded_file.name
    analysis_key = ""

    if file_size_kb > 500 or "accident" in filename.lower() or aspect_ratio < 0.7:
        analysis_key = "accident"
    elif aspect_ratio > 1.8 and file_size_kb > 100: 
        analysis_key = "urban"
    elif file_size_kb < 100: 
        analysis_key = "signage"
    else:
        analysis_key = "general"
    
    base_report = {
        "unique_id": unique_file_id,
        "size": f"{file_size_kb:.2f} KB",
        "resolution": f"{width}x{height}",
        "aspect_ratio": f"{aspect_ratio:.2f}",
    }

    if analysis_key == "accident":
        risk_summary = "**CRITICAL** Immediate emergency response and full investigation (IRC:SP-55)."
        identified_issues = [
            f"**CRITICAL INCIDENT DETECTED** (ID: {unique_file_id}). Immediate action required.",
            "Likely cause: Speeding, Loss of control, or Road Hazard. Requires on-site investigation.",
            "Road surface friction analysis required based on tire marks observed.",
        ]
        risk_level = "Critical"

    elif analysis_key == "urban":
        risk_summary = "**HIGH** risk of low-speed accidents and pedestrian injury."
        identified_issues = [
            f"**High Congestion & Conflict** (ID: {unique_file_id}) and pedestrian conflict observed.",
            "Missing or faded pedestrian crossing markings (IRC:35/IRC:67). High-risk.",
            "Traffic mix (autos, bikes, cycles) suggests complex flow management issues.",
        ]
        risk_level = "High"

    elif analysis_key == "signage":
        risk_summary = "**MEDIUM** risk due to insufficient driver guidance."
        identified_issues = [
            f"**Signage/Marking Deficiency** (ID: {unique_file_id}) detected.",
            "Low retro-reflectivity or physical damage to sign confirmed (IRC:67 violation).",
            "Vegetation encroachment potentially obscuring driver visibility.",
        ]
        risk_level = "Medium"

    else: # general
        risk_summary = "**LOW** risk, routine maintenance priority."
        identified_issues = [
            f"**General Roadway Check** (ID: {unique_file_id}).",
            "Pavement condition appears fair; monitor for early signs of distress (IRC:37).",
            "Compliance check for shoulder width and horizontal curve radius initiated.",
        ]
        risk_level = "Low"
    
    suggested_interventions = [
        "Dispatch emergency services and secure the scene." if analysis_key == "accident" else
        "Install high-visibility pedestrian markings and signals." if analysis_key == "urban" else
        "Immediate replacement of the damaged/faded element (IRC:67 compliance)." if analysis_key == "signage" else
        "Schedule minor pavement crack sealing and preventative maintenance.",
        
        "Review approach speed limits and warning signage for visibility." if analysis_key == "accident" else
        "Enforce 'No Parking' zones to ensure clear sight distances." if analysis_key == "urban" else
        "Clear vegetation or obstacles within the clear zone." if analysis_key == "signage" else
        "Conduct quarterly inspection for debris accumulation and drainage system function.",

        "Schedule a detailed safety audit for this precise location." if analysis_key == "accident" else
        "Consider dedicated non-motorized transport lanes (NMT) for segregation." if analysis_key == "urban" else
        "Verify sign placement height and offset from the carriageway." if analysis_key == "signage" else
        "Monitor for speed violations during non-peak hours using existing systems."
    ]


    new_task = {
        "ID": f"VIS-{unique_file_id[:4].upper()}",
        "Source": "Vision AI",
        "Issue": identified_issues[1].replace('**', ''), 
        "Intervention": suggested_interventions[0].replace('.', ''),
        "Risk": risk_level,
        "Status": "To Do"
    }
    if not any(t['Issue'] == new_task['Issue'] for t in st.session_state['action_plan']):
        st.session_state['action_plan'].append(new_task)

    identified_issues.insert(0, f"**FILE TRACE ID:** `{base_report['unique_id']}` | **Size:** {base_report['size']} | **Resolution:** {base_report['resolution']}")
    
    return {
        "identified_issues": identified_issues,
        "risk_summary": risk_summary,
        "suggested_interventions": suggested_interventions
    }


# --- GEOGRAPHICAL RISK DATA ---
RISK_ZONES = [
# ... (existing RISK_ZONES data remains unchanged) ...
    {"lat": 28.6139, "lon": 77.2090, "name": "Delhi Blackspot (NH-44)", "risk": "High", "color": "red", 
     "road_type": "Highway", "weather": ["Clear", "Fog"],
     "popup_text": "Predicted Cause: **Fatal Rear-End Collisions**. Intervention: **Speed Cameras, IRC:67 audit**."},
    {"lat": 12.9716, "lon": 77.5946, "name": "High-Risk Zone: Bangalore Ring Road", "risk": "Critical", "color": "darkred", 
     "road_type": "Urban", "weather": ["Clear", "Rain"],
     "popup_text": "Predicted Cause: **Signal Jumping**, Low Visibility. Intervention: **Full Signal Optimization & Rumble Strips**."},
    {"lat": 30.7333, "lon": 76.7794, "name": "Chandigarh Curve (NH-5)", "risk": "Medium", "color": "orange", 
     "road_type": "Highway", "weather": ["Clear"],
     "popup_text": "Predicted Cause: Sharp Curve, Insufficient Superelevation. Intervention: **Install larger cautionary signs**."},
    {"lat": 18.5204, "lon": 73.8567, "name": "Pune Highway (Mumbai-Pune)", "risk": "Low", "color": "green", 
     "road_type": "Highway", "weather": ["Rain", "Clear"],
     "popup_text": "Predicted Cause: Debris/Poor Drainage. Intervention: **Routine Sweep, Drainage Check**."},
    {"lat": 23.0225, "lon": 72.5714, "name": "Ahmedabad Intersection", "risk": "High", "color": "red",
     "road_type": "Urban", "weather": ["Clear"],
     "popup_text": "Predicted Cause: Pedestrian Conflict. Intervention: **Install Traffic Guards, High-Vis Zebra**."},
    {"lat": 22.5726, "lon": 88.3639, "name": "Kolkata Bypass Crossing", "risk": "Medium", "color": "orange",
     "road_type": "Urban", "weather": ["Clear", "Rain"],
     "popup_text": "Predicted Cause: Unregulated turnings. Intervention: **Install barrier and clear signage**."},
    {"lat": 19.0760, "lon": 72.8777, "name": "Mumbai Western Express Highway", "risk": "Critical", "color": "darkred",
     "road_type": "Urban", "weather": ["Rain"],
     "popup_text": "Predicted Cause: **High Volume, Lane Changing**. Intervention: **Mandatory Lane Discipline Enforcement**."},
    {"lat": 13.0827, "lon": 80.2707, "name": "Chennai Outer Ring Road", "risk": "High", "color": "red",
     "road_type": "Highway", "weather": ["Clear", "Rain"],
     "popup_text": "Predicted Cause: **Night-time Blind Spots**, Missing Glare Screens. Intervention: **Install High-Mast Lights**."},
    {"lat": 17.3850, "lon": 78.4867, "name": "Hyderabad Tank Bund Road", "risk": "Medium", "color": "orange",
     "road_type": "Residential", "weather": ["Clear"],
     "popup_text": "Predicted Cause: **Unauthorized Parking**, Sight Distance Obstruction. Intervention: **Tow-Away Zones, Clear Visibility**."},
]

@st.cache_data
def create_folium_map(risk_filter: str, road_type_filter: str, weather_filter: str):
# ... (function body remains unchanged) ...
    """
    Creates a Folium map, filtering markers based on the selected risk level,
    road type, and weather condition.
    """
    # Centered near New Delhi
    m = folium.Map(location=[28.7041, 77.1025], zoom_start=6) 
    
    folium.TileLayer('cartodbpositron', name='Light Basemap').add_to(m)
    folium.TileLayer('OpenStreetMap', name='Detailed Streets').add_to(m)
    
    marker_group = folium.FeatureGroup(name="Safety Risk Zones").add_to(m)

    filtered_zones = RISK_ZONES
    
    # 1. Filter by Risk Level
    if risk_filter != "All Risk Levels":
        filtered_zones = [zone for zone in filtered_zones if zone['risk'] == risk_filter]

    # 2. Filter by Road Type
    if road_type_filter != "All Road Types":
        filtered_zones = [zone for zone in filtered_zones if zone['road_type'] == road_type_filter]

    # 3. Filter by Weather
    if weather_filter != "All Conditions":
        filtered_zones = [zone for zone in filtered_zones if weather_filter in zone['weather']]

    for zone in filtered_zones:
        icon_color = zone["color"]
        icon_name = "flag" if zone['risk'] == "Critical" else ("exclamation-triangle" if zone['risk'] == "High" else "info-circle")
        
        popup_html = f"<b>{zone['name']}</b><br>Risk: <span style='color:{icon_color}; font-weight:bold;'>{zone['risk']}</span><br>Road Type: {zone['road_type']}<br>Weather: {', '.join(zone['weather'])}<br>{zone.get('popup_text', 'Monitor traffic flow.')}"
        
        folium.Marker(
            location=[zone["lat"], zone["lon"]], 
            popup=folium.Popup(popup_html, max_width=300), 
            icon=folium.Icon(color=icon_color, icon=icon_name, prefix='fa')
        ).add_to(marker_group)
        
    folium.LayerControl().add_to(m)
    
    return m

# --- SIDEBAR FOR FILTERING & GUIDE (UPDATED) ---

# --- SHECODES TEAM BRANDING (NEW IMAGE LOGO) ---
# FIX 1: Corrected the path to be relative to the project root, 
# FIX 1: which requires including the 'app/' directory.
# Assuming your image is at: ROADSAFETYGPT/app/images/logo.jpeg
LOGO_PATH = "app/images/logo.jpeg" 

st.sidebar.markdown("---")

# FIX 2: Using st.sidebar.image is more robust for local files than raw HTML markdown.
try:
    st.sidebar.image(
        LOGO_PATH, 
        # FIX 3: Using the current best practice parameter (use_container_width=True)
        use_container_width=True
    )
except FileNotFoundError:
    # Provides a useful error if the image is still not found at the expected path
    st.sidebar.error(f"Error: Logo file not found. Ensure '{LOGO_PATH}' exists.")
except Exception:
    st.sidebar.error("Error displaying image. Check file permissions or format.")

st.sidebar.markdown("---")

# --- END SHECODES TEAM BRANDING ---

st.sidebar.header("Map Filter")
risk_level_options = ["All Risk Levels", "Critical", "High", "Medium", "Low"]
selected_risk_level = st.sidebar.selectbox(
    "Filter Zones by Predicted Risk:",
    options=risk_level_options,
    key="map_risk_filter"
)

# NEW FILTER 1: Road Type
road_type_options = ["All Road Types", "Highway", "Urban", "Residential"]
selected_road_type = st.sidebar.selectbox(
    "Filter by Road Type:",
    options=road_type_options,
    key="map_road_type_filter"
)

# NEW FILTER 2: Weather Conditions
weather_options = ["All Conditions", "Clear", "Rain", "Fog"]
selected_weather = st.sidebar.selectbox(
    "Filter by Contributing Weather:",
    options=weather_options,
    key="map_weather_filter"
)

st.sidebar.markdown("---")
st.sidebar.header("App Guide")
st.sidebar.info(
    "**Knowledge Base (RAG):** Ask IRC/MoRTH compliance questions to get a safety recommendation.\n\n"
    "**Image Analysis:** Upload a road photo (e.g., of a sign or a junction) for instant fault detection and compliance checks.\n\n"
    "**Action Plan:** All identified issues automatically populate this table for prioritization and tracking."
)


# --- 1. TOP BANNER AND METRICS ---

# Styled Banner Title (Using the dark gradient CSS class)
st.markdown("""
<div class="dashboard-header">
    <h1 style="color: white; margin: 0; font-size: 2.5rem;">
        <i class="fas fa-traffic-light"></i> RoadSafetyGPT
    </h1>
    <p style="margin: 5px 0 0 0; font-size: 1.1rem; font-weight: 300; text-align: center;">
        AI Assistant for Indian Road Safety & Compliance (IRC/MoRTH)
    </p>
</div>
""", unsafe_allow_html=True)


col1, col2, col3 = st.columns(3)

# DUMMY DATA 
kpi_data = {
    "Potential Risk Reduction": {"value": "24%", "delta": 2, "delta_color": "normal"}, 
    "Accidents Predicted This Month": {"value": "12", "delta": -8, "delta_color": "inverse"}, 
    "IRC Compliance Score": {"value": "91%", "delta": 3, "delta_color": "normal"}, 
}

# Displaying KPIs
with col1:
    st.metric(label="Potential Risk Reduction", 
              value=kpi_data["Potential Risk Reduction"]["value"], 
              delta=f"+{kpi_data['Potential Risk Reduction']['delta']}% ⬆️")
    
with col2:
    st.metric(label="Accidents Predicted This Month", 
              value=kpi_data["Accidents Predicted This Month"]["value"], 
              delta=f"{abs(kpi_data['Accidents Predicted This Month']['delta'])} Cases ⬇️", 
              delta_color='inverse') 

with col3:
    st.metric(label="IRC Compliance Score", 
              value=kpi_data["IRC Compliance Score"]["value"], 
              delta=f"+{kpi_data['IRC Compliance Score']['delta']} Pts ⬆️")

st.markdown("<br>", unsafe_allow_html=True) 

# <--- 5. NEW SECTION: REAL-TIME CONTEXTUAL INPUT (To make RAG Adaptive) --->
st.markdown("## 🌦 Real-Time Contextual Input (Enhances RAG Precision)", unsafe_allow_html=True)

col_loc, col_btn = st.columns([4, 1])

with col_loc:
    location_input = st.text_input(
        "Enter City/Location to Fetch Real-Time Weather:", 
        "New Delhi, India",
        key="weather_location_input",
        label_visibility="collapsed"
    )

with col_btn:
    weather_fetch_btn = st.button("🌦 Fetch Weather", key="fetch_weather_btn")

# -------------------------------------------------------------------------
# START: WEATHER FETCH LOGIC
if weather_fetch_btn:
    # Set a temporary loading status
    st.session_state['last_fetch_status'] = 'Fetching live weather data...' 
    
    if WEATHER_API_KEY == "d7618eeb28c090eeeb14e936927691d4":
        st.session_state['last_fetch_status'] = "⚠️ **API Key Placeholder**: Please replace the placeholder key in `app.py` with your actual key to enable real-time fetching."
        st.session_state['current_weather'] = "Clear (API Key Placeholder)"
    else:
        try:
            with st.spinner('Fetching live weather data...'):
                params = {
                    'q': location_input,
                    'appid': WEATHER_API_KEY,
                    'units': 'metric'
                }
                response = requests.get(WEATHER_API_URL, params=params, timeout=10)

                # Check for 401 (API Key Inactive/Invalid) and 404 (City Not Found) first
                if response.status_code == 401:
                    try:
                        api_message = response.json().get('message', 'Invalid API key or key not yet active.')
                    except:
                        api_message = 'Invalid API key or key not yet active. Response was not JSON.'
                    
                    st.session_state['last_fetch_status'] = f"❌ **API Key Error (401)**: {api_message}. Please ensure your key is correct and fully activated (may take up to 2 hours)."
                    st.session_state['current_weather'] = "Clear (API Key Error)"
                    st.rerun() # FIX: Replaced st.experimental_rerun()
                    
                
                if response.status_code == 404:
                    try:
                        api_message = response.json().get('message', 'City not found.')
                    except:
                        api_message = 'City not found. Response was not JSON.'
                        
                    st.session_state['last_fetch_status'] = f"❌ **Location Error (404)**: {api_message}. Please check the spelling of the location."
                    st.session_state['current_weather'] = "Clear (Location Not Found)"
                    st.rerun() # FIX: Replaced st.experimental_rerun()
                    # FIX: Removed the invalid 'return' statement
                    
                
                # Raise an exception for all other HTTP errors (e.g., 500 server error)
                response.raise_for_status() 
                
                # Only proceed to parse JSON if the status is 200 OK
                weather_data = response.json()

                # Extract relevant weather condition
                main_weather = weather_data['weather'][0]['main'] # e.g., 'Clouds', 'Rain', 'Mist'
                description = weather_data['weather'][0]['description']
                temp = round(weather_data['main']['temp']) # FIX: Rounding temperature
                
                # Store the weather condition and description for use in the RAG prompt/logic
                weather_string = f"{main_weather} ({description})"
                st.session_state['current_weather'] = weather_string
                
                # Store success message in session state
                st.session_state['last_fetch_status'] = f"Weather context updated for **{location_input}**: **{weather_string}** | Temperature: {temp}°C"
                st.rerun() # FIX: Replaced st.experimental_rerun()
        
        except requests.exceptions.RequestException as e:
            # Store error message
            st.session_state['last_fetch_status'] = f"Could not connect to the API. Check your network or base URL. Error: {e}"
            st.session_state['current_weather'] = "Clear (Connection Error)"
        except Exception as e:
            # Store error message
            st.session_state['last_fetch_status'] = f"An unexpected programming error occurred: {e}"
            st.session_state['current_weather'] = "Clear (Unknown Error)"
# END: WEATHER FETCH LOGIC
# -------------------------------------------------------------------------

# --- Display Persistent Status Message (FIX 2b) ---
if st.session_state['last_fetch_status'] != 'Initial Load':
    # Check if the message is a success message
    if st.session_state['last_fetch_status'].startswith('Weather context updated'):
        st.success(st.session_state['last_fetch_status'])
    # Check if the message is an error or warning (starting with ❌ or ⚠️)
    elif st.session_state['last_fetch_status'].startswith(('❌', '⚠️')):
        st.error(st.session_state['last_fetch_status'])
    # If it's a non-critical error or simple message, show it as info
    elif st.session_state['last_fetch_status'] != 'Fetching live weather data...':
        st.info(st.session_state['last_fetch_status'])


st.caption(f"Current Weather Context: **{st.session_state['current_weather']}** (This context is used by the RAG bot.)")

st.markdown("---") 
# <--- END NEW WEATHER INPUT --->


# --- 2. AI INTERVENTION TABS (RAG & Multimodal) ---
with st.container():
    st.markdown("## 🧠 AI-Powered Safety Insights", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📚 Knowledge Base (RAG)", "📸 Multimodal Image Analysis"])

    # --- RAG TAB (Query Bot) ---
    with tab1:
        # NEW: Use a two-column structure for RAG input and output
        rag_input_col, rag_output_col = st.columns([1, 1])

        with rag_input_col:
            st.markdown(f"### Ask an IRC/MoRTH Question")
            st.info(f"The AI will use the weather context: **{st.session_state['current_weather']}**", icon="💡")

            if 'rag_result' not in st.session_state:
                st.session_state['rag_result'] = None
            
            # Use columns for text input and button for better alignment
            q_input_col, q_btn_col = st.columns([4, 1])
            
            with q_input_col:
                question = st.text_area(
                    "RAG Query Input", 
                    placeholder="e.g., What are the safety standards for zebra crossings as per IRC:67?",
                    key="rag_query_input_text", 
                    height=150, # Made the input box larger
                    label_visibility="collapsed",
                )
            
            with q_btn_col:
                st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True) # Spacer for button alignment
                rag_button = st.button("🔍 Get RAG Answer", key="get_rag_answer_btn")


        with rag_output_col:
            st.markdown(f"### AI Compliance Recommendation")
            
            if rag_button:
                if question:
                    with st.spinner('Querying IRC/MoRTH knowledge base...'):
                        rag_output = get_rag_answer(question)
                        st.session_state['rag_result'] = rag_output
                else:
                    st.warning("Please enter a question.")
            
            if st.session_state['rag_result']:
                result = st.session_state['rag_result']
                
                if "error" in result:
                    st.error(result["message"])
                else:
                    st.markdown(
                        f"""
                        <div class="rag-output-container">
                            <p class="rag-subheader"><i class="fas fa-tools"></i> Suggested Intervention (IRC/MoRTH Compliant)</p>
                            <ul>
                                {(''.join(f'<li>{interv}</li>' for interv in result['intervention']))}
                            </ul>
                            <p class="rag-subheader"><i class="fas fa-book"></i> Evidence Base & Confidence</p>
                            <p>{result['evidence']}</p>
                            <p class="rag-severity"><i class="fas fa-exclamation-triangle"></i> Severity/Impact Prediction: {result['severity']}</p>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
            else:
                # Placeholder content moved to a separate container for better styling
                st.markdown("""
                <div class="rag-output-container">
                    <p class="rag-subheader"><i class="fas fa-tools"></i> Suggested Intervention</p>
                    <ul>
                        <li>(Answer will appear here, grounded in official IRC and MoRTH documents.)</li>
                    </ul>
                    <p class="rag-subheader"><i class="fas fa-book"></i> Evidence Base (from IRC/MoRTH)</p>
                    <p>IRC/MoRTH codes and reports are indexed and ready for semantic search. Ask about standards, compliance, or best practices.</p>
                    <p class="rag-severity"><i class="fas fa-exclamation-triangle"></i> Risk Summary: **Pending**</p>
                </div>
                """, unsafe_allow_html=True)


    # --- MULTIMODAL TAB (Image Analysis) ---
    with tab2:
        st.markdown("Upload an image of a road segment for AI analysis against safety standards and geometric compliance.", unsafe_allow_html=True)
        
        if 'analysis_result' not in st.session_state:
            st.session_state['analysis_result'] = None
        
        # NEW: Use a two-column structure for image input/display and analysis report
        image_col, text_col = st.columns([1, 1])
        
        with image_col:
            st.markdown("### Image Upload & Preview")
            
            uploaded_file = st.file_uploader(
                "Drag and drop image file here (JPG, JPEG, PNG)", 
                type=["jpg", "jpeg", "png"], 
                key="uploader_tab2",
                label_visibility="collapsed" 
            )
            
            if uploaded_file is not None:
                # Display image in a clean container
                st.image(uploaded_file, caption=f"Image for AI Analysis: {uploaded_file.name}", use_container_width=True)
            else:
                st.info("No image uploaded. Try dropping one above.")
                st.markdown("<div style='height: 250px;'></div>", unsafe_allow_html=True) # Spacer for balance


        with text_col:
            st.markdown("### AI Analysis Report")
            analyze_btn_col, _ = st.columns([0.4, 0.6])
            with analyze_btn_col:
                analyze_button = st.button("✨ Run AI Analysis", key="run_analysis_btn")
            
            if analyze_button:
                if uploaded_file is not None:
                    st.session_state['analysis_result'] = None 
                    with st.spinner(f'Analyzing {uploaded_file.name} against IRC/MoRTH standards...'):
                        analysis_output = analyze_road_image(uploaded_file)
                        st.session_state['analysis_result'] = analysis_output
                else:
                    st.warning("Please upload an image before running the analysis.")

            if st.session_state['analysis_result']:
                result = st.session_state['analysis_result']
                
                if "error" in result:
                    st.error(result["message"])
                else:
                    st.markdown(
                        f"""
                        <div class="rag-output-container">
                            <p class="rag-subheader"><i class="fas fa-bug"></i> Identified Issues & Traceability</p>
                            <ul>
                                {(''.join(f'<li>{issue}</li>' for issue in result['identified_issues']))}
                            </ul>
                            <p class="rag-subheader"><i class="fas fa-screwdriver"></i> Suggested Interventions (Actionable Steps)</p>
                            <ul>
                                {(''.join(f'<li>{interv}</li>' for interv in result['suggested_interventions']))}
                            </ul>
                            <p class="rag-severity"><i class="fas fa-exclamation-triangle"></i> Risk Summary: {result['risk_summary']}</p>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
            else:
                # Placeholder content
                st.markdown("""
                <div class="rag-output-container">
                    <p class="rag-subheader"><i class="fas fa-bug"></i> AI Analysis Report Status</p>
                    <p>The AI will perform a real-time assessment of the road environment, identifying potential compliance issues (e.g., faded markings, geometry faults, obstruction) and generating a risk summary.</p>
                    <p class="rag-severity"><i class="fas fa-exclamation-triangle"></i> Risk Summary: **Pending**</p>
                </div>
                """, unsafe_allow_html=True)


# --- 3. GEOGRAPHICAL RISK ANALYSIS (FOLIUM MAP) ---
st.markdown("<br>", unsafe_allow_html=True) 

with st.container():
    st.markdown("## 🌍 Geographical Risk Analysis (AI Prediction)")
    
    # Removed the column structure to allow the map to take full width
    m = create_folium_map(selected_risk_level, selected_road_type, selected_weather)
    # FIX APPLIED HERE: use_container_width=True ensures the map spans the full width of the container.
    st_folium(m, height=500, use_container_width=True) 

    st.markdown("""
    <div class="risk-summary-container" style="margin-top: 5px;">
        <p class="risk-summary-text">
            <i class="fas fa-map-marker-alt"></i> <strong>Key Intervention Priority: Bangalore Ring Road</strong> 
            <br>Predicted Cause: Signal Jumping, Gravel on surface, Low Visibility at night.
            <br>Suggested Intervention: **Full Signal Optimization, Install Pre-Junction Rumble Strips, and Pavement Repair (IRC:37/IRC:93 Compliance).**
        </p>
    </div>
    """, unsafe_allow_html=True)
    
st.markdown("---")

# --- 4. ACTION PLANNING AND PRIORITIZATION ---
st.markdown('<div class="action-plan-container">', unsafe_allow_html=True) # <-- NEW WRAPPER START
with st.container():
    st.markdown("## 📝 Action Planning and Prioritization")
    st.markdown("Review and manage the issues automatically generated from the **Geographical Analysis**, **RAG**, and **Vision AI** tabs.")
    
    clear_col, _ = st.columns([0.2, 0.8])
    with clear_col:
        st.button("🧹 Clear Completed Tasks", on_click=clear_completed_tasks, key="clear_tasks_btn")

    action_df = pd.DataFrame(st.session_state['action_plan'])
    
    if not action_df.empty:
        key_suffix = len(action_df) 
        
        column_config = {
            "ID": st.column_config.TextColumn("Trace ID", disabled=True),
            "Source": st.column_config.TextColumn("Source", disabled=True),
            "Issue": st.column_config.TextColumn("Identified Issue", help="The compliance issue reported by AI systems."),
            "Intervention": st.column_config.TextColumn("Suggested Action", help="The primary intervention required (e.g., install sign, repave)."),
            "Risk": st.column_config.SelectboxColumn(
                "Risk Level",
                options=["Low", "Medium", "High", "Critical"],
                required=True,
                help="The severity level of the issue, editable for prioritization."
            ),
            "Status": st.column_config.SelectboxColumn(
                "Status",
                options=["To Do", "In Progress", "Completed", "Deferred"],
                required=True,
                help="The current status of the corrective action."
            ),
        }
        
        edited_df = st.data_editor(
            action_df,
            column_config=column_config,
            hide_index=True,
            num_rows="dynamic",
            use_container_width=True, # Recommended best practice
            key=f"action_plan_editor_{key_suffix}"
        )
        
        try:
            if not action_df.equals(edited_df):
                st.session_state['action_plan'] = edited_df.to_dict('records')
        except Exception:
            pass
            

    else:
        st.info("The Action Plan is currently empty. Run a RAG query or an Image Analysis to automatically populate tasks.")
st.markdown('</div>', unsafe_allow_html=True) # <-- NEW WRAPPER END
st.markdown("---")

# --- 5. COMPARATIVE VIEWS ---
with st.container():
    st.markdown("## 📈 Comparative Views (Year-over-Year Analysis)")
    st.info("This section provides a simulated comparison of key safety metrics between two selected periods.")
    
    col_period1, col_period2 = st.columns(2)
    
    with col_period1:
        st.markdown("### **Period 1: Q3 2024 (Current)**")
        st.metric(label="Total Incidents", value="452", delta="18% ⬆️ vs. Period 2", delta_color="inverse")
        st.metric(label="Fatalities", value="38", delta="-5% ⬇️ vs. Period 2", delta_color="normal")
    
    with col_period2:
        st.markdown("### **Period 2: Q3 2023 (Baseline)**")
        st.metric(label="Total Incidents", value="383", delta="-18% ⬇️ vs. Period 1", delta_color="normal")
        st.metric(label="Fatalities", value="40", delta="+5% ⬆️ vs. Period 1", delta_color="inverse")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Simulated Comparative Chart
    # Create a data structure for a STACKED BAR CHART
    stacked_data = pd.DataFrame({
        'Period': ['Q3 2023 (Baseline)', 'Q3 2024 (Current)'],
        'Fatalities': [40, 38],
        'Serious Injuries': [155, 170],
        'Minor Injuries': [188, 244]
    }).set_index('Period') # Set Period as index for bar chart categories.

    # Using the same theme colors: Red (#C0392B), Purple (#6C3483), Yellow (#FFC300)
    st.bar_chart(
        stacked_data,
        color=["#C0392B", "#6C3483", "#FFC300"]
    )
    
    st.caption("Stacked bar chart showing the total and distribution of accident severity by period. **Note the rise in Minor Injuries (Yellow) leading to a higher overall incident count.**")

st.markdown("---")

# --- 6. KNOWLEDGE BASE TRANSPARENCY (Refined for aesthetic) ---
coverage_data = pd.DataFrame({
    'Source': ['MoRTH Reports', 'IRC Codes', 'NCRB Data'], 
    'Count': [450, 35, 15]
})
confidence_points = {
    'Confidence (77-100%)': [0.70, 0.74, 0.76, 0.80, 0.84, 0.88, 0.90, 0.92, 0.96, 1.00], 
    'Frequency': [100, 80, 100, 120, 150, 100, 180, 220, 400, 50]
}
confidence_match_df = pd.DataFrame(confidence_points)

# Use the custom CSS class to style this section container
st.markdown('<div class="data-integrity-container">', unsafe_allow_html=True)
st.markdown("## ⚠ Data Integrity & Transparency")

col_data_coverage, col_model_confidence = st.columns(2)

with col_data_coverage:
    st.markdown("### Indexed Document Coverage")
    
    # Use the secondary yellow color for the bars to stand out on the dark background
    st.bar_chart(coverage_data, x='Source', y='Count', color='#FFC300') 
    
    # Wrap the percentages in a new div for the CSS change (Step 1)
    st.markdown("""
    <div class="chart-percentages" style="display:flex; justify-content: space-around; font-size: 0.8rem; color: #555; margin-top: -10px;">
        <span style="flex:1; text-align:center;">~60%</span>
        <span style="flex:1; text-align:center;">~25%</span>
        <span style="flex:1; text-align:center;">~15%</span>
    </div>
    """, unsafe_allow_html=True)

with col_model_confidence:
    st.markdown("### Model Confidence Distribution")
    
    # Use white color for the line to stand out clearly
    st.line_chart(confidence_match_df, x='Confidence (77-100%)', y='Frequency', color='#FFFFFF')

st.markdown('</div>', unsafe_allow_html=True)
st.info("Transparency Note: The charts above represent the simulated coverage and confidence levels of the internal RAG knowledge base, ensuring users understand the breadth and reliability of the AI's recommendations.")

st.markdown("---")