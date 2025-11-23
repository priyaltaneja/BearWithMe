"""
Bear With Me - Azure + ElevenLabs Phoneme Feedback
Captures audio from microphone, gets phoneme scores, and speaks feedback for low-scoring phonemes only.
Gives positive feedback if all phonemes are correct.
"""

import azure.cognitiveservices.speech as speechsdk
from elevenlabs import ElevenLabs
import tempfile
import os
import sys
import time
import json
import random
import argparse
import pygame
from datetime import datetime

# Initialize random seed with current time for better randomization
random.seed()
from datetime import datetime

# Seed random with current time for better randomization
random.seed()

# --- CONFIG --- #
# Azure - Hardcoded API keys
AZURE_KEY = "481cEqHk3bzX4gUtXAz7658eQJkv9IMnR7Acw9qP17NcgZ10lddkJQQJ99BKACYeBjFXJ3w3AAAYACOGoajC"
AZURE_REGION = "eastus"

# ElevenLabs - Hardcoded API keys
ELEVEN_API_KEY = "sk_90d22827a443c34176be1f86585b035f6bb42f1cf1d46b82"
VOICE_ID = "EXAVITQu4vr4xnSDxMaL"
THRESHOLD = 80  # phoneme score threshold

# Feedback prompts
PROMPTS = {
    "intro": "Let's practice the word {}.",
    "phoneme_practice": "Let's practice the sound {}.",
    "repeat_phoneme": "Can you say the sound {}?",
    "repeat_word": "Now try saying the whole word {} again.",
    "success_phoneme": "Good!",
    "all_correct": "Great job! You pronounced all the sounds correctly."
}

# --- SETUP --- #
eleven_client = ElevenLabs(api_key=ELEVEN_API_KEY)


def speak(text):
    """Plays text via ElevenLabs TTS."""
    audio_stream = eleven_client.text_to_speech.convert(
        voice_id=VOICE_ID,
        model_id="eleven_multilingual_v2",
        text=text
    )
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        for chunk in audio_stream:
            f.write(chunk)
        temp_path = f.name
    
    # Play audio directly without opening a window
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_path)
        except:
            pass


def speak_phoneme(phoneme_sound):
    """
    Speaks a phoneme sound with consistent context to ensure TTS pronounces it the same way each time.
    Uses a standardized phrase format that helps TTS interpret phonemes consistently.
    """
    # Use consistent format with clear context to ensure TTS pronounces it the same way each time
    # The phrase structure "say the sound [phoneme]" helps TTS consistently interpret phonemes
    speak(f"Say the sound {phoneme_sound}.")


def azure_phoneme_to_text(phoneme):
    """
    Convert Azure phonemes to TTS-friendly, accurate pronunciation text.
    Uses comprehensive CMU phoneme set mapping for accurate feedback.
    """
    # Remove stress numbers (AH0 -> AH, B1 -> B)
    base = ''.join([c for c in phoneme if not c.isdigit()]).lower()

    # Comprehensive CMU phoneme to readable pronunciation mapping
    # Based on CMU Pronouncing Dictionary phoneme set
    phoneme_mapping = {
        # Vowels - elongated for better TTS pronunciation
        "aa": "ahh",     # father, calm (elongated)
        "ae": "ah",      # cat, bat (elongated)
        "ah": "uhh",     # but, cut (elongated)
        "ao": "aww",     # law, caught (elongated)
        "aw": "oww",     # cow, how (elongated)
        "ay": "eye",     # buy, eye
        "eh": "ehh",     # bed, red (elongated)
        "er": "err",     # her, bird (elongated)
        "ey": "ayy",     # say, day (elongated)
        "ih": "ihh",     # bit, sit (elongated)
        "iy": "eee",     # see, bee (elongated)
        "ow": "ohh",     # go, show (elongated)
        "oy": "oyy",     # boy, toy (elongated)
        "uh": "ooo",     # book, put (elongated)
        "uw": "ooo",     # blue, food (elongated)
        "ax": "uhh",     # about, the (schwa, elongated)
        "axr": "err",    # better, water (elongated)
        
        # Consonants - elongated for better TTS pronunciation
        "b": "buh",      # bat
        "ch": "chuh",    # chair (elongated)
        "d": "duh",      # dog
        "dh": "thuh",    # this, that (voiced, elongated)
        "f": "fuh",      # fish
        "g": "guh",      # go
        "h": "heh",      # hat (single h)
        "hh": "huh",     # hat
        "jh": "juh",     # jump
        "k": "kuh",      # cat
        "l": "luh",      # let
        "m": "muh",      # mat
        "n": "nuh",      # not
        "ng": "nguh",    # sing (elongated)
        "p": "puh",      # pat
        "r": "ruh",      # red
        "s": "suh",      # sit
        "sh": "shuh",    # ship (elongated)
        "t": "tuh",      # top
        "th": "thuh",    # think (unvoiced, elongated)
        "v": "vuh",      # van
        "w": "wuh",      # wet
        "y": "yuh",      # yes
        "z": "zuh",      # zip
        "zh": "zhuh",    # measure (elongated)
    }

    # Get the readable pronunciation
    readable = phoneme_mapping.get(base, base)
    
    # If still not found and it's a single character, try to make it pronounceable
    if readable == base and len(base) == 1:
        # Fallback for single characters
        fallback = {
            "a": "ay", "e": "ee", "i": "eye", "o": "oh", "u": "oo",
            "h": "heh"  # Ensure single 'h' maps to 'huh'
        }
        readable = fallback.get(base, base)
    
    return readable


def assess_pronunciation_phonemes(target_word):
    """Uses Azure to assess phonemes and return a phoneme→score dictionary."""
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_KEY, region=AZURE_REGION)
    speech_config.speech_recognition_language = "en-US"
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

    pronunciation_config = speechsdk.PronunciationAssessmentConfig(
        reference_text=target_word,
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
        enable_miscue=True
    )
    global i
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    pronunciation_config.apply_to(recognizer)

    speak(f"Please say the word {target_word} now.")

    result = recognizer.recognize_once_async().get()

    if result.reason != speechsdk.ResultReason.RecognizedSpeech:
        print("❌ No speech recognized or recognition canceled.")
        return None, None

    pron_result = speechsdk.PronunciationAssessmentResult(result)
    phoneme_scores = {}
    phoneme_details = []  # Store phoneme info with position
    
    if hasattr(pron_result, 'words') and pron_result.words:
        for word in pron_result.words:
            if hasattr(word, 'phonemes') and word.phonemes:
                for idx, phoneme in enumerate(word.phonemes):
                    phoneme_key = phoneme.phoneme
                    phoneme_scores[phoneme_key] = phoneme.accuracy_score
                    phoneme_details.append({
                        'phoneme': phoneme_key,
                        'score': phoneme.accuracy_score,
                        'position': idx,
                        'total': len(word.phonemes)
                    })
    
    return phoneme_scores, phoneme_details


def give_phoneme_feedback(word, phoneme_scores, phoneme_details=None):
    """Speaks feedback for low-scoring phonemes with accurate pronunciation guidance.
    Gives positive feedback if all phonemes are above threshold.
    """
    if not phoneme_scores:
        return
    
    # Identify low-scoring phonemes with their details
    low_scoring_phonemes = []
    
    if phoneme_details:
        # Use detailed phoneme info if available
        for detail in phoneme_details:
            if detail['score'] < THRESHOLD:
                low_scoring_phonemes.append(detail)
    else:
        # Fallback to simple dictionary iteration
        for phoneme, score in phoneme_scores.items():
            if score < THRESHOLD:
                low_scoring_phonemes.append({
                    'phoneme': phoneme,
                    'score': score,
                    'position': None,
                    'total': None
                })

    if not low_scoring_phonemes:
        # All phonemes are above threshold
        speak(PROMPTS["all_correct"])
        return

    # Sort low-scoring phonemes by position (if available) to give feedback in order
    if phoneme_details and low_scoring_phonemes[0].get('position') is not None:
        low_scoring_phonemes.sort(key=lambda x: x.get('position', 0))
    
    # Provide feedback for each low-scoring phoneme in order
    for detail in low_scoring_phonemes:
        phoneme = detail['phoneme']
        score = detail['score']
        readable = azure_phoneme_to_text(phoneme)  # This gives us the sound like "huh", "buh", etc.
        
        # Determine position description for feedback
        position_desc = ""
        if detail['position'] is not None and detail['total'] is not None:
            pos = detail['position'] + 1
            total = detail['total']
            if pos == 1:
                position_desc = "first"
            elif pos == total:
                position_desc = "last"
            elif pos == 2:
                position_desc = "second"
            elif pos == 3:
                position_desc = "third"
            elif pos == 4:
                position_desc = "fourth"
            elif pos == 5:
                position_desc = "fifth"
            else:
                # For positions beyond 5th, use numeric format
                position_desc = f"{pos}th"
        
        # Provide contextual feedback about position in word for console output
        position_info = ""
        if detail['position'] is not None and detail['total'] is not None:
            pos = detail['position'] + 1
            total = detail['total']
            if pos == 1:
                position_info = " at the beginning of the word"
            elif pos == total:
                position_info = " at the end of the word"
            else:
                position_info = f" in the middle of the word (sound {pos} of {total})"
        
        print(f"   ⚠️  Phoneme '{phoneme}' (sound: {readable}) scored {score:.1f}%{position_info}")
        
        # Simple workflow: "Let's try the [first/second/last] sound together. Say [sound]"
        if position_desc:
            speak(f"Let's try the {position_desc} sound together. Say {readable}.")
        else:
            speak(f"Let's try this sound together. Say {readable}.")
        time.sleep(1.5)  # Give time for user to practice the sound
        speak("Good!")
        time.sleep(0.3)
    
    # After practicing individual sounds, always ask to repeat the whole word
    if low_scoring_phonemes:
        speak(f"")
        time.sleep(0.3)


def load_word_library(file_path="word_library.json"):
    """
    Load word library from JSON file.
    Expected format: [{"text": "word1", "breakdown": "break - down"}, ...]
    Returns list of word texts, or empty list if file doesn't exist.
    """
    # Get the script's directory and project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # Go up one level from main/ to project root
    
    # Try multiple possible locations for the file
    possible_paths = [
        os.path.abspath(file_path),  # Absolute path if provided
        os.path.join(project_root, file_path),  # Project root (most likely location)
        os.path.join(os.getcwd(), file_path),  # Current working directory
        os.path.join(script_dir, file_path),  # Same directory as script (main/)
        file_path,  # Relative path as-is
    ]
    
    actual_path = None
    for path in possible_paths:
        normalized_path = os.path.normpath(path)
        if os.path.exists(normalized_path):
            actual_path = normalized_path
            break
    
    if not actual_path:
        print(f"⚠️  Word library file '{file_path}' not found in any of these locations:")
        for path in possible_paths:
            print(f"   - {os.path.normpath(path)}")
        print("   Using default word 'apple'.")
        return []
    
    print(f"📚 Loading word library from: {actual_path}")
    
    try:
        with open(actual_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print(f"⚠️  Invalid format in '{actual_path}'. Expected a list of words.")
            return []
        
        # Extract word texts from the library
        words = []
        for item in data:
            if isinstance(item, dict) and 'text' in item:
                words.append(item['text'])
            elif isinstance(item, str):
                words.append(item)
        
        if not words:
            print(f"⚠️  No words found in '{actual_path}'.")
            return []
        
        print(f"✅ Loaded {len(words)} words from word library: {', '.join(words[:5])}{'...' if len(words) > 5 else ''}")
        print(f"   Words available: {words}")
        return words
    except json.JSONDecodeError as e:
        print(f"⚠️  Error parsing JSON from '{actual_path}': {e}")
        return []
    except Exception as e:
        print(f"⚠️  Error loading word library: {e}")
        return []


def select_word_from_library(word_library, specified_word=None, random_selection=True):
    """
    Select a word from the library.
    If specified_word is provided, validates it exists in library.
    Otherwise, returns a random word from the library (or first if random_selection=False).
    """
    if not word_library:
        return "apple"  # Default fallback
    
    if specified_word:
        # Validate that the specified word exists in library
        if specified_word.lower() in [w.lower() for w in word_library]:
            print(f"✅ Using specified word: '{specified_word}'")
            return specified_word
        else:
            print(f"⚠️  Word '{specified_word}' not found in word library.")
            print(f"   Available words: {', '.join(word_library[:10])}{'...' if len(word_library) > 10 else ''}")
            if random_selection:
                selected = random.choice(word_library)
                print(f"   Randomly selected from library: '{selected}'")
                return selected
            else:
                print(f"   Using first word from library instead: '{word_library[0]}'")
                return word_library[0]
    
    # Randomly select a word from library
    if random_selection:
        if len(word_library) == 1:
            print(f"ℹ️  Only one word in library: '{word_library[0]}'")
            return word_library[0]
        # Use random index for better randomization
        selected_index = random.randint(0, len(word_library) - 1)
        selected = word_library[selected_index]
        print(f"🎲 Randomly selected word: '{selected}' (index {selected_index} of {len(word_library)} words: {', '.join(word_library)})")
        return selected
    else:
        print(f"ℹ️  Using first word from library: '{word_library[0]}'")
        return word_library[0]


def main():
    parser = argparse.ArgumentParser(
        description='Practice pronunciation with phoneme-level feedback',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main/main2.py                           # Random word from word_library.json
  python main/main2.py --word "hello"             # Use specific word (must be in library)
  python main/main2.py --library custom.json      # Use different library file
  python main/main2.py --no-random                # Use first word instead of random
        """
    )
    parser.add_argument(
        '--word', '-w',
        type=str,
        help='Specific word to practice (must exist in word library)'
    )
    parser.add_argument(
        '--library', '-l',
        type=str,
        default='word_library.json',
        help='Path to word library JSON file (default: word_library.json)'
    )
    parser.add_argument(
        '--no-random',
        action='store_true',
        help='Use first word from library instead of random selection'
    )
    
    args = parser.parse_args()
    
    # Load word library
    word_library = load_word_library(args.library)
    
    # Debug: Show what we got
    if word_library:
        print(f"📋 Word library contains: {word_library}")
    else:
        print("⚠️  Word library is empty, using default word")
    
    # Select target word (random by default, unless --no-random or --word specified)
    random_selection_enabled = not args.no_random
    print(f"🎲 Random selection: {'ENABLED' if random_selection_enabled else 'DISABLED'}")
    target_word = select_word_from_library(word_library, args.word, random_selection=random_selection_enabled)
    
    print(f"\n🎯 Target word: '{target_word}'")
    print("=" * 50)

    while True:
        phoneme_scores, phoneme_details = assess_pronunciation_phonemes(target_word)

        if not phoneme_scores:
            print("❌ Incorrect pronunciation, let's try again.")
            continue

        print("\n📊 Phoneme-level scores:")
        # Display phonemes in order if we have details
        if phoneme_details:
            for detail in phoneme_details:
                status = "✅" if detail['score'] >= THRESHOLD else "⚠️"
                readable = azure_phoneme_to_text(detail['phoneme'])
                print(f"{status} {detail['phoneme']} ({readable}): {detail['score']:.1f}%")
        else:
            # Fallback display
            for ph, sc in phoneme_scores.items():
                readable = azure_phoneme_to_text(ph)
                status = "✅" if sc >= THRESHOLD else "⚠️"
                print(f"{status} {ph} ({readable}): {sc:.1f}%")

        give_phoneme_feedback(target_word, phoneme_scores, phoneme_details)

        # If everything was correct, break the loop
        if all(score >= THRESHOLD for score in phoneme_scores.values()):
            print("\n🎉 Great job! All phonemes are correct!")
            break



if __name__ == "__main__":
    main()