# pins chosen for rpi pico w below
import rp2
from machine import I2S
from machine import Pin

print("debug 1")

inmp443_pins = {
    'sd': Pin(6), # pin 9
    'sck': Pin(7), # pin 10
    'ws': Pin(8), # pin 11
}
print("debug 2")
# ##audio_in = I2S(I2S.NUM0,                                 # create I2S peripheral to read audio
# audio_in = I2S(1,                                 # create I2S peripheral to read audio
# #               bck=bck_pin, ws=ws_pin, sdin=sdin_pin,    # sample data from an INMP441
#                bck=inmp443_pins['sck'],
#                ws=inmp443_pins['ws'],
#                sdin=inmp443_pins['sd'],
#                standard=I2S.PHILIPS, mode=I2S.MASTER_RX, # microphone module 
#                dataformat=I2S.B32,                       
#                channelformat=I2S.RIGHT_LEFT,
#                samplerate=16000, 
#                dmacount=16,dmalen=256)
audio_in = I2S(1,
               sck=inmp443_pins['sck'],
               ws=inmp443_pins['ws'],
               sd=inmp443_pins['sd'],
#               standard=I2S.PHILIPS,
               mode=I2S.RX,
#               dataformat=I2S.B32,                       
#               channelformat=I2S.RIGHT_LEFT,
               bits=16,
               format=I2S.MONO,
               rate=22050,
               ibuf=(2*22050*1),
#               samplerate=16000, 
#               dmacount=16,
#               dmalen=256
               )

print("debug 2")
samples = bytearray(2*22050*1)                                # bytearray to receive audio samples

print("debug 3")

num_bytes_read = audio_in.readinto(samples)              # read audio samples from microphone
                                                         # note:  blocks until sample array is full
                                                         # - see optional timeout argument
                                                         # to configure maximum blocking duration
                                                         
print("debug 4")
