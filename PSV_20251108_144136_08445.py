
import streamlit as st
import pandas as pd
from pdf_generator import create_form_81c_pdf
from utils import load_exhibit_data

st.set_page_config(page_title="Form Builder - Legal Suite", page_icon="📝", layout="wide")

# --- Data Loading and State Management ---
exhibit_df = load_exhibit_data()
if exhibit_df.empty:
    st.warning("CUSTODY_COURT_EXHIBITS.txt not found. Exhibit referencing will be disabled.")

def load_form_data(form_name, default_content):
    if f'{form_name}_data' not in st.session_state:
        st.session_state[f'{form_name}_data'] = {'content': default_content}
    return st.session_state[f'{form_name}_data']

def save_form_data(form_name, data):
    st.session_state[f'{form_name}_data'] = data

# --- Default Content Definitions ---
FORM_81C_DEFAULT = (
    "1. The Respondent, Craig Schulz, seeks an Order for Primary Residence...\n\n"
    "2. The Respondent seeks an Order for Sole Decision-Making Responsibility...\n\n"
    "3. The Respondent requests a court-ordered Capacity Assessment...\n\n"
    "4. The Respondent requests that the Applicant's parenting time be supervised...\n\n"
    "5. The Respondent seeks a court Order imposing a mandatory compliance penalty clause..."
)

FORM_81B_DEFAULT = (
    "I, Craig Schulz, of the City of Saint John, New Brunswick, MAKE OATH AND SAY AS FOLLOWS:\n\n"
    "1. I am the Respondent and have personal knowledge of the facts herein.\n\n"
    "2. (Begin drafting your narrative here. Use the tool to insert exhibit references.)\n\n"
    "SWORN TO (OR AFFIRMED) before me...\n"
    "_________________________\nCRAIG SCHULZ"
)

# --- Main Application --- #
st.title("📝 Form Builder")
st.info("**Court File No.: FDSJ-739-2024** is added to all generated documents.")

tab1, tab2, tab3, tab4 = st.tabs(["Form 81C: Answer/Counter-Claim", "Form 81B: Affidavit", "Form 72J: Financial Info", "Form 37A: Motions"])

# --- Form 81C: Answer & Counter-Claim ---
with tab1:
    st.header("Form 81C: Answer and Counter-Claim")
    form_data = load_form_data('form81c', FORM_81C_DEFAULT)
    
    content = st.text_area(
        "**Respondent's Claims**", 
        value=form_data.get('content', ''), 
        height=350,
        help="Enter each claim as a numbered paragraph."
    )
    form_data['content'] = content
    save_form_data('form81c', form_data)

    if st.button("Generate PDF of Form 81C"):
        pdf_buffer = create_form_81c_pdf(content)
        st.download_button(
            label="Download Form 81C PDF",
            data=pdf_buffer,
            file_name=f"Form_81C_Answer_{pd.Timestamp.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )

# --- Form 81B: Affidavit ---
with tab2:
    st.header("Form 81B: Affidavit in Support of Claim")
    form_data = load_form_data('form81b', FORM_81B_DEFAULT)

    col1, col2 = st.columns([2.5, 1.5])
    with col1:
        content = st.text_area(
            "**Affidavit Body**", 
            value=form_data.get('content', ''), 
            height=600
        )
        form_data['content'] = content
        save_form_data('form81b', form_data)

    with col2:
        st.subheader("Exhibit Referencing Tool")
        if not exhibit_df.empty:
            exhibit_df['display'] = exhibit_df.index + ": " + exhibit_df['Context'].str.slice(0, 40) + "..."
            
            selected_exhibit = st.selectbox("Select Exhibit", options=exhibit_df['display'])

            if st.button("Insert Exhibit Reference into Affidavit"):
                exhibit_id = selected_exhibit.split(":")[0]
                exhibit_row = exhibit_df.loc[exhibit_id]
                reference = f"\n\nNOW PRODUCED AND SHOWN TO ME AND MARKED AS EXHIBIT \"{exhibit_id}\" is a true copy of '{exhibit_row['File']}'."
                st.session_state.form81b_data['content'] += reference
                st.experimental_rerun()
        else:
            st.warning("Exhibit data not available.")

# --- Other Forms (Placeholders) ---
with tab3:
    st.warning("Form 72J is under construction.")
with tab4:
    st.warning("Form 37A is under construction.")
