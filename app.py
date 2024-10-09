import streamlit as st
from pydub import AudioSegment
import os
import speech_recognition as sr
import arabic_reshaper
from bidi.algorithm import get_display

# The reference surah
REFERENCE_SURAH = "انا اعطيناك الكوثر فصل لربك وانحر ان شانئك هو الابتر"

import openai-whisper
from pydub import AudioSegment
import os

def transcribe_audio(file_path):
    """Transcribes the given audio file using Whisper AI and returns the transcribed Arabic text."""
    try:
        # Convert any audio format to wav
        sound = AudioSegment.from_file(file_path)  # Automatically handles various formats
        wav_file_path = file_path.rsplit('.', 1)[0] + '.wav'  # Change extension to .wav
        sound.export(wav_file_path, format='wav')
        
        # Load Whisper model
        model = whisper.load_model("base")  # You can also use 'tiny', 'small', 'medium', or 'large' models based on the resources available
        
        # Transcribe the audio, specifying that the language is Arabic
        result = model.transcribe(wav_file_path, language='ar')
        
        # Clean up the wav file after processing
        os.remove(wav_file_path)

        # Return the transcribed text
        return result['text']
    
    except Exception as e:
        return f"حدث خطأ: {str(e)}"


def compare_texts(reference, transcription):
    """Compares reference text with transcription and returns colored HTML."""
    reference_words = reference.strip().split()
    transcription_words = transcription.strip().split()

    colored_output = []
    ref_index = 0  # Track position in the reference string

    # Iterate through transcription words
    for trans_word in transcription_words:
        # Check if we have reached the end of the reference
        if ref_index < len(reference_words):
            if trans_word == reference_words[ref_index]:
                # If the word matches, color it green and move to the next word in the reference
                colored_output.append(f"<span style='color:green;'>{trans_word}</span>")
                ref_index += 1  # Move to the next word in the reference
            else:
                # If it does not match, color it red
                colored_output.append(f"<span style='color:red;'>{trans_word}</span>")
        else:
            # If we've exhausted the reference words, color remaining transcription words red
            colored_output.append(f"<span style='color:red;'>{trans_word}</span>")

    # Handle any remaining words in the reference (not present in transcription)
    while ref_index < len(reference_words):
        # Not necessary since we're displaying transcription only
        ref_index += 1

    return " ".join(colored_output)

def main():
    # Streamlit app title
    st.title("Quran Speech to Text")

    # Add custom CSS for Arabic font
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Amiri&display=swap');

            .arabic-text {
                font-family: 'Amiri', serif;  /* Use a nice Arabic font */
                font-size: 28px;              /* Increased font size for better readability */
                direction: rtl;               /* Right to left direction */
                text-align: right;            /* Align text to right */
                line-height: 1.6;             /* Increase line height for better spacing */
            }
        </style>
        """, unsafe_allow_html=True)

    # File uploader for audio files
    uploaded_file = st.file_uploader("Upload Audio File", type=["mp3", "wav", "flac", "ogg", "aac", "wma"])
    
    # Initialize a variable to store the audio file path
    if uploaded_file is not None:
        # Save the uploaded file to a temporary location
        with open("temp_audio_file", "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Create a button to proceed with transcription
        if st.button("Proceed Audio"):
            # Transcribe the audio file
            transcribed_text = transcribe_audio("temp_audio_file")
            
            # Reshape and display the text
            reshaped_text = arabic_reshaper.reshape(transcribed_text)
            bidi_text = get_display(reshaped_text)

            # Compare transcribed text with the reference surah and get colored output
            comparison_html = compare_texts(REFERENCE_SURAH, transcribed_text)

            # Display the result with mismatches highlighted
            st.markdown(f"<p class='arabic-text'>{comparison_html}</p>", unsafe_allow_html=True)

if __name__ == "__main__":  # Corrected line
    main()
