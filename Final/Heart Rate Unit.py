import os, sys, io
import M5
from M5 import *
from hardware import *
import time

title0 = None
label0 = None
adc1 = None
adc1_val = None

# Constants
SAMPLE_TIME = 20  # Sample time in seconds for BPM calculation
THRESHOLD = 3000  # Threshold value to detect a beat
last_time = 0
beat_count = 0
start_time = time.ticks_ms()

def setup():
    global label0, adc1
    M5.begin()
    # Initialize display title and label:
    title0 = Widgets.Title("Heart Rate Monitor", 3, 0x000000, 0xffffff, Widgets.FONTS.DejaVu18)
    label0 = Widgets.Label("-- BPM", 3, 20, 1.0, 0xffffff, 0x000000, Widgets.FONTS.DejaVu18)
    # Initialize analog to digital converter on pin 1:
    adc1 = ADC(Pin(1), atten=ADC.ATTN_11DB)

def loop():
    global label0, adc1, adc1_val, beat_count, start_time, last_time
    M5.update()
    # Read ADC value:
    adc1_val = adc1.read()
    # Print the ADC value for debugging:
    #print("ADC Value:", adc1_val)

    # Detect heartbeat:
    current_time = time.ticks_ms()
    if adc1_val > THRESHOLD:
        # To avoid counting the same beat multiple times,
        # ensure at least some time has passed since the last beat:
        if time.ticks_diff(current_time, last_time) > 300:  # At least 200 ms between beats
            beat_count += 1
            last_time = current_time
            #print("Beat detected!")

    # Calculate BPM every SAMPLE_TIME seconds:
    if time.ticks_diff(current_time, start_time) > SAMPLE_TIME * 1000:
        bpm = beat_count * (60 / SAMPLE_TIME)
        label0.setText("{:.0f} BPM".format(bpm))
        print("Heart Rate: {:.0f} BPM".format(bpm))
        beat_count = 0
        start_time = time.ticks_ms()
    
    time.sleep_ms(500)

if __name__ == '__main__':
    try:
        setup()
        while True:
            loop()
    except (Exception, KeyboardInterrupt) as e:
        try:
            from utility import print_error_msg
            print_error_msg(e)
        except ImportError:
            print("please update to latest firmware")
