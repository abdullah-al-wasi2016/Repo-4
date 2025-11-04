import tkinter as tk
import pyaudio
import wave
import random
import webbrowser
import openai
import serial
import time
from datetime import datetime
import pyttsx3
import os

# Welcome
print("Welcome!")
time_system = datetime(2007, 1, 1, 00, 00, 00)
print(f"Time: {time_system}")

# Start
def CallApp(name, number):
    contact = []
    contact.append(name)
    contact.append(number)
    print(f"Stored Contact Data: {contact}.")

    # Record audio
    p = pyaudio.PyAudio()
    stream = p.open(
        rate=44100,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=1024
    )

    print("* Recording started...")
    frames = []
    for i in range(int(44100 * 7200 / 1024)):
        data = stream.read(1024)
        frames.append(data)
    
    print("* Recording stopped.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open('output.wav', 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(44100)
    wf.writeframes(b''.join(frames))
    wf.close()

    # Send call signals
    try:
        ser = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)
        def send_at_command(command, expected_response="OK", timeout=5):
          """Sends an AT command and waits for a response."""
        ser.write(command.encode() + b'\r\n')
        time.sleep(0.1)  # Short delay after sending
        response = b''
        start_time = time.time()
        while time.time() - start_time < timeout:
            if ser.in_waiting > 0:
                response += ser.read(ser.in_waiting)
            if expected_response.encode() in response:
                print(f"Command '{command}' sent. Response: {response.decode().strip()}")
                return True
            time.sleep(0.1)
        print(f"Command '{command}' timed out or received unexpected response.")
        print(f"Received: {response.decode().strip()}")
        return False

        try:
          if ser.isOpen():
            print(f"Serial port {ser.port} opened successfully.")

            # Initialize the modem (optional, but good practice)
            send_at_command("AT")
            send_at_command("ATE0")  # Turn off echo

            phone_number = input("Enter phone number to call: ")

            # Initiate the call
            print(f"Attempting to call {phone_number}...")
            if send_at_command(f"ATD{phone_number};", expected_response="OK", timeout=10):
                print("Call initiated. You may hear ringing or connection tones.")
                # You might need to add logic here to detect call status
                # For example, waiting for "NO CARRIER" to detect call end
            else:
                print("Failed to initiate call.")

            # Wait for a few seconds (adjust as needed)
            time.sleep(20)

            # Hang up the call
            print("Attempting to hang up...")
            if send_at_command("ATH", expected_response="OK", timeout=5):
                print("Call hung up.")
            else:
                print("Failed to hang up.")

        except serial.SerialException as e:
          print(f"Serial port error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if ser.isOpen():
            ser.close()
            print(f"Serial port {ser.port} closed.")

def tts(text):
    engine = pyttsx3.init()
    pyttsx3.speak(text)

def gpt(prompt):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-turbo",
            messages={"role": "user", "content": prompt}
        )

        response_generated = response.choices[0].message.content
        print(f"GPT: {response_generated}")

    except Exception:
        print("Error. Can't connect.")
    

def browser(url):
    try:
        browser_open = webbrowser.get("safari")
        browser_open.open(url)
    except webbrowser.Error:
        print("Error. Website is not opening.")

def game(number):
    secret = random.randint(a=1, b=100)
    if number != secret:
        print("Failed.")
    else:
        print("Yes!")

# The GUI design
def main():
    root = tk.Tk()
    name = str(input("Enter contact name:  "))
    number = str(input("Enter the contact number:  "))
    text = str(input("Enter Text for TTS:  "))
    prompt = str(input("Enter prompt for GPT:  "))
    url = str(input("Enter a website name with domain:  "))
    guess_game = int(input("Enter a number for the game:  "))

    option1 = tk.Button(root, text="Call Someone", command=lambda: CallApp(name=name, number=number))
    option2 = tk.Button(root, text="TTS", command=lambda: tts(text=text))
    option3 = tk.Button(root, text="GPT", command=lambda: gpt(prompt=prompt))
    option4 = tk.Button(root, text="Browser", command=lambda: browser(url=url))
    option5 = tk.Button(root, text="Game", command=lambda: game(number=guess_game))

    option1.pack(pady=10)
    option2.pack(pady=10)
    option3.pack(pady=10)
    option4.pack(pady=10)
    option5.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
