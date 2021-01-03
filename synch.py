from rgbxy import ColorHelper,GamutA
from signal import signal,SIGABRT, SIGINT, SIGTERM
import config
import requests
import json
import socket
import datetime
import time
import random
import os

def clean(*args):
    url = "http://192.168.1.119:16021/api/v1/WhKqKUyUscTD3ZslDpONvBrDMlQCX8tJ/state"

    payload="{\n  \"on\": {\n    \"value\": false\n  }\n}"
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("PUT", url, headers=headers, data=payload)
    print(response)
    os._exit(0)

for sig in (SIGABRT, SIGINT, SIGTERM):
    signal(sig, clean)

nanoleaf_ip = config.nanoleaf_ip
nanoleaf_udp_port = config.nanoleaf_udp_port
nanoleaf_port = config.nanoleaf_port
nanoleaf_auth_token = config.nanoleaf_auth_token
panels = config.panels

hue_ip = config.hue_ip
hue_auth_token = config.hue_auth_token
hue_light_id = config.hue_light_id

d = config.d
tHours = config.tHours
blink_duration = config.blink_duration
tMinutes = round(blink_duration * 10 / 2)
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
response = requests.request("PUT", url, headers=headers, data=payload)


url = "http://"+hue_ip+"/api/"+hue_auth_token+"/lights/"+str(hue_light_id)
payload={}
headers = {}
step = 0
prevMinutesPanel = -1
first = True

previousRgb = [-1,-1,-1]

while True:
    #get the state of hue light
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        light = json.loads(response.text)
        on = light["state"]["on"]
        bri = light["state"]["bri"]
        x = light["state"]["xy"][0]
        y = light["state"]["xy"][1]
        ct = light["state"]["ct"]
        if (first == True):
            tBg = 10
            first = False
        else:
            tBg = ct - 20
    except:
        on = False

    if on == True:
        #if the light is on we get its color
        rgb = converter.get_rgb_from_xy_and_brightness(x,y,bri)
    else:
        #if the light is off we get a random color
        if (first == True):
            tBg = 10
            first = False
        else:
            tBg = blink_duration * 100 - 50

        ok = False
        if step == 0:
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

    newcolor = False
    #get random variations of color for each panel
    if (rgb[0] != previousRgb[0]) or (rgb[1] != previousRgb[1]) or (rgb[2] != previousRgb[2]):
        newcolor = True
        randomR = []
        randomG = []
        randomB = []
        for i in range(12):
            randomR.append(random.randint(-d,d))
            randomG.append(random.randint(-d,d))
            randomB.append(random.randint(-d,d))

    for i in range(12):
        rd = rgb[0] + randomR[i]
        if rd < 0: rd = 0
        if rd > 255: rd = 255

        gd = rgb[1] + randomG[i]
        if gd > 255: gd = 255
        if gd < 0: gd = 0

        bd = rgb[2] + randomB[i]
        if bd > 255: bd = 255
        if bd < 0: bd = 0

        r.append(rd)
        g.append(gd)
        b.append(bd)

    #print(str(rd)+":"+str(gd)+":"+str(bd))

    #get the current date / hour / minute
    date = datetime.datetime.now()
    hour = date.hour
    minute = date.minute

    rMESSAGE = []
    rMESSAGE.append((0).to_bytes(1, byteorder='big'))
    nbPanels = 0

    for j in range(12):
        if j == int(((minute) / 60) * 12):
            #panel for minutes
            prevMinutesPanel = j
            if step == 0:
                rMESSAGE.append(panels[j].to_bytes(2, byteorder='big'))
                rMESSAGE.append(r1.to_bytes(1, byteorder='big'))
                rMESSAGE.append(g1.to_bytes(1, byteorder='big'))
                rMESSAGE.append(b1.to_bytes(1, byteorder='big'))
                rMESSAGE.append((0).to_bytes(1, byteorder='big'))
                rMESSAGE.append(tMinutes.to_bytes(2, byteorder='big'))
                nbPanels += 1
            elif step == round(blink_duration / step_duration / 2):
                rMESSAGE.append(panels[j].to_bytes(2, byteorder='big'))
                rMESSAGE.append(r2.to_bytes(1, byteorder='big'))
                rMESSAGE.append(g2.to_bytes(1, byteorder='big'))
                rMESSAGE.append(b2.to_bytes(1, byteorder='big'))
                rMESSAGE.append((0).to_bytes(1, byteorder='big'))
                rMESSAGE.append(tMinutes.to_bytes(2, byteorder='big'))
                nbPanels += 1
        #panel for hours
        elif (j == (hour - 1) or j == (hour - 13)) or (j == 11 and hour == 0):
            rMESSAGE.append(panels[j].to_bytes(2, byteorder='big'))
            rMESSAGE.append(rh.to_bytes(1, byteorder='big'))
            rMESSAGE.append(gh.to_bytes(1, byteorder='big'))
            rMESSAGE.append(bh.to_bytes(1, byteorder='big'))
            rMESSAGE.append((0).to_bytes(1, byteorder='big'))
            rMESSAGE.append(tHours.to_bytes(2, byteorder='big'))
            nbPanels += 1
        #other panel
        elif (rgb[0] != previousRgb[0]) or (rgb[1] != previousRgb[1]) or (rgb[2] != previousRgb[2]) or (j == prevMinutesPanel):
                t = tBg
                if j == prevMinutesPanel:
                    t = 10
                    prevMinutesPanel = -1
                rMESSAGE.append(panels[j].to_bytes(2, byteorder='big'))
                rMESSAGE.append(r[j].to_bytes(1, byteorder='big'))
                rMESSAGE.append(g[j].to_bytes(1, byteorder='big'))
                rMESSAGE.append(b[j].to_bytes(1, byteorder='big'))
                rMESSAGE.append((0).to_bytes(1, byteorder='big'))
                rMESSAGE.append(t.to_bytes(2, byteorder='big'))
                nbPanels += 1

    if newcolor:
        previousRgb[0] = rgb[0]
        previousRgb[1] = rgb[1]
        previousRgb[2] = rgb[2]
                
    if step == round(blink_duration / step_duration):
        step = -1

    step += 1
    #first bytes = number of panels
    rMESSAGE[0]=(nbPanels).to_bytes(2, byteorder='big')

    #send the message to the nanoleaf
    MESSAGE = b''.join(rMESSAGE)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(MESSAGE, (nanoleaf_ip, nanoleaf_udp_port))

    #wait before next step
    time.sleep(step_duration)