import streamlit as st
import google-generativeai as genai
from gtts import gTTS
import os
import pandas as pd
import PyPDF2
import tempfile
from PIL import Image
import pytesseract
from dotenv import load_dotenv
load_dotenv()


# set up the Google Generative AI API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("GOOGLE_API_KEY not found. Please set it in your .env file.")
else:
    genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")  # Use the model name

#  Functtiom: Transform text using Google Generative AI
def translate_text_gemini(text, target_language):
        try:
             prompt=f"Translate the following text to {target_language}:\n\n{text}"
             response = model.generate_content(prompt)
             return response.text.strip()

        except Exception as e:
             return f"Error while translating {str(e)}"                
                  
             

    

# Function: Extract text from uploadded files
def extract_text_from_file(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.getbuffer())
            temp_file_path = temp_file.name

        with open(temp_file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        os.remove(temp_file_path)
        return text
    elif uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        return df.to_string()
    elif uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
        return df.to_string()
    #  redaings from an image
    elif uploaded_file.name.endswith((".png", ".jpg", ".jpeg")):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_img:
                temp_img.write(uploaded_file.getbuffer())
                temp_img_path = temp_img.name
            image = Image.open(temp_img_path)
            text = pytesseract.image_to_string(image)
            os.remove(temp_img_path)
            return text.strip() if text.strip() else "No text found in image."
        except Exception as e:
            return f"Error extracting text from image: {str(e)}"
    else:
        return "Unsupported file format. Please upload a PDF, CSV, or Excel file."

#  Convert text to speech
def text_to_speech(text, lang_code):
    try:
        tts = gTTS(text, lang=lang_code)  # Use first two letters of the language code
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            tts.save(temp_audio.name)
            return temp_audio.name

    except Exception as e:
        return f"Error in Text-to-Speech conversion: {str(e)}"

#  streamlit APP UI
st.set_page_config(page_title="Multilingual Text Translator", page_icon="🌐", layout="wide")
st.title("Multilingual Text Translator")
st.write("Upload a file (PDF, CSV, Excel, or Image) and translate its content to your desired language.")
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "csv", "xlsx", "png", "jpg", "jpeg"], key="file_uploader_main")

# Text input or file upload
text_input = st.text_area("Or enter text to translate:")

target_language = {
    "English": 'en',
    "French": 'fr',
    "German": 'de',
    "Spanish": 'es',
    "Italian": 'it',
    "Chinese": 'zh',
    "Japanese": 'ja',
    "Russian": 'ru',
    "Arabic": 'ar',
    "Hindi": 'hi',
}
selected_language = st.selectbox("Select target language:", list(target_language.keys()))

if st.button("Translate"):
    # Get text from file or input
    if uploaded_file is not None:
        text = extract_text_from_file(uploaded_file)
    else:
        text = text_input

    # Validate text input/extracted text
    if text.strip() == "":
        st.error("Please enter some text or upload a valid file.")
    else:
        # Translate text (using Gemini model) to selected language
        translate_text = translate_text_gemini(text, selected_language)
        st.subheader("Translated Text:")
        st.write(translate_text)

        #  Convert translated text to speech
        audio_file = text_to_speech(translate_text, target_language[selected_language])

        if audio_file:
            st.audio(audio_file, format="audio/mp3")
            with open(audio_file, "rb") as f:
                st.download_button("Download Audio", f, file_name="translated_audio.mp3", mime="audio/mp3")
        else:
            st.error("Error in Text-to-Speech conversion.")

 
            
# Text-to-Speech conversion
def text_to_speech():

    try:
        tts = gTTS(translated_text, lang=target_language[selected_language][:2].lower())  # Use first two letters of the language code
        audio_file = "translated_audio.mp3"
        tts.save(audio_file)
        st.audio(audio_file, format="audio/mp3")
    except Exception as e:
        st.error(f"Error in Text-to-Speech conversion: {str(e)}")

if uploaded_file and target_language:
    text = extract_text_from_file(uploaded_file)
    if text.startswith("Error") or text == "Unsupported file format. Please upload a PDF, CSV, or Excel file.":
        st.error(text)
    else:
        translated_text = translate_text_gemini(text, target_language)
        if translated_text.startswith("Error"):
            st.error(translated_text)
        else:
            st.subheader("Translated Text:")
            st.text_area("Translation", translated_text, height=300)
            
            # Text-to-Speech conversion
            try:
                tts = gTTS(translated_text, lang=target_language[:2].lower())  # Use first two letters of the language code
                audio_file = "translated_audio.mp3"
                tts.save(audio_file)
                st.audio(audio_file, format="audio/mp3")
            except Exception as e:
                st.error(f"Error in Text-to-Speech conversion: {str(e)}")

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'



