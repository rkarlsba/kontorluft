# vim:ts=4:sw=4:sts=4:et:ai

import rp2
import network
import ubinascii
import machine
import urequests as requests
import time
import ntptime
from secrets import wifi_auth
import socket
import json

office_data = {
    'configuration': {
        'tcp_port': 14142,
        'listen_address': '0.0.0.0',
    },
    'unit_data': {
        'mac_address': '',
        'ip_address':  '',
        'ip_netmask':  '',
        'ip_gateway':  '',
        'ip_dns':  '',
        'frequency': '',
    },
    'measurement_units': {
        'temperature': 'Degrees celcius (C)',
        'humidity': 'Percent (%)',
        'co2_ppm': 'Parts per million (PPM)',
        'noise': 'Decibels (dB)',
        'time': 'Seconds since the epoch (1970-01-01 00:00:00)',
    },
    'measurements': {
        'temperature': {
            'time': 0,
            'value': -300,
        },
        'humidity': {
            'time': 0,
            'value': -1,
        },
        'co2': {
            'time': 0,
            'value': -1,
        },
        'noise': {
            'time': 0,
            'value': -1,
        },
        'time': 0,
    },
    'limits': {
        'warning': {
            'temperature_max': 22,
            'temperature_min': 20,
            'humidity_min': 20,
            'humidity_max': 60,
            'co2_ppm': 1000,
#            'co_ppm':  25,
            'noise': 55,
        },
        'critical': {
            'temperature_max': 26,
            'temperature_min': 19,
            'humidity_min': 20,
            'humidity_max': 60,
            'co2_ppm': 1200,
#            'co_ppm': 100,
            'noise': 70,
        },
    },
}

# Set country to avoid possible errors
rp2.country('NO')

led = machine.Pin('LED', machine.Pin.OUT)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
# If you need to disable powersaving mode
# wlan.config(pm = 0xa11140)

# See the MAC address in the wireless chip OTP
mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
print('mac = ' + mac)
office_data['unit_data']['mac_address'] = mac
office_data['unit_data']['frequency'] = machine.freq()

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

def blabla(arg = "her burde det vært noe"):
    print(arg)
    return


def timer_blink():
    blink_once()
    
# blink
def blink_once(on_ms=200,off_ms=200):
    if (on_ms > 0):
        time.sleep(on_ms/1000)
        led.on()
        if (off_ms > 0):
            time.sleep(off_ms/1000)
    led.off()

# Define blinking function for onboard LED to indicate error codes
def blinketiblink(num_blinks):
    if (num_blinks<0):
        print("Can't blink ", num_blinks, "times")
        return
    for i in range(num_blinks):
        blink_once()

led_status_tim = machine.Timer(-1)
#led_status_tim.init(period=1000, mode=machine.Timer.PERIODIC, callback=timer_blink)
led_status_tim.init(period=2000, mode=machine.Timer.PERIODIC, callback=lambda t:led.value(not led.value()))
# led_status_tim.init(period=1000, mode=machine.Timer.PERIODIC, lambda t: led.value(not led.value()))

# Handle connection error
# Error meanings
# 0  Link Down
# 1  Link Join
# 2  Link NoIp
# 3  Link Up
# -1 Link Fail
# -2 Link NoNet
# -3 Link BadAuth

blabla()

wlan_status = wlan.status()
blinketiblink(wlan_status)

if wlan_status != 3:
    raise RuntimeError('Wi-Fi connection failed')
else:
    print('Connected')
    status = wlan.ifconfig() #  WLAN.ifconfig([(ip, subnet, gateway, dns)])
    print('ip = ' + status[0])
    office_data['unit_data']['ip_address'] = status[0];
    office_data['unit_data']['ip_netmask'] = status[1];
    office_data['unit_data']['ip_gateway'] = status[2];
    office_data['unit_data']['ip_dns'] = status[3];

    print("Local time before synchronization：%s" %str(time.localtime()))
    ntptime.settime()
    print("Local time after synchronization：%s" %str(time.localtime()))


# TCP server with socket
addr = socket.getaddrinfo(office_data['configuration']['listen_address'],
                          office_data['configuration']['tcp_port'])[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

print('Listening on', addr)

# Listen for connections
while True:
    try:
        cl, addr = s.accept()
        print('Client connected from', addr)
        r = cl.recv(1024)
        # print(r)

        office_data['measurements']['time'] = int(time.time())
        office_json = json.dumps(office_data) 
        r = str(r)
        cl.send('HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n')
        cl.send(office_json)
        cl.close()

    except OSError as e:
        cl.close()
        print('Connection closed')
