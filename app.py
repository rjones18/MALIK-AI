import boto3
import speech_recognition as sr
from playsound import playsound
import time
import os

# Initialize AWS Polly client
polly = boto3.client('polly')

# Initialize speech recognizer
recognizer = sr.Recognizer()

def speak_with_polly(text):
    print(f"Malik says: {text}")
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId='Matthew'  # Change to 'Joanna', 'Kendra', etc. if preferred
    )
    with open('response.mp3', 'wb') as file:
        file.write(response['AudioStream'].read())
    playsound("response.mp3")

def passive_listen():
    """ Listens for the wake word 'hey malik' """
    with sr.Microphone() as source:
        print("🎤 Malik is in standby. Say 'Hey Malik' to activate...")
        audio = recognizer.listen(source, phrase_time_limit=4)
        try:
            trigger = recognizer.recognize_google(audio).lower()
            print(f"🧠 Heard: {trigger}")
            if "hey malik" in trigger:
                print("✅ Wake word detected.")
                return True
        except sr.UnknownValueError:
            pass
        except sr.RequestError:
            print("⚠️ Speech recognition service error.")
    return False

def listen_command():
    with sr.Microphone() as source:
        print("🎧 Malik is listening for your command...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"🗣️ You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            return "Sorry, I didn't catch that."
        except sr.RequestError:
            return "Speech recognition service is down."

def respond_to_command(command):
    if "your name" in command:
        return "I am Malik, your intelligent assistant."
    elif "time" in command:
        import datetime
        return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}."
    elif "joke" in command:
        return "Why did the AI go broke? Because it had too many neural debts!"
    elif "exit" in command or "quit" in command:
        return "Shutting down. Goodbye!"
    else:
        return "I'm still learning. Please try asking something else."

# Main loop
if __name__ == "__main__":
    while True:
        if passive_listen():
            speak_with_polly("Whats good? What do you need?")
            command = listen_command()
            response = respond_to_command(command)
            speak_with_polly(response)
            if "shutting down" in response.lower():
                break
        time.sleep(1)
