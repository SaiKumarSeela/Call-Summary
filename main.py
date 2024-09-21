import streamlit as st
import pandas as pd

def main():
    st.set_page_config(layout="wide")
    
    # Custom CSS for centering content and styling clickable headers
    st.markdown("""
    <style>
    .stButton > button {
        background-color: transparent; /* No background */
        border: none;                  /* No border */
        color: white !important;       /* Default text color */
        font-weight: bold;             /* Bold text */
        cursor: pointer;               /* Pointer cursor on hover */
    }
    .stButton > button:hover {
        color: #e6e6e6 !important;     /* Hover color */
        text-decoration: underline;    /* Underline on hover */
    }
    .selected {
        color: red !important;         /* Text color when selected */
        text-decoration: underline;     /* Underline when selected */
    }
    .transcript-line {
        border-bottom: 1px solid #e6e6e6;
        padding-bottom: 10px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("Transcript Analysis App")

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<p class="column-header">🗣️ Transcription</p>', unsafe_allow_html=True)
        show_transcription()
    
    # Create columns for clickable subheaders
    with col2:
        cols = st.columns(4)
        sections = ["📌Topics", "🗣️Intents", "📒Summary", "📊Stats"]
        
        # Create buttons that look like text for section selection
        if 'selected_section' not in st.session_state:
            st.session_state.selected_section = "📌Topics"  # Default selection
        
        for i, section in enumerate(sections):
            # Check if the current section is selected
            is_selected = st.session_state.selected_section == section
            
            # Create the button and check if it was clicked
            if cols[i].button(section, key=section):
                st.session_state.selected_section = section  # Update session state on click
            
            # # Apply selected class for styling
            # button_class = "selected" if is_selected else ""
            # cols[i].markdown(f'<span class="{button_class}">{section}</span>', unsafe_allow_html=True)

        # Display content based on selection
        if st.session_state.selected_section == "📌Topics":
            show_topics()
        elif st.session_state.selected_section == "🗣️Intents":
            show_intents()
        elif st.session_state.selected_section == "📒Summary":
            show_summary()
        elif st.session_state.selected_section == "📊Stats":
            show_stats()

def show_transcription():
    st.subheader("Transcription")
    
    transcript_data = [
        {"Speaker": "Speaker 1:", "Text": "hello hello yes I am talking to speaker 2"},
        {"Speaker": "Speaker 2:", "Text": "Sir your video kyC has been done right access bank's credit call me is hasn't no yes sir it has been done"},
        {"Speaker": "Speaker 1:", "Text": "It was completed then I don't know what happened between I don't know what happened after saying that I don't know what happened after saying that"},
        {"Speaker": "Speaker 2:", "Text": "Sir it's done I am showing that it's done your credit card will be available in 2-3 days"},
        {"Speaker": "Speaker 1:", "Text": "okay I mean it will be available on 1st"}
    ]
    
    for entry in transcript_data:
        st.markdown(f'<div class="transcript-line"><strong>{entry["Speaker"]}</strong> {entry["Text"]}</div>', unsafe_allow_html=True)

def show_topics():
    st.subheader("Topics")
    st.text("This is where Topics content would be displayed.")

def show_intents():
    st.subheader("Intents")
    st.text("This is where Intents content would be displayed.")

def show_summary():
    st.subheader("Summary")
    
    summary_data = {
        "Category": ["Call Type"],
        "Details": ["First call. The primary purpose is to confirm the completion of video KYC and to discuss credit card benefits and charges."]
    }
    
    df = pd.DataFrame(summary_data)
    st.table(df)

def show_stats():
    st.subheader("Stats")
    st.text("This is where Stats content would be displayed.")

if __name__ == "__main__":
    main()