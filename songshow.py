import time
import serial
import numpy as np
import pyaudio
import simpleaudio as sa
import threading
import os


vlc_plugin_path = r"C:\Program Files\VideoLAN\VLC64\plugins"
os.environ["VLC_PLUGIN_PATH"] = vlc_plugin_path

# Constants for PyAudio
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024  # Number of audio samples per frame

# Constants for LED mapping
LED_COUNT = 50


# Path to the audio file
AUDIO_FILE = 'alliwantforchristmasisyou.wav'

# Function to play audio using simpleaudio
def play_audio(audio_path):
    wave_obj = sa.WaveObject.from_wave_file(audio_path)
    play_obj = wave_obj.play()
    # Removed the wait_done() to make it non-blocking


# Thread to play audio
audio_thread = threading.Thread(target=play_audio, args=(AUDIO_FILE,))
audio_thread.start()

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open stream for audio input
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# Initialize serial connection to Arduino
arduino = serial.Serial(port='COM3', baudrate=115200, timeout=100)


def light_leds(frequency_data):
    print(f"Lighting LEDS")
    # Calculate brightness based on amplitude at each frequency band
    brightness_array = np.abs(frequency_data) / np.max(np.abs(frequency_data)) * 255
    brightness_mean = np.mean(brightness_array)

    # Converting the mean brightness to an integer between 0 and 255
    brightness = int(round(brightness_mean))

    # Map frequencies to LED indices
    led_indices = np.linspace(0, LED_COUNT - 1, len(brightness_array)).astype(int)
    
    # Construct LED command string
    led_commands = []
    for i, b in zip(led_indices, brightness_array):
        # Mapping frequencies to colors can be done based on the index or frequency range
        # This is a simple mapping: low frequencies are red, mids are green, highs are blue
        if i < LED_COUNT // 3:
            color = 'FF0000'  # Red
        elif i < 2 * LED_COUNT // 3:
            color = '00FF00'  # Green
        else:
            color = '0000FF'  # Blue
        if ( i == 0 ):
            led_commands.append(f'light {i} {color} {brightness} {int(b)};')
            break
        else: 
            led_commands.append(f'{i} {color} {brightness} {int(b)};')

    # Send to Arduino
    #send_command(''.join(led_commands))
    send_command('light 1 FF0000 1000 255')

def send_command(command):
    print(f"Send command called {command}")
    arduino.write(command.encode())
    time.sleep(0.5)  # Give Arduino time to respond

    # Wait for response from Arduino
    data = arduino.readline()
    if data:
        print(data.decode(), end="")  # Print response from Arduino

def analyze_stream():
    print("Starting audio analysis")
    try:
        while True:
            # Read audio stream
            data = stream.read(CHUNK, exception_on_overflow=False)
            # Convert audio data to integers
            audio_data = np.frombuffer(data, dtype=np.int16)
            # Apply FFT and take only the positive frequencies
            fft_data = np.fft.rfft(audio_data)
            # Process and light LEDs
            light_leds(fft_data)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Stopping audio analysis")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    # Terminate the PyAudio object
    p.terminate()
    # Close serial port
    arduino.close()

if __name__ == "__main__":
    analyze_stream()
