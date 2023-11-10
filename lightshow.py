import serial
import time
import pygame
import numpy as np
import simpleaudio as sa
import threading
import os
import pyaudio
import colorsys
from rpi_ws281x import PixelStrip, Color
import time
import serial

# Constants for serial
COM_PORT  = 'COM3'
BAUD_RATE = 115200
TIMEOUT = 100

# Constants for PyAudio
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024  # Number of audio samples per frame

# Constants for LED mapping
LED_COUNT = 50


# Path to the audio file
AUDIO_FILE = 'alliwantforchristmasisyou.wav'


def frequency_to_color(frequency_index, num_frequencies, brightness):
    # Map the frequency index to a hue between 0 and 270 degrees (you can adjust this range as needed)
    hue = (frequency_index / num_frequencies) * 270
    # Set saturation to 100% and value according to the brightness
    saturation = 1.0
    value = brightness / 255.0
    # Convert HSV to RGB
    r, g, b = colorsys.hsv_to_rgb(hue / 360, saturation, value)
    # Convert RGB from 0-1 range to 0-255 range and return as hex
    return '{:02x}{:02x}{:02x}'.format(int(r * 255), int(g * 255), int(b * 255))

# Function to play audio using simpleaudio
def play_audio(audio_path):
    wave_obj = sa.WaveObject.from_wave_file(audio_path)
    play_obj = wave_obj.play()


# Initialize PyAudio
p = pyaudio.PyAudio()

# Open stream for audio input
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# Replace 'COM3' with the serial port your Arduino is connected to.
arduino = serial.Serial(port=COM_PORT, baudrate=BAUD_RATE, timeout=TIMEOUT)

def main():
    while True:
        # Example commands to control the lights.
        # These need to match with the code on the Arduino.
        # To set a light manually, use `light <index> <color> <duration> <brightness>`
        # To light many lights at once, send `light <index> <color> <duration> <brightness>;<index> <color> <duration> <brightness>;...;<index> <color> <duration> <brightness>`

        cmd = input("Enter command (chase, sparkle, fire, wipe, rainbow, ukraine, light, song, off): ")

        if cmd == "song":
             play_song()
        else:      
            send_command(cmd)
        if cmd == "off":
            break

        # Wait for response from Arduino
        data = arduino.readline()
        if data:
            print(data.decode(), end="")  # Print response from Arduino

    arduino.close()

def light_leds(frequency_data):
    print(f"Lighting LEDS")
    # Calculate the magnitudes from the complex numbers
    magnitudes = np.abs(frequency_data)

    # Normalize the magnitudes
    normalized_magnitudes = magnitudes / np.max(magnitudes)

    # Number of frequency bins per LED
    bins_per_led = len(frequency_data) // LED_COUNT

    # Average the bins for each LED
    led_brightness = np.array([np.mean(normalized_magnitudes[i*bins_per_led:(i+1)*bins_per_led]) for i in range(LED_COUNT)])

    # Map to brightness
    brightness_values = (led_brightness * 255).astype(int)

    # Generate a color for each LED
    colors = [colorsys.hsv_to_rgb(i / LED_COUNT, 1, led_brightness[i]) for i in range(LED_COUNT)]

    # Format the colors as hexadecimal
    hex_colors = ['{:02x}{:02x}{:02x}'.format(int(r * 255), int(g * 255), int(b * 255)) for r, g, b in colors]
   
    # Construct the command strings
    led_commands = [f'light {i} {color} {brightness_values[i]};' for i, color in enumerate(hex_colors)]
        
    # Send to Arduino
    print(''.join(led_commands))
    send_command(''.join(led_commands))
    
def send_command(command):
    arduino.write(bytes(command, 'utf-8'))
    time.sleep(0.5)  # Give Arduino time to respond
    if command == "off":
            arduino.close()

    # Wait for response from Arduino
    data = arduino.readline()
    if data:
        print(data.decode('utf-8', errors='replace'), end="")

def play_song():
     print("Playing song")
     # Thread to play audio
     audio_thread = threading.Thread(target=play_audio, args=(AUDIO_FILE,))
     audio_thread.start()
     analyze_stream()

def analyze_stream():
    print("Starting audio analysis")
    try:
        while True:
            # Read new audio stream data
            data = stream.read(CHUNK, exception_on_overflow=False)
            # Process the new data
            audio_data = np.frombuffer(data, dtype=np.int16)
            fft_data = np.fft.rfft(audio_data)
            # Ensure fft_data is changing
            print(fft_data)
            # Call the function to light LEDs
            light_leds(fft_data)
            # Adjust sleep time as needed
            time.sleep(.5)
    except KeyboardInterrupt:
        print("Stopping audio analysis")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    # Terminate the PyAudio object
    p.terminate()
    # Close serial port
    arduino.close()


def get_frequency_magnitude(fft_data, freq_range, sample_rate, chunk_size):
    # Calculate the frequency of each FFT bin
    freq_bin = sample_rate / chunk_size
    start_bin = int(freq_range[0] / freq_bin)
    end_bin = int(freq_range[1] / freq_bin)
    
    # Sum the magnitudes of the FFT data in our frequency range
    magnitude = np.sum(np.abs(fft_data[start_bin:end_bin]))
    
    return magnitude

def normalize_magnitude(magnitude, num_leds, max_magnitude):
    # Scale magnitude to the range of 0 to the number of LEDs
    normalized_magnitude = np.clip((magnitude / max_magnitude), 0, 1)
    scaled_magnitude = int(normalized_magnitude * num_leds)
    
    return scaled_magnitude

def display_band_on_led(strip, led_start, led_end, magnitude):
    # Turn off all LEDs in the strip section
    for i in range(led_start, led_end):
        strip.setPixelColor(i, Color(0, 0, 0))

    # Turn on LEDs up to the calculated magnitude
    for i in range(led_start, led_start + magnitude):
        strip.setPixelColor(i, Color(0, 255, 0))  # Example: Green color

    strip.show()



if __name__ == "__main__":
    main()



