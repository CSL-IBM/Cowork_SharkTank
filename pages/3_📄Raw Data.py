import streamlit as st
import base64
from utils.constants import *

st.set_page_config(page_title='Template' ,layout="wide",initial_sidebar_state="auto", page_icon='👧🏻') # always show the sidebar

def local_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)
        
local_css("styles/styles_main.css")
    
# get the variables from constants.py
pronoun = info['Pronoun']

# app sidebar (좌측 메뉴 하단)
with st.sidebar:
    st.markdown("""
                # FAQ
                """)
    with st.expander("Click here to see FAQs"):
        st.info(
            f"""
            - What are the items with a due date after today??
            - Show me the list where the collector is Lisa and the category is Yellow!
            - Show me the list where the collector is David and the forecast code is AUTO!
            - Show me the list where the collector is John and the forecast date is after August!
            - How many AUTO in Forecastcode per collector?
            - How many invoice numbers with due date greater than August 10th 2024?
            - How many green per collector in category??
            - ++++++++++++++TBD++++++++++++++
            """
        )
        
    st.caption(f"© Made by CSL_Test 2024. All rights reserved.")
 
st.title("📝 Raw Data")

st.write(f"[Click here if it's blocked by your browser]({info['Resume']})")

with open("images/Raw Data.pdf","rb") as f:
      base64_pdf = base64.b64encode(f.read()).decode('utf-8')
      pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="1000mm" height="1000mm" type="application/pdf"></iframe>'
      st.markdown(pdf_display, unsafe_allow_html=True)
        
