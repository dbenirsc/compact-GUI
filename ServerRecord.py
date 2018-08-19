import usb.core
import usb.util
import numpy as np
import struct
import sys

def usbinit():
# This is straight from https://github.com/walac/pyusb/blob/master/docs/tutorial.rst

# find our Seek Thermal device  289d:0010
    dev = usb.core.find(idVendor=0x289d, idProduct=0x0010)
    if dev is None:
        raise ValueError('Device not found')
# get an endpoint instance 
    dev.set_configuration()


# configuration will be the active one
# get an endpoint instance
    cfg = dev.get_active_configuration()
    intf = cfg[(0,0)]

    ep = usb.util.find_descriptor(
        intf,
        # match the first OUT endpoint
        custom_match = \
        lambda e: \
            usb.util.endpoint_direction(e.bEndpointAddress) == \
            usb.util.ENDPOINT_OUT)

    assert ep is not None

    return dev
def send_msg(dev,bmRequestType, bRequest, wValue=0, wIndex=0,
             data_or_wLength=None, timeout=None):
    assert (dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data_or_wLength, timeout) == len(data_or_wLength))

def receive_msg(dev,bmRequestType, bRequest, wValue=0,
                wIndex=0,data_or_wLength=None, timeout=None):
    zz = dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data_or_wLength, timeout) # == len(data_or_wLength))
    return zz

def deinit(dev):
    msg = '\x00\x00'
    for i in range(3):
        send_msg(dev,0x41, 0x3C, 0, 0, msg)           # 0x3c = 60  Set Operation Mode 0x0000 (Sleep)

def camerainit(dev):
    try:
        msg = '\x01'
        send_msg(dev,0x41, 0x54, 0, 0, msg)              # 0x54 = 84 Target Platform 0x01 = Android
    except Exception as e:
        deinit(dev)
        msg = '\x01'
        send_msg(dev,0x41, 0x54, 0, 0, msg)              # 0x54 = 84 Target Platform 0x01 = Android

    send_msg(dev,0x41, 0x3C, 0, 0, '\x00\x00')              # 0x3c = 60 Set operation mode    0x0000  (Sleep)
    ret1 = receive_msg(dev,0xC1, 0x4E, 0, 0, 4)             # 0x4E = 78 Get Firmware Info
    #print ret1
    #array('B', [1, 3, 0, 0])

    ret2 = receive_msg(dev,0xC1, 0x36, 0, 0, 12)            # 0x36 = 54 Read Chip ID
    #print ret2
    #array('B', [20, 0, 12, 0, 86, 0, 248, 0, 199, 0, 69, 0])

    send_msg(dev,0x41, 0x56, 0, 0, '\x20\x00\x30\x00\x00\x00')                  # 0x56 = 86 Set Factory Settings Features
    ret3 = receive_msg(dev,0xC1, 0x58, 0, 0, 0x40)                              # 0x58 = 88 Get Factory Settings
    #print ret3
    #array('B', [2, 0, 0, 0, 0, 112, 91, 69, 0, 0, 140, 65, 0, 0, 192, 65, 79, 30, 86, 62, 160, 137, 64, 63, 234, 149, 178, 60, 0, 0, 0, 0, 0, 0, 0, 0, 72, 97, 41, 66, 124, 13, 1, 61, 206, 70, 240, 181, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 66, 0, 0, 2, 67])

    send_msg(dev,0x41, 0x56, 0, 0, '\x20\x00\x50\x00\x00\x00')                  # 0x56 = 86 Set Factory Settings Features
    ret4 = receive_msg(dev,0xC1, 0x58, 0, 0, 0x40)                              # 0x58 = 88 Get Factory Settings
    #print ret4
    #array('B', [0, 0, 0, 0, 0, 0, 0, 0, 255, 255, 255, 255, 255, 255, 255, 255, 161, 248, 65, 63, 40, 127, 119, 60, 44, 101, 55, 193, 240, 133, 129, 63, 244, 253, 96, 66, 40, 15, 155, 63, 43, 127, 103, 186, 9, 144, 186, 52, 0, 0, 0, 0, 0, 0, 2, 67, 0, 0, 150, 67, 0, 0, 0, 0])

    send_msg(dev,0x41, 0x56, 0, 0, '\x0C\x00\x70\x00\x00\x00')                  # 0x56 = 86 Set Factory Settings Features
    ret5 = receive_msg(dev,0xC1, 0x58, 0, 0, 0x18)                              # 0x58 = 88 Get Factory Settings
    #print ret5
    #array('B', [0, 0, 0, 0, 255, 255, 255, 255, 190, 193, 249, 65, 205, 204, 250, 65, 48, 42, 177, 191, 200, 152, 147, 63])

    send_msg(dev,0x41, 0x56, 0, 0, '\x06\x00\x08\x00\x00\x00')                  # 0x56 = 86 Set Factory Settings Features   
    ret6 = receive_msg(dev,0xC1, 0x58, 0, 0, 0x0C)                              # 0x58 = 88 Get Factory Settings
    #print ret6
    #array('B', [49, 52, 48, 99, 49, 48, 69, 52, 50, 78, 55, 49])

    send_msg(dev,0x41, 0x3E, 0, 0, '\x08\x00')                                  # 0x3E = 62 Set Image Processing Mode 0x0008
    ret7 = receive_msg(dev,0xC1, 0x3D, 0, 0, 2)                                 # 0x3D = 61 Get Operation Mode
    #print ret7
    #array('B', [0, 0])

    send_msg(dev,0x41, 0x3E, 0, 0, '\x08\x00')                                  # 0x3E = 62 Set Image Processing Mode  0x0008
    send_msg(dev,0x41, 0x3C, 0, 0, '\x01\x00')                                  # 0x3c = 60 Set Operation Mode         0x0001  (Run)
    ret8 = receive_msg(dev,0xC1, 0x3D, 0, 0, 2)                                 # 0x3D = 61 Get Operation Mode
    #print ret8
    #array('B', [1, 0])

# Send a read frame request
def read_frame(dev):
    # Read frame in <%dH %S format 
    send_msg(dev,0x41, 0x53, 0, 0, '\xC0\x7E\x00\x00')                 # 0x53 = 83 Set Start Get Image Transfer
    try:
        data  = dev.read(0x81, 0x3F60, 1000)
        data += dev.read(0x81, 0x3F60, 1000)
        data += dev.read(0x81, 0x3F60, 1000)
        data += dev.read(0x81, 0x3F60, 1000)
    except usb.USBError as e:
        sys.exit()
    return data

	
if __name__ == "__main__":
	# Dimensions of array
	W = 208
	L = 156
	S = W*L
	
	# Usb and Camera initialization
	dev = usbinit()
	camerainit(dev)
	
	# Read in first calibration frame. The frame status is contained at [20]
	# status 1 = calibration frame, status = 3 is regular frame, ignore the others
	# for now
	status = 0
	while status != 1:
	    cal_byte = read_frame(dev)
	    status = cal_byte[20]
	    # print 'Round = %d, status = %d' % (l_round,status)
	
	cal_image = np.reshape(struct.unpack('<%dh' % S,cal_byte),(L,W))
	# Main loop continue updating images
        l_round = 0
	while 1:
	    l_round += 1
	    byte = read_frame(dev)
	    status = byte[20]
	    if status == 1:
	        cal_byte = byte
	        cal_image = np.reshape(struct.unpack('<%dh' % S,cal_byte),(L,W))
	        print 'Round = %d, status = %d' % (l_round,status)
	    elif status == 3:
	        frame_byte = byte
	        frame_image = np.reshape(struct.unpack('<%dh' % S,frame_byte),(L,W))
	        print 'Round = %d, status = %d' % (l_round,status)
	        Image = frame_image-cal_image
	        Image_scale = Image-Image.min()
	    else:
	        print 'Round = %d, status = %d' % (l_round,status)
	        continue
