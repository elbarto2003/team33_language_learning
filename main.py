import streamlit as st
from audio_recorder_streamlit import audio_recorder
from pydub import AudioSegment
import tempfile
import azure.cognitiveservices.speech as speechsdk
import io
from pymongo import MongoClient
import datetime
import random


client = MongoClient("mongodb+srv://bmowinski2:4K4cR171KB6uLPVT@team33data.5p0rb.mongodb.net/?retryWrites=true&w=majority&appName=team33data")

# Access the database (will be created on first insert)
db = client.language_learning_app

# Access the collections (will be created on first insert)
users_collection = db.users
sentences_collection = db.sentences
attempted_sentences_collection = db.attempted_sentences
# Access or create the flashcards collection
flashcards_collection = db.flashcards

# Access or create the vocabulary collection
vocabulary_collection = db.vocabulary


# Fetch a random sentence from MongoDB
def get_random_sentence():
    sentences = list(sentences_collection.find({}))
    return random.choice(sentences) if sentences else None

def get_new_sentence_for_user(user_id):
    attempted_sentence_ids = attempted_sentences_collection.find({"user_id": user_id}, {"sentence_id": 1})
    attempted_ids = {attempt["sentence_id"] for attempt in attempted_sentence_ids}
    new_sentence = sentences_collection.find_one({"_id": {"$nin": list(attempted_ids)}})
    return new_sentence

def store_attempt_result(user_id, sentence_id, accuracy_score, fluency_score, completeness_score, overall_score):
    attempt_data = {
        "user_id": user_id,
        "sentence_id": sentence_id,
        "accuracy_score": accuracy_score,
        "fluency_score": fluency_score,
        "completeness_score": completeness_score,
        "overall_score": overall_score,
        "timestamp": datetime.utcnow()
    }
    attempted_sentences_collection.insert_one(attempt_data)


def process_audio(audio_file_path, reference_text):
    # Setting up azure speach sdk
    speech_config = speechsdk.SpeechConfig(subscription="136f4daa70b74cb8aca9bb595b33d4c5", region="eastus2")
    audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)

    # Configuring pronunciation assessment
    pronunciation_config = speechsdk.PronunciationAssessmentConfig(
        reference_text=reference_text,
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
        enable_miscue=True
    )

    # Creating recognizer and applying pronunciation assessment config
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    pronunciation_config.apply_to(recognizer)

    # Perform pronunciation assessment
    result = recognizer.recognize_once()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        pronunciation_result = speechsdk.PronunciationAssessmentResult(result)
        assessment_details = {
            "Accuracy Score": pronunciation_result.accuracy_score,
            "Fluency Score": pronunciation_result.fluency_score,
            "Completeness Score": pronunciation_result.completeness_score,
            "Overall Pronunciation Score": pronunciation_result.pronunciation_score
        }
        return assessment_details
    elif result.reason == speechsdk.ResultReason.NoMatch:
        return "No speech could be recognized"
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        return f"Speech Recognition canceled: {cancellation_details.reason}, {cancellation_details.error_details}"

# Initialize the session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "Home"

# Sidebar navigation buttons
st.sidebar.title("Navigation")
if st.sidebar.button("Home"):
    st.session_state.page = "Home"
if st.sidebar.button("Pronunciation Test"):
    st.session_state.page = "Pronunciation Test"
if st.sidebar.button("Flashcards"):
    st.session_state.page = "Flashcards"
if st.sidebar.button("Vocabulary Builder"):
    st.session_state.page = "Vocabulary Builder"

# Display the selected page content
if st.session_state.page == "Home":
    st.title("🌟 Language Learning App Dashboard")
    st.markdown("""
        Welcome to the Language Learning App! Use the navigation menu on the left to access different features:

        - **Pronunciation Test**: Evaluate your pronunciation and get feedback.
        - **Flashcards**: Test your knowledge with Flashcards!.
        - **Vocabulary Builder**: Vocabulary Builder.

        Choose a feature from the sidebar to get started!
    """)

elif st.session_state.page == "Pronunciation Test":

    st.title("🎙️ Pronunciation Assessment")
    st.markdown("""
    Record your voice, evaluate your pronunciation, and get feedback.
    """)

    # Ensure st.session_state.sentence has a value
    if "sentence" not in st.session_state:
        st.session_state.sentence = get_random_sentence()

    if st.session_state.sentence:
        # Display the sentence if it was successfully fetched
        st.markdown(
            f"<h3><strong>Practice Saying This Sentence:</strong></h3><blockquote style='font-size: 24px; font-weight: bold;'>{st.session_state.sentence['text']}</blockquote>",
            unsafe_allow_html=True
        )
    else:
        # Handle the case where no sentence is available
        st.error("No sentence available in the database. Please check your database connection and content.")

    # Instructions
    st.markdown("""
        <div style="background-color:#f9f9f9; padding:10px; border-radius:10px; margin-bottom: 20px;">
            <h2 style='color: #333;'>Instructions</h2>
            <ul style='color: #555;'>
                <li>Click the microphone icon to start recording.</li>
                <li>Say the sentence: <b>'This is the text to evaluate for pronunciation.'</b></li>
                <li>Stop recording when you're done, and wait for assessment results.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    # Recording Section
    st.markdown("<h3 style='color: #ff6347;'>Record Your Voice 🎤</h3>", unsafe_allow_html=True)
    audio_bytes = audio_recorder()

    # Playback and Results Section
    if audio_bytes:
        st.markdown("<h3 style='color: #4682b4;'>Playback</h3>", unsafe_allow_html=True)
        st.audio(audio_bytes, format="audio/wav")

        # Convert audio bytes to WAV format and save to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as audio_file:
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="wav")
            audio.export(audio_file.name, format="wav")
            audio_file_path = audio_file.name

        # Display Spinner and Process Audio
        with st.spinner("Assessing your pronunciation..."):
            assessment_result = process_audio(audio_file_path, st.session_state.sentence['text'])

        # Display Results with color coding
        st.markdown("<h3 style='color: #4682b4;'>Pronunciation Assessment Results</h3>", unsafe_allow_html=True)
        if isinstance(assessment_result, dict):
            for key, value in assessment_result.items():
                color = "#4CAF50" if value > 80 else "#FF6347" if value < 50 else "#FFA500"
                st.markdown(f"<p style='font-size: 18px; color: {color};'><b>{key}:</b> {value}</p>",
                            unsafe_allow_html=True)
        else:
            st.error(assessment_result)

elif st.session_state.page == "Flashcards":
    st.title("📝 Flashcards")

    # Input fields for adding a new flashcard
    front_text = st.text_input("Front of Flashcard")
    back_text = st.text_input("Back of Flashcard")

    if st.button("Add Flashcard"):
        if front_text and back_text:
            flashcards_collection.insert_one({"front": front_text, "back": back_text})
            st.success("Flashcard added!")
        else:
            st.warning("Please enter both the front and back of the flashcard.")

    st.write("---")

    # Initialize session state for managing flashcard review
    if "in_review" not in st.session_state:
        st.session_state.in_review = False
    if "show_back" not in st.session_state:
        st.session_state.show_back = False
    if "flashcard_index" not in st.session_state:
        st.session_state.flashcard_index = None

    # Start Review button: Loads flashcards and sets in_review mode
    if st.button("Start Review"):
        flashcards = list(flashcards_collection.find())

        if flashcards:
            st.session_state.flashcards = flashcards
            st.session_state.flashcard_index = random.randint(0, len(flashcards) - 1)
            st.session_state.in_review = True
            st.session_state.show_back = False
        else:
            st.warning("No flashcards available to review.")
            st.session_state.in_review = False

    # Show the current flashcard only if in_review is True
    if st.session_state.in_review:
        flashcard = st.session_state.flashcards[st.session_state.flashcard_index]

        st.write("**Front:**")
        st.markdown(f"> {flashcard['front']}")

        # Show the back if `show_back` is True
        if st.session_state.show_back:
            st.write("**Back:**")
            st.markdown(f"> {flashcard['back']}")

            # Next button to move to a new card
            if st.button("Next"):
                st.session_state.flashcard_index = random.randint(0, len(st.session_state.flashcards) - 1)
                st.session_state.show_back = False

        # Show Answer button to reveal the back of the flashcard
        elif st.button("Show Answer"):
            st.session_state.show_back = True

    else:
        st.write("Click 'Start Review' to begin reviewing flashcards.")

elif st.session_state.page == "Vocabulary Builder":
    st.title("📖 Vocabulary Builder")

    # Initialize session state for word index and daily word count
    if "vocabulary_words" not in st.session_state:
        st.session_state.vocabulary_words = list(vocabulary_collection.find({}))
        random.shuffle(st.session_state.vocabulary_words)
    if "word_index" not in st.session_state:
        st.session_state.word_index = 0
    if "daily_count" not in st.session_state:
        st.session_state.daily_count = 0

    # Display word if daily limit hasn't been reached
    if st.session_state.daily_count < 5 and st.session_state.word_index < len(st.session_state.vocabulary_words):
        word = st.session_state.vocabulary_words[st.session_state.word_index]["word"]
        st.markdown(f"### New words today: **{word}**")

        # Button to go to the next word
        if st.button("Next"):
            st.session_state.word_index += 1
            st.session_state.daily_count += 1
    else:
        st.write("That's all for today! Come back tomorrow for more words.")

    # Reset daily limit at midnight
    if datetime.datetime.now().hour == 0 and st.session_state.daily_count >= 5:
        st.session_state.word_index = 0
        st.session_state.daily_count = 0





