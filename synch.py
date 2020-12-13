from rgbxy import ColorHelper,GamutA
import config
import requests
import json
import socket
import datetime
import time
import random

nanoleaf_ip = config.nanoleaf_ip
nanoleaf_udp_port = config.nanoleaf_udp_port
nanoleaf_port = config.nanoleaf_port
nanoleaf_auth_token = config.nanoleaf_auth_token
panels = config.panels

hue_ip = config.hue_ip
hue_auth_token = config.hue_auth_token
hue_light_id = config.hue_light_id

d = config.d
tBg = config.tBg
tMinutes = config.tMinutes
step_duration = config.step_duration

r2 = config.r2
g2 = config.g2
b2 = config.b2
r1 = config.r1
g1 = config.g1
b1 = config.b1
rh = config.rh
gh = config.gh
bh = config.bh

converter = ColorHelper(GamutA)

#start the stream mode on the nanoleaf
url = "http://"+nanoleaf_ip+":"+str(nanoleaf_port)+"/api/v1/"+nanoleaf_auth_token+"/effects"
payload="{\"write\" : {\"command\" : \"display\", \"animType\" : \"extControl\", \"extControlVersion\" : \"v2\"} }"
headers = {
  'Content-Type': 'text/plain'
}
response = requests.request("WRITE", url, headers=headers, data=payload)


url = "http://"+hue_ip+"/api/"+hue_auth_token+"/lights/"+str(hue_light_id)
payload={}
headers = {}
step = 0

while True:
    #get the state of hue light
    response = requests.request("GET", url, headers=headers, data=payload)
    
    light = json.loads(response.text)
    on = light["state"]["on"]
    bri = light["state"]["bri"]
    x = light["state"]["xy"][0]
    y = light["state"]["xy"][1]

    if on == True:
        #if the light is on we get its color
        rgb = converter.get_rgb_from_xy_and_brightness(x,y,bri)
    else:
        #if the light is off we get a random color
        ok = False
        while ok == False:
            rr = random.randint(0,255)
            gg = random.randint(0,255)
            bb = random.randint(0,255)
            rgb = [rr,gg,bb]
            #to be sure to be near to near from hour color
            if ((rr < (rh - 30)) or (rr > (rh + 30))) and ((gg < (gh - 30)) or (gg > (gh + 30))) and ((bb < (bh - 30)) or (bb > (bh + 30))):
                ok = True

    r=[]
    g=[]
    b=[]

    #get random variations of color for each panel
    for i in range(12):
        rd = rgb[0] + random.randint(0,d) - d
        if rd < 0: rd = 0
        if rd > 255: rd = 255

        gd = rgb[1] + random.randint(0,d) - d
        if gd > 255: gd = 255
        if gd < 0: gd = 0

        bd = rgb[2] + random.randint(0,d) - d
        if bd > 255: bd = 255
        if bd < 0: bd = 0

        r.append(rd)
        g.append(gd)
        b.append(bd)

    #get the current date / hour / minute
    date = datetime.datetime.now()
    hour = date.hour
    minute = date.minute

    rMESSAGE = []
    #first bytes = number of panels
    rMESSAGE.append((12).to_bytes(2, byteorder='big'))
    for j in range(12):
        if j == int(((minute) / 60) * 12):
            #panel for minutes
            if step == 0:
                rMESSAGE.append(panels[j].to_bytes(2, byteorder='big'))
                rMESSAGE.append(r1.to_bytes(1, byteorder='big'))
                rMESSAGE.append(g1.to_bytes(1, byteorder='big'))
                rMESSAGE.append(b1.to_bytes(1, byteorder='big'))
                rMESSAGE.append((0).to_bytes(1, byteorder='big'))
                rMESSAGE.append(tMinutes.to_bytes(2, byteorder='big'))
                step = 1
            else:
                rMESSAGE.append(panels[j].to_bytes(2, byteorder='big'))
                rMESSAGE.append(r2.to_bytes(1, byteorder='big'))
                rMESSAGE.append(g2.to_bytes(1, byteorder='big'))
                rMESSAGE.append(b2.to_bytes(1, byteorder='big'))
                rMESSAGE.append((0).to_bytes(1, byteorder='big'))
                rMESSAGE.append(tMinutes.to_bytes(2, byteorder='big'))
                step = 0
        #panel for hours
        elif (j == (hour - 1) or j == (hour - 13)) or (j == 11 and hour == 0):
            rMESSAGE.append(panels[j].to_bytes(2, byteorder='big'))
            rMESSAGE.append(rh.to_bytes(1, byteorder='big'))
            rMESSAGE.append(gh.to_bytes(1, byteorder='big'))
            rMESSAGE.append(bh.to_bytes(1, byteorder='big'))
            rMESSAGE.append((0).to_bytes(1, byteorder='big'))
            rMESSAGE.append(tBg.to_bytes(2, byteorder='big'))
        #other panel
        else:
            rMESSAGE.append(panels[j].to_bytes(2, byteorder='big'))
            rMESSAGE.append(r[j].to_bytes(1, byteorder='big'))
            rMESSAGE.append(g[j].to_bytes(1, byteorder='big'))
            rMESSAGE.append(b[j].to_bytes(1, byteorder='big'))
            rMESSAGE.append((0).to_bytes(1, byteorder='big'))
            rMESSAGE.append(tBg.to_bytes(2, byteorder='big'))

    #send the message to the nanoleaf
    MESSAGE = b''.join(rMESSAGE)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(MESSAGE, (nanoleaf_ip, nanoleaf_udp_port))

    #wait before next stepÒ
    time.sleep(step_duration)