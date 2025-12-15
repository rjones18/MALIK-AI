import boto3
import speech_recognition as sr
from playsound import playsound
import datetime
import threading
import os
import time

import customtkinter as ctk
from tkinter import END

# ========== AWS + Speech Setup ==========

polly = boto3.client('polly')
recognizer = sr.Recognizer()

def speak_with_polly(text):
    """Send text to Polly, save to mp3, and play it."""
    print(f"Malik says: {text}")
    try:
        response = polly.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Matthew'  # Change voice here if you want
        )
        out_file = "response.mp3"
        with open(out_file, 'wb') as file:
            file.write(response['AudioStream'].read())
        playsound(out_file)
        # Optional: clean up file
        try:
            os.remove(out_file)
        except OSError:
            pass
    except Exception as e:
        print(f"Polly error: {e}")

def listen_command():
    """Listen once for a command from the mic and return recognized text."""
    with sr.Microphone() as source:
        try:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
        except Exception:
            pass

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

def respond_to_command(command: str) -> str:
    """Your existing basic logic for Malik's brain."""
    command = command.lower()

    if "your name" in command:
        return "I am Malik, your intelligent assistant."
    elif "time" in command:
        return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}."
    elif "joke" in command:
        return "Why did the AI go broke? Because it had too many neural debts!"
    elif "exit" in command or "quit" in command or "shut down" in command:
        return "Shutting down. Goodbye!"
    else:
        return "I'm still learning. Please try asking something else."

# ========== UI App ==========

class MalikApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # ---- Window config ----
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")  # You can try "green" or custom themes

        self.title("MΛLIK • Voice AI")
        self.geometry("900x600")
        self.minsize(800, 500)

        # Grid layout (2 rows: header, main; 1 column)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ---- Header frame ----
        self.header_frame = ctk.CTkFrame(self, corner_radius=20)
        self.header_frame.grid(row=0, column=0, sticky="nsew", padx=16, pady=(16, 8))

        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=0)

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="MΛLIK",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=16, pady=12)

        self.status_label = ctk.CTkLabel(
            self.header_frame,
            text="Standby 💤",
            font=ctk.CTkFont(size=14, weight="normal")
        )
        self.status_label.grid(row=0, column=1, sticky="e", padx=16, pady=12)

        # ---- Main body frame ----
        self.body_frame = ctk.CTkFrame(self, corner_radius=20)
        self.body_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))

        self.body_frame.grid_rowconfigure(0, weight=1)
        self.body_frame.grid_rowconfigure(1, weight=0)
        self.body_frame.grid_columnconfigure(0, weight=1)

        # Chat display
        self.chat_box = ctk.CTkTextbox(
            self.body_frame,
            wrap="word",
            state="disabled",
            corner_radius=16,
            font=ctk.CTkFont(size=14),
            activate_scrollbars=True
        )
        self.chat_box.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)

        # Input frame
        self.input_frame = ctk.CTkFrame(self.body_frame, corner_radius=16)
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 16))

        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_columnconfigure(1, weight=0)
        self.input_frame.grid_columnconfigure(2, weight=0)

        # Text entry
        self.entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Type a message or press 🎤 to talk...",
            font=ctk.CTkFont(size=14)
        )
        self.entry.grid(row=0, column=0, sticky="ew", padx=(12, 8), pady=10)
        self.entry.bind("<Return>", self.on_enter_pressed)

        # Mic button
        self.mic_button = ctk.CTkButton(
            self.input_frame,
            text="🎤",
            width=50,
            command=self.on_mic_pressed
        )
        self.mic_button.grid(row=0, column=1, padx=(0, 8), pady=10)

        # Send button
        self.send_button = ctk.CTkButton(
            self.input_frame,
            text="Send",
            command=self.on_send_pressed
        )
        self.send_button.grid(row=0, column=2, padx=(0, 12), pady=10)

        # Welcome message
        self._append_message("Malik", "What’s good? I’m online and ready to help. 👋")

    # ---- Chat helpers ----

    def _append_message(self, speaker: str, text: str):
        """Append a nicely formatted message to the chat box."""
        self.chat_box.configure(state="normal")

        if speaker.lower() == "you":
            tag = "user"
            prefix = "🧍‍♂️ You: "
        else:
            tag = "malik"
            prefix = "🤖 Malik: "

        # Create tag styles once
        if not "user" in self.chat_box.tag_names():
            self.chat_box.tag_config("user", foreground="#91E6FF")
        if not "malik" in self.chat_box.tag_names():
            self.chat_box.tag_config("malik", foreground="#A3FF9B")

        self.chat_box.insert(END, prefix, tag)
        self.chat_box.insert(END, text + "\n\n")
        self.chat_box.yview_moveto(1.0)  # scroll to bottom

        self.chat_box.configure(state="disabled")

    def _set_status(self, text: str):
        self.status_label.configure(text=text)

    # ---- Event handlers ----

    def on_enter_pressed(self, event):
        self.on_send_pressed()

    def on_send_pressed(self):
        user_text = self.entry.get().strip()
        if not user_text:
            return

        self.entry.delete(0, END)
        self._append_message("You", user_text)

        # Handle in background so UI doesn't freeze
        threading.Thread(target=self._handle_command, args=(user_text,), daemon=True).start()

    def on_mic_pressed(self):
        """Trigger listening via microphone."""
        self._set_status("Listening 🎧…")
        self._append_message("Malik", "I’m listening… go ahead. 🎙️")

        threading.Thread(target=self._mic_listen_and_handle, daemon=True).start()

    def _mic_listen_and_handle(self):
        command = listen_command()
        self._set_status("Processing 🧠…")

        # Show what the user said
        self._append_message("You", command)

        # Then process it
        self._handle_command(command)

    def _handle_command(self, text: str):
        self._set_status("Thinking 🧠…")

        response = respond_to_command(text)

        # Speak and display response
        try:
            speak_with_polly(response)
        except Exception as e:
            print(f"Speak error: {e}")

        self._append_message("Malik", response)

        if "shutting down" in response.lower():
            self._set_status("Offline ❌")
            # Give a short delay so the last speech can finish
            time.sleep(1.5)
            self.quit()
        else:
            self._set_status("Standby 💤")


if __name__ == "__main__":
    app = MalikApp()
    app.mainloop()

