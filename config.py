#config nanoleaf
nanoleaf_ip = "192.168.1.119"
nanoleaf_port = 16021
nanoleaf_udp_port = 60222
nanoleaf_auth_token = "your_auth_token"
#you can find your panels ids with the following api:
#http://<nanoleaf_ip>:<nanoleaf_port>/api/v1/<auth_token>
panels = [64515,50673,27251,28493,55824,25887,51393,6638,33498,59611,32896,55135]

#config hue
hue_ip = "192.168.1.100"
hue_auth_token = "your_auth_token"
#you can find your light id with the following api:
#http://<hue_ip>/api/hue_auth_token/lights
hue_light_id = 4

#color config
#start color for minutes
r1 = 255
g1 = 255
b1 = 0

#end color for minutes
r2 = 255
g2 = 100
b2 = 0

#color for hours
rh = 255
gh = 100
bh = 0

#range for random color
d = 50

#delays
#transition time for background
tBg = 30 # = 1.5s ?      

#transition time for minutes blinking
tMinutes = 20  # = 1s ?

#duration for 1 step in seconds
step_duration = 2
