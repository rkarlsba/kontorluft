# vim:ts=4:sw=4:sts=4:et:ai

import rp2
import network
import ubinascii
import machine
import urequests as requests
import time
from secrets import wifi_auth
import socket
import json

office_data = {
    'unit_data': {
        'mac_address': '',
        'ip_address':  '',
        'ip_mask':  '',
        'ip_gateway':  '',
        'ip_dns':  '',
    },
    'measurements': {
        'meteorology': {
            'temperature': 20.2,
            'humidity': 53.4,
            'co2_ppm': 495.2,
            'co_ppm': 3.2,
        }
        'other': {
            'noise': 67.3,
        }
    }
    'limits': {
        'warning': {
            'meteorology': {
                'temperature_max': 22,
                'temperature_min': 20,
                'humidity_min': 20,
                'humidity_max': 60,
                'co2_ppm': 1000,
                'co_ppm':  25,
            },
            'other': {
                'noise': 55,
            }
        'critical': {
            'meteorology': {
                'temperature_max': 26,
                'temperature_min': 19,
                'humidity_min': 20,
                'humidity_max': 60,
                'co2_ppm': 1200,
                'co_ppm': 100,
            },
            'other': {
                'noise': 70,
            }
        }
    }
}

# Set country to avoid possible errors
rp2.country('NO')

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
# If you need to disable powersaving mode
# wlan.config(pm = 0xa11140)

# See the MAC address in the wireless chip OTP
mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
print('mac = ' + mac)

# Other things to query
# print(wlan.config('channel'))
# print(wlan.config('essid'))
# print(wlan.config('txpower'))

# Load login data from different file for safety reasons
# ssid = wifi_auth['ssid']
# pw = wifi_auth['pw']

wlan.connect(wifi_auth['ssid'], wifi_auth['pw'])

# Wait for connection with 10 second timeout
timeout = 10
while timeout > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    timeout -= 1
    print('Waiting for connection...')
    time.sleep(1)

# Define blinking function for onboard LED to indicate error codes
def blink_onboard_led(num_blinks):
    led = machine.Pin('LED', machine.Pin.OUT)
    for i in range(num_blinks):
        led.on()
        time.sleep(.2)
        led.off()
        time.sleep(.2)

# Handle connection error
# Error meanings
# 0  Link Down
# 1  Link Join
# 2  Link NoIp
# 3  Link Up
# -1 Link Fail
# -2 Link NoNet
# -3 Link BadAuth

wlan_status = wlan.status()
blink_onboard_led(wlan_status)

if wlan_status != 3:
    raise RuntimeError('Wi-Fi connection failed')
else:
    print('Connected')
    status = wlan.ifconfig()
    print('ip = ' + status[0])
    print(status)

# Function to load in html page
def get_html(html_name):
    with open(html_name, 'r') as file:
        html = file.read()

    return html

# HTTP server with socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

print('Listening on', addr)
led = machine.Pin('LED', machine.Pin.OUT)

# Listen for connections
while True:
    try:
        cl, addr = s.accept()
        print('Client connected from', addr)
        r = cl.recv(1024)
        # print(r)

        office_json = json.dumps(office_data) 
        r = str(r)
        cl.send('HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n')
        cl.send(office_json)
        cl.close()

    except OSError as e:
        cl.close()
        print('Connection closed')
