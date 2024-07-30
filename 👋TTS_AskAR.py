import streamlit as st
from streamlit_option_menu import option_menu
from utils.constants import info
import streamlit.components.v1 as components
from PIL import Image

# Configure page settings
st.set_page_config(page_title='Template', layout="wide", initial_sidebar_state="auto", page_icon='👧🏻')

# Load local CSS styles
def local_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)
        
local_css("styles/styles_main.css")

# Get the variables from constants.py
pronoun = info['Pronoun']

def hero(content1, content2):
    st.markdown(f'<h1 style="text-align:center;font-size:60px;border-radius:2%;">'
                f'<span>{content1}</span><br>'
                f'<span style="color:black;font-size:22px;">{content2}</span></h1>', 
                unsafe_allow_html=True)

with st.container():
    col1, col2 = st.columns([8, 3])

full_name = info['Full_Name']
with col1:
    hero(f"Hi, I'm {full_name}👋", info["Intro"])
    st.write("")
    st.write(info['About'])

    from streamlit_extras.switch_page_button import switch_page
    col_1, col_2, col_3 = st.columns([0.3, 0.4, 0.3])
    with col_1:
        btn1 = st.button("AskEngageAR")
        if btn1:
            switch_page("AskEngageAR")
    with col_2:
        btn2 = st.button("Contract Information")
        if btn2:
            switch_page("Contract Information")
    with col_3:
        btn3 = st.button("Payment Trend")
        if btn3:
            switch_page("Payment Trend")

def change_button_color(widget_label, background_color='transparent'):
    htmlstr = f"""
        <script>
            var elements = window.parent.document.querySelectorAll('button');
            for (var i = 0; i < elements.length; ++i) {{ 
                if (elements[i].innerText == '{widget_label}') {{ 
                    elements[i].style.background = '{background_color}'
                }}
            }}
        </script>
        """
    components.html(f"{htmlstr}", height=0, width=0)

change_button_color('Chat with My AI Assistant', '#0cc789') 

with col2:
    profile = Image.open("images/SharkTank_2.png")
    st.image(profile, width=280)

endorsements = {
    "img1": "https://raw.githubusercontent.com/CSL-IBM/Cowork_SharkTank/main/images/git_background_1.png",
    "img2": "https://raw.githubusercontent.com/CSL-IBM/Cowork_SharkTank/main/images/git_background_2.png",
}
       
st.write("---")
with st.container():  
    col1, col2 = st.columns([0.6, 0.4])
    
    with col1:
        st.subheader("💵 Korea ART")
        st.write("https://w3.ibm.com/w3publisher/artkorea")  # 추가된 텍스트
        components.html(
        f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * {{box-sizing: border-box;}}
            .mySlides {{display: none;}}
            img {{vertical-align: middle;}}

            /* Slideshow container */
            .slideshow-container {{
            position: relative;
            margin: auto;
            width: 100%;
            }}

            /* The dots/bullets/indicators */
            .dot {{
            height: 15px;
            width: 15px;
            margin: 0 2px;
            background-color: #eaeaea;
            border-radius: 50%;
            display: inline-block;
            transition: background-color 0.6s ease;
            }}

            .active {{
            background-color: #6F6F6F;
            }}

            /* Fading animation */
            .fade {{
            animation-name: fade;
            animation-duration: 1s;
            }}

            @keyframes fade {{
            from {{opacity: .4}} 
            to {{opacity: 1}}
            }}

            /* On smaller screens, decrease text size */
            @media only screen and (max-width: 300px) {{
            .text {{font-size: 11px}}
            }}
            </style>
        </head>
        <body>
            <div class="slideshow-container">
                <div class="mySlides fade">
                <img src={endorsements["img1"]} style="width:90%">
                </div>

                <div class="mySlides fade">
                <img src={endorsements["img2"]} style="width:90%">
                </div>

            </div>
            

            <div style="text-align:center">
                <span class="dot"></span> 
                <span class="dot"></span> 
            </div>

            <script>
            let slideIndex = 0;
            showSlides();

            function showSlides() {{
            let i;
            let slides = document.getElementsByClassName("mySlides");
            let dots = document.getElementsByClassName("dot");
            for (i = 0; i < slides.length; i++) {{
                slides[i].style.display = "none";  
            }}
            slideIndex++;
            if (slideIndex > slides.length) {{slideIndex = 1}}    
            for (i = 0; i < dots.length; i++) {{
                dots[i].className = dots[i].className.replace("active", "");
            }}
            slides[slideIndex-1].style.display = "block";  
            dots[slideIndex-1].className += " active";
            }}

            var interval = setInterval(showSlides, 2500); // Change image every 2.5 seconds

            function pauseSlides(event)
            {{
                clearInterval(interval); // Clear the interval we set earlier
            }}
            function resumeSlides(event)
            {{
                interval = setInterval(showSlides, 2500);
            }}
            // Set up event listeners for the mySlides
            var mySlides = document.getElementsByClassName("mySlides");
            for (i = 0; i < mySlides.length; i++) {{
            mySlides[i].onmouseover = pauseSlides;
            mySlides[i].onmouseout = resumeSlides;
            }}
            </script>

            </body>
            </html> 

            """,
                height=270,
    )

    with col2:
        st.subheader("📨 Contact Me")
        email = info["Email"]
        contact_form = f"""
        <form action="https://formsubmit.co/{email}" method="POST">
            <input type="hidden" name="_captcha value="false">
            <input type="text" name="name" placeholder="Your name" required>
            <input type="email" name="email" placeholder="Your email" required>
            <textarea name="message" placeholder="Your message here" required></textarea>
            <button type="submit">Send</button>
        </form>
        """
        st.markdown(contact_form, unsafe_allow_html=True)

# 캡션 텍스트를 맨 아래에 배치
st.caption(f"© Made by Korea AR Team for SharkTank 2024. All rights reserved.")
