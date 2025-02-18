import streamlit as st
import pyttsx3
from gtts import gTTS
import os
import tempfile
from googletrans import Translator
from pydub import AudioSegment
import speech_recognition as sr

# --- Custom CSS (Embedded) ---
def inject_custom_css():
    css = """
    <style>
        body {
            font-family: 'Arial', sans-serif; 
            background-color: #ffe6f2; 
            color: #333;
        }

        h1 {
            color: #5e64ff;
            text-align: center;
            padding-bottom: 10px;
        }

        .stButton>button {
            color: #fff;
            background-color: #5e64ff;
            border-radius: 5px;
            height: 3em;
            width: 10em;
            border: none;
            cursor: pointer;
        }

        .stButton>button:hover {
            background-color: #4247d0;
        }

        .stTextInput > label, .stTextArea > label, .css-16ids5w > label {
            color: #262730;
        }

        .stSidebar {
            background-color: #f9f9f9;
            padding: 20px;
        }

        .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4 {
            color: #262730;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# --- Function Definitions (Same as before) ---

def offline_tts(text, accent):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    available_voices = [voice.name for voice in voices]
    print("Available voices:", available_voices)

    selected_voice = None
    if accent == "English":
        selected_voice = next((voice for voice in voices if 'english' in voice.name.lower()), None)
    elif accent == "Telugu":
        selected_voice = next((voice for voice in voices if 'telugu' in voice.name.lower()), None)
    elif accent == "Hindi":
        selected_voice = next((voice for voice in voices if 'hindi' in voice.name.lower()), None)
    elif accent == "Spanish":
        selected_voice = next((voice for voice in voices if 'spanish' in voice.name.lower()), None)
    elif accent == "French":
        selected_voice = next((voice for voice in voices if 'french' in voice.name.lower()), None)
    elif accent == "German":
        selected_voice = next((voice for voice in voices if 'german' in voice.name.lower()), None)
    elif accent == "Italian":
        selected_voice = next((voice for voice in voices if 'italian' in voice.name.lower()), None)
    elif accent == "Portuguese":
        selected_voice = next((voice for voice in voices if 'portuguese' in voice.name.lower()), None)

    # Default to the first voice if none found
    if selected_voice is None:
        st.warning(f"No voice available for {accent}. Defaulting to first available voice.")
        selected_voice = voices[0]  # Default to the first available voice

    engine.setProperty('voice', selected_voice.id)
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1)

    # Save speech to temporary WAV file
    with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as tmpfile:
    tts.write_to_fp(tmpfile)
    tmpfile.flush()  # Ensure content is written
    tmpfile.seek(0)
    # Continue using tmpfile as needed


    # Convert WAV to MP3 using pydub
    mp3_file = tmpfile.name.replace(".wav", ".mp3")
    audio = AudioSegment.from_wav(tmpfile.name)
    audio.export(mp3_file, format="mp3")
    os.remove(tmpfile.name)  # Clean up temporary WAV file

    return mp3_file


def online_tts(text, accent):
    accent_map = {
        "English": 'en',
        "Telugu": 'te',
        "Hindi": 'hi',
        "Spanish": 'es',
        "French": 'fr',
        "German": 'de',
        "Italian": 'it',
        "Portuguese": 'pt',
    }

    language_code = accent_map.get(accent, 'en')
    tts = gTTS(text=text, lang=language_code, slow=False)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
        tts.write_to_fp(tmpfile)
        return tmpfile.name


def translate_text(text, target_language):
    translator = Translator()
    translated_text = translator.translate(text, dest=target_language).text
    return translated_text

def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()

    try:
        # Convert MP3 to WAV using pydub
        wav_file = audio_file.replace(".mp3", ".wav")
        audio = AudioSegment.from_mp3(audio_file)
        audio.export(wav_file, format="wav")

        with sr.AudioFile(wav_file) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except FileNotFoundError:
        return "Audio file not found."
    except Exception as e:
        return f"Error during transcription: {str(e)}"
    finally:
        if os.path.exists(wav_file):
            os.remove(wav_file)



# --- Streamlit UI with Enhanced Styling ---

# Inject CSS
inject_custom_css()

# Header
st.markdown("<h1 style='text-align: center; color: #262730;'>Speechify</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #262730;'>Text-to-Speech with Translation and Audio Transcription</p>", unsafe_allow_html=True)

# Input Area
st.markdown("<p style='color: #262730;'>Enter Text:</p>", unsafe_allow_html=True)
text = st.text_area("", "Hello, how are you doing today?", height=150)

# Sidebar
with st.sidebar:
    st.header("Settings")
    tts_choice = st.selectbox("Select TTS Engine", ["gTTS (online)", "pyttsx3 (offline)"])
    accent = st.selectbox("Select Accent or Language", ["English", "Telugu", "Hindi", "Spanish", "French", "German", "Italian", "Portuguese"])

# Translation
if accent not in ["English"]:
    translated_text = translate_text(text, accent)
else:
    translated_text = text

# Button and Processing
button_container = st.container()
with button_container:
    generate_button = st.button("Generate")

if generate_button:
    if translated_text:
        with st.spinner("Generating audio..."):
            if tts_choice == "gTTS (online)":
                audio_file = online_tts(translated_text, accent)
            else:
                audio_file = offline_tts(translated_text, accent)

            if audio_file:
                st.subheader("Audio:")
                st.audio(audio_file, format='audio/mp3')

                # Transcribe the generated audio
                with st.spinner("Transcribing audio..."):
                    transcribed_text = transcribe_audio(audio_file)
                st.subheader("Transcription:")
                st.write(transcribed_text)

                # Clean up the temporary audio file after transcription
                os.remove(audio_file)
    else:
        st.warning("Please enter text to generate audio.")
