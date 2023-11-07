import serial
import time
import pygame
import numpy as np
from pygame.sndarray import array

COM_PORT  = 'COM3'
BAUD_RATE = 115200
TIMEOUT = 100


# Initialize pygame mixer 
pygame.mixer.init() 

# Load wav file
wav_file = "alliwantforchristmasisyou.mp3"

# Load song
sound = pygame.mixer.Sound(wav_file)

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

def light_leds(audio):
    # Take FFT to get frequency bands
    fft = np.fft.fft(audio)
    
    # Map FFT frequencies to LEDs 
    # (modify this mapping as needed for your setup)
    bass = np.mean(fft[:50])  
    mid = np.mean(fft[50:250])  
    treble = np.mean(fft[250:])
    
    # Scale and convert to byte values
    bass = int(bass/100)
    mid = int(mid/100) 
    treble = int(treble/100)

    # Map frequencies to colors
    bass_color = (255, 0, 0) # red
    mid_color = (0, 255, 0) # green
    treble_color = (0, 0, 255) # blue
    
    # Create LED command strings
    leds = []
    
    # For each frequency band
    for i, color in enumerate([bass_color, mid_color, treble_color]):
    
        # Construct string
        led_cmd = f"light {i} {color} 250 250;"
        
        # Add to list
        leds.append(led_cmd)
        
    # Join into one long string    
    led_string = "".join(leds)
    # Send to Arduino
    send_command(led_string)
    
def send_command(command):
    arduino.write(bytes(command, 'utf-8'))
    time.sleep(0.05)  # Give Arduino time to respond
    if command == "off":
            arduino.close()

    # Wait for response from Arduino
    data = arduino.readline()
    if data:
        print(data.decode(), end="")  # Print response from Arduino

def play_song():
     print("Playing song")
     # Start playing audio
     pygame.mixer.music.play()

     # Stream audio analysis while playing
     while pygame.mixer.music.get_busy(): 
        audio = pygame.mixer.music.get_buffer()
        light_leds(audio)

if __name__ == "__main__":
    main()



