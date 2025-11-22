"""
Bear With Me - Azure Speech Phoneme Pronunciation Assessment
Captures audio from microphone and returns phoneme-level scores.
"""

import azure.cognitiveservices.speech as speechsdk

# Azure credentials
speech_key = "key"
service_region = "eastus"


def assess_pronunciation_phonemes(target_word):
    """
    Captures audio from microphone and assesses pronunciation against target word.
    Returns a dictionary mapping phonemes to accuracy scores.
    """
    # Speech configuration
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_recognition_language = "en-US"
    
    # Audio configuration (default microphone)
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    
    # Pronunciation assessment configuration
    pronunciation_config = speechsdk.PronunciationAssessmentConfig(
        reference_text=target_word,
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
        enable_miscue=True
    )
    
    # Create recognizer
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config
    )
    pronunciation_config.apply_to(speech_recognizer)
    
    print(f"\n🎤 Say the word '{target_word}' now...")

    # Single recognition call (waits until you speak)
    result = speech_recognizer.recognize_once_async().get()
    
    # Handle cancellations
    if result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speechsdk.CancellationDetails(result)
        print(f"❌ Recognition canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"   Error details: {cancellation_details.error_details}")
        return None
    elif result.reason != speechsdk.ResultReason.RecognizedSpeech:
        print("❌ No speech recognized. Please try again.")
        return None

    # Get pronunciation assessment result
    pronunciation_result_obj = speechsdk.PronunciationAssessmentResult(result)
    print(f"✅ Recognized text: '{result.text}'")

    # Build phoneme-to-score dictionary
    phoneme_scores = {}
    if hasattr(pronunciation_result_obj, 'words') and pronunciation_result_obj.words:
        for word in pronunciation_result_obj.words:
            if hasattr(word, 'phonemes') and word.phonemes:
                for phoneme in word.phonemes:
                    phoneme_scores[phoneme.phoneme] = phoneme.accuracy_score

    return phoneme_scores


def main():
    print("="*50)
    print("🐻 Bear With Me - Azure Phoneme Pronunciation Assessment")
    print("="*50)

    # Example word to test
    target_word = "Hello"
    phoneme_scores = assess_pronunciation_phonemes(target_word)

    if phoneme_scores:
        print("\n📊 Phoneme-level scores:")
        for phoneme, score in phoneme_scores.items():
            print(f"{phoneme}: {score:.1f}%")
        print("\n✅ Assessment complete!")
    else:
        print("\n❌ Could not get phoneme scores. Check your microphone and try again.")


if __name__ == "__main__":
    main()
