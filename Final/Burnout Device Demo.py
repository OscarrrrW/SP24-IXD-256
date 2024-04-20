import os, sys, io
import M5
from M5 import *
from hardware import *
import time
import network
from umqtt import *
#import pygame
#import pygame.mixer
#from pygame import mixer

#pygame.init()
#mixer.init()
#music01 = mixer.music.loadf('adv_final/music01.mp3')
title0 = None
label0 = None
label1 = None
adc1 = None
adc1_val = None
adc2 = None
adc2_val = None
rgb = None
pin41 = None
button_value = None
light_status = False
sleep_status = False
ssid = 'ACCD'
password = 'tink1930'

mqtt_client = None
aio_user_name = 'OscarrrrrrW'
aio_password = 'aio_Vxad64Lwbjdy82D7DuPMkxcngfuy'

adc_timer = 0

meditation_timer = 0
meditation_end_time = 0

sleep_timer = 0
sleep_end_time = 0

#button_timer = 0
mqtt_timer = 0


def wifi_connect():
  wifi = network.WLAN(network.STA_IF)
  wifi.active(True)
  wifi.connect(ssid, password)

  print('connect to WiFi...')
  while wifi.isconnected() == False:
    print('.', end='')
    time.sleep_ms(100)

  print('WiFi connection successful')
  
  ip_list = wifi.ifconfig()
  ip_address = ip_list[0]
  print('IP address:', ip_address)



def setup():
  global label0, label1, adc1, rgb, pin41, adc2 
  global mqtt_client
  M5.begin()

  

      
  title0 = Widgets.Title("Heart Rate Detect", 3, 0x000000, 0xffffff, Widgets.FONTS.DejaVu18)
  label0 = Widgets.Label("--", 3, 20, 1.0, 0xffffff, 0x000000, Widgets.FONTS.DejaVu18)
  label1 = Widgets.Label("--", 3, 40, 1.0, 0xffffff, 0x000000, Widgets.FONTS.DejaVu18)
  
  adc1 = ADC(Pin(6), atten=ADC.ATTN_11DB)

  adc2 = ADC(Pin(8), atten=ADC.ATTN_11DB)
  
  rgb = RGB(io=2, n=30, type="SK6812")
  
  rgb.fill_color(get_color(0, 0, 0))
  
  pin41 = Pin(41, mode=Pin.IN)
  
  wifi_connect()
  mqtt_client = MQTTClient(
      'testclient',
      'io.adafruit.com',
      port = 1883,
      user = aio_user_name,
      password = aio_password,
      keepalive = 3000
  )
  mqtt_client.connect(clean_session=True)
  mqtt_client.subscribe(aio_user_name+'/feeds/stage01', feed_callback)

def feed_callback(data):
  print('received..', data[1].decode())
  
def get_color(r, g, b):
  rgb_color = (r << 16) | (g << 8) | b
  return rgb_color




def map_value(in_val, in_min, in_max, out_min, out_max):
  out_val = out_min + (in_val - in_min) * (out_max - out_min) / (in_max - in_min)
  if out_val < out_min:
    out_val = out_min
  elif out_val > out_max:
    out_val = out_max
  return int(out_val)

def loop():
  global label0, adc1, adc1_value, rgb, pin41, button_value, light_status, adc2, adc2_value, label1
  global mqtt_client
  global meditation_timer, meditation_end_time
  global sleep_status, sleep_timer, sleep_end_time
  global adc_timer
  #global meditation_timer
  #global button_timer
  global mqtt_timer
  
  M5.update()
  
  button_value = pin41.value()
  
  adc1_val = adc1.read()
  
  adc1_val_8bit = map_value(adc1_val, in_min=0, in_max=4095, out_min=0, out_max=150)
  
  adc2_val = adc2.read()
  
  adc2_val_8bit = map_value(adc2_val, in_min=0, in_max=4095, out_min=0, out_max=100)
  
  # update mqtt feed every 3 seconds:
  if time.ticks_ms() > mqtt_timer + 3000:
      # publish adc2_val_8bit to volume feed:
      print('publish volume..')
      mqtt_client.publish(aio_user_name +'/feeds/volume', str(adc2_val_8bit), qos=0)
      mqtt_timer = time.ticks_ms()  # update mqtt timer
  
  # if current time in milliseconds is more than adc timer plus half second:
  if time.ticks_ms() > adc_timer + 3000:
    if (adc1_val_8bit > 100):
        print("burnout! Need a rest! Press button to start a meditation")
    print(adc1_val_8bit)
    adc_timer = time.ticks_ms()  # update adc timer
  
  label0.setText(str(adc1_val_8bit))
  label1.setText("Volume is:"+ str(adc2_val_8bit))
  
 
  
  if BtnA.wasClicked():
      print('button clicked!')
      #if (adc1_val_8bit > 100 and button_value == 0 and not sleep_status):
      if (adc1_val_8bit > 100 and not sleep_status):
         #if (adc1_val_8bit > 100):
         #if (button_value == 0):  # button is pressed
          if (light_status == False):
              light_status = True
              
              time.sleep(5)
              rgb.fill_color(get_color(255, 0, 0))
              mqtt_client.publish(aio_user_name +'/feeds/stage01', 'ON', qos=0)
              #pygame.mixer.music.play('music01')
              print('meditation start!')
              
              time.sleep(30)
              #meditation_timer = time.ticks_ms()  # update meditation timer
              #meditation_end_time = meditation_timer + 20*1000 # set end time to 20 seconds from now
              #meditation_end_time =  meditation_timer + 20*1000
              
              #if time.ticks_ms() > meditation_end_time: 
              rgb.fill_color(get_color(0, 0, 0))
              light_status = False
              print('meditation ends!')
              mqtt_client.publish(aio_user_name +'/feeds/stage01', 'OFF', qos=0)
                 #meditation_timer = time.ticks_ms() 
              
              #meditation_timer = time.ticks_ms()  # update meditation timer
              #button_timer = time.ticks_ms()
              
          elif (light_status == True):
              light_status = False
              rgb.fill_color(get_color(0, 0, 0))  
              print('meditation ends!')
              mqtt_client.publish(aio_user_name +'/feeds/stage01', 'OFF', qos=0)
          #time.sleep(1)
          time.sleep(3)
        
      
   
  
  #if time.ticks_ms() > meditation_timer + 3000:
    #print('meditation timer expired..')
    #meditation_timer = time.ticks_ms() # update meditation timer
      #if (adc1_val_8bit < 70 and button_value == 0 and not light_status and not sleep_status):
      if (adc1_val_8bit < 100 and not light_status):
          if(not sleep_status):
              print('start sleep..')
              sleep_status = True
              sleep_timer = time.ticks_ms()
              
  if (sleep_status):
                      if( adc1_val_8bit < 70):
                          print("sleep start..")
                          
                          time.sleep_ms(20000)
                          rgb.fill_color(get_color(0, 255, 0))  # set rgb color to green
                          mqtt_client.publish(aio_user_name +'/feeds/stage02', 'ON', qos=0)
                          print("music02 play")
                          
                          time.sleep_ms(40000)
                          
                          rgb.fill_color(get_color(255, 255, 0))  # set rgb color to yellow
                          mqtt_client.publish(aio_user_name +'/feeds/stage02', 'OFF', qos=0)
                          mqtt_client.publish(aio_user_name +'/feeds/stage03', 'ON', qos=0)
                          print("music03 play")
                          
                          time.sleep_ms(40000)
                          
                          rgb.fill_color(get_color(0, 0, 0)) 
                          mqtt_client.publish(aio_user_name +'/feeds/stage03', 'OFF', qos=0)
                          print("wake up end")
                          sleep_status = False
  
#               #sleep_end_time = sleep_timer + 2*1000  # set end time to 2 seconds from now
#               if time.ticks_ms() > sleep_timer + 2000:
#               #if sleep_status :
#               #if time.ticks_diff(time.ticks_ms(), sleep_end_time) > 0:  # if 20 seconds have passed
#                     rgb.fill_color(get_color(0, 255, 0))  # set rgb color to green
#                     mqtt_client.publish(aio_user_name +'/feeds/stage02', 'ON', qos=0)
#                     print("music02 play")
#               elif time.ticks_ms() > sleep_timer + 20000:
# 
#                 #elif time.ticks_diff(time.ticks_ms(), sleep_end_time) > 0:  # if 20 seconds have passed
#                     rgb.fill_color(get_color(255, 255, 0))  # set rgb color to yellow
#                     mqtt_client.publish(aio_user_name +'/feeds/stage02', 'OFF', qos=0)
#                     mqtt_client.publish(aio_user_name +'/feeds/stage03', 'ON', qos=0)
#                     print("music03 play")
#                     #sleep_end_time = time.ticks_ms() + 20*1000  # set end time to 20 seconds from now
#                 
#               if time.ticks_ms() > sleep_timer + 40000:  # if 20 seconds have passed
#                     rgb.fill_color(get_color(0, 0, 0)) 
#                     mqtt_client.publish(aio_user_name +'/feeds/stage03', 'OFF', qos=0)
#                     print("music stop")
#                     sleep_timer = time.ticks_ms()
#                     sleep_status = False

  # check the Adafruit IO feed for changes:
  mqtt_client.check_msg()

      
      






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

