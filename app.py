import streamlit as st
from PIL import Image

PROJ_NAME = 'INSERT_PROJ_NAME'

INTRO = """
*Developed by Anthony Zang, Isaac Song, Kieran Slattery, and Zini Chakraborty*

*Hacklytics 2025 @ Georgia Tech*


"""

def main():
    st.title(PROJ_NAME)
    st.write(INTRO)
    
    st.write('## Please upload an image of a room')
    uploaded_file = st.file_uploader("Choose a room...",
                                     type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Room.', use_container_width=True)

    if st.button('Reimagine Your Room') and uploaded_file is not None:
        st.write('### Reimagining your room...')
        

    
    
if __name__ == "__main__":
    main()