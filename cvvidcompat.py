#Copyright (c) 2020 Derek Frombach
import socket
import time
import subprocess
from PIL import Image, ImageDraw, ImageFont
import v4l2

remhost='0.0.0.0'
host='0.0.0.0'
remport=8081
port=8082
tout=5.0
buff=1500
logging=True

#Computing of Display Colors
dcolors=[]
for a in range(1,11):
    for b in range(1,11):
        for c in range(1,11):
            if not (c==b and b==a):
                dcolors.append([(256//a)-1,(256//b)-1,(256//c)-1])

#Opening the local IP and initalizing recieve buffer
q=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP/IP socket
q.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Unbind when done
q.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1) #Zero latency TCP
q.bind((host,port)) #Start server
q.listen(1) #Listen for connections

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1) #Zero latency TCP

#Initalisation of Computer Vision
classes="""unlabeled
person
bicycle
car
motorcycle
airplane
bus
train
truck
boat
traffic light
fire hydrant
street sign
stop sign
parking meter
bench
bird
cat
dog
horse
sheep
cow
elephant
bear
zebra
giraffe
hat
backpack
umbrella
shoe
eye glasses
handbag
tie
suitcase
frisbee
skis
snowboard
sports ball
kite
baseball bat
baseball glove
skateboard
surfboard
tennis racket
bottle
plate
wine glass
cup
fork
knife
spoon
bowl
banana
apple
sandwich
orange
broccoli
carrot
hot dog
pizza
donut
cake
chair
couch
potted plant
bed
mirror
dining table
window
desk
toilet
door
tv
laptop
mouse
remote
keyboard
cell phone
microwave
oven
toaster
sink
refrigerator
blender
book
clock
vase
scissors
teddy bear
hair drier
toothbrush""".splitlines()
proc=subprocess.Popen(['python3','object_rec.py'],stdout=PIPE)

#Video Loopback Connect
vid=open('/dev/video2','wr')
font=ImageFont.truetype("arial",10)

#Initalisation of log file
f=open('VidConnection.log','a') #Don't change this

#Function call speedups
tt=time.time
tp=time.perf_counter
ts=time.sleep
rdwr=socket.SHUT_RDWR
ste=socket.timeout
se=socket.error
fw=f.write
ff=f.flush

print("READY!")
addr=["NC","NC"]

#Main Loop
while True:

    #Do Not Change Anything Below, All of this is Security
    if logging:
        fw("Disconnected\n") #File Append
        fw(str(tt())+"\n")
        fw(str(addr[0])+", ")
        fw(str(addr[1])+"\n")
        ff() #Write to File

    #Connection Handler
    q.settimeout(0.1) #Set Timeout
    try:
        while True:
            try:
                conn,addr=q.accept()
            except ste:
                pass
            else:
                break
    except KeyboardInterrupt:
        q.close()
        f.close()
        break

    if logging:
        fw("Connected\n")
        fw(str(tt())+"\n")
        fw(str(addr[0])+", ")
        fw(str(addr[1])+"\n")
        ff()
    conn.settimeout(tout)

    #Also Mandatory HTTP Headers
    ostr="HTTP/1.1 200 OK\r\nConnection: close\r\nServer: PyVidStreamServer MJPEG SERVER\r\nCache-Control: no-store, no-cache, must-revalidate, pre-check=0, post-check=0, max-age=0\r\nPragma: no-cache\r\nExpires: -1\r\nAccess-Control-Allow-Origin: *\r\nContent-Type: multipart/x-mixed-replace;boundary=ThisRandomString\r\n\r\n"
    o=ostr.encode("utf-8")

    #Header Communication with Client
    cs=conn.sendall #Connection Speedup
    #Client Timeout Handler
    try:
        data=conn.recv(buff)
        if len(data)==0:
            if logging: fw("BOT!\n")
            conn.shutdown(rdwr)
            conn.close()
            continue
        cs(o) #Sending Header
        s.connect((remhost,remport))
    except ste:
        ts(0.1)
        if logging: fw("BOT!\n")
        conn.shutdown(rdwr)
        conn.close()
        continue
    except se:
        ts(0.1)
        conn.close()
        continue
    except KeyboardInterrupt:
        s.close()
        conn.shutdown(rdwr)
        conn.close()
        q.close()
        if logging:
            fw("Disconnected\n") 
            fw(str(tt())+"\n")
            fw(str(addr[0])+", ")
            fw(str(addr[1])+"\n")
            ff()
        f.close()
        break
    
    print('connected')
    sr=s.recv
    ss=s.sendall
    cr=conn.recv
    c=b''
    s.settimeout(tout)
    ss(data)
    oops=True
    while True: #CV Data Reciever
        img=Image.new('RGBA',(640,480),(0,0,0,0))
        draw=ImageDraw(img)
        n=0
        try:
            out,err=proc.communicate(timeout=0.001)
        except TimeoutExpired:
            if oops:
                out=''
            elif len(out)>1:
                out=out.decode()
                lines=out.splitlines()
                i=0
                cid=0
                conf=0.0
                l=0
                r=0
                b=0
                t=0
                w=0
                h=0
                a=0
                c=''
                text=''
                cx=0
                cy=0
                for line in lines:
                    lf=line.find
                    if lf('detectNet.Detection object')>=0:
                        i=1
                    elif i==1 and lf('ClassID')>=0:
                        cid=int(float(line[9+lf('ClassID'):].rstrip().lstrip()))
                        i=2
                    elif i==2 and lf('Confidence')>=0:
                        conf=float(line[12+lf('Confidence'):].rstrip().lstrip())
                        i=3
                    elif i==3 and lf('Left')>=0:
                        l=int(float(line[6+lf('Left'):].rstrip().lstrip()))
                        i=4
                    elif i==4 and lf('Top')>=0:
                        t=int(float(line[5+lf('Top'):].rstrip().lstrip()))
                        i=5
                    elif i==5 and lf('Right')>=0:
                        r=int(float(line[7+lf('Right'):].rstrip().lstrip()))
                        i=6
                    elif i==6 and lf('Bottom')>=0:
                        b=int(float(line[8+lf('Bottom'):].rstrip().lstrip()))
                        i=7
                    elif i==7 and lf('Width')>=0:
                        w=int(float(line[7+lf('Width'):].rstrip().lstrip()))
                        i=8
                    elif i==8 and lf('Height')>=0:
                        h=int(float(line[8+lf('Height'):].rstrip().lstrip()))
                        i=9
                    elif i==9 and lf('Area')>=0:
                        a=int(float(line[6+lf('Area'):].rstrip().lstrip()))
                        i=10
                    elif i==10 and lf('Center')>=0:
                        c=((line[8+lf('Center'):].rstrip().lstrip())[1:-1]).split(', ')
                        cx=int(float(c[0]))
                        cy=int(float(c[1]))
                        #translation time from raspberry pi to lifecam
                        b=min(round((max(b,11)-11)/2.301),479)
                        t=min(round((min(t,1068)-11)/2.301),479)
                        l=min(round((max(l,223)-223)/2.20275),639)
                        r=min(round((min(r,1695)-223)/2.20275),639)
                        text=classes[cid]+' '+(str(conf)[:4])+'%'
                        #do something with the info
                        rc,gc,bc=dcolors[n]
                        draw.rectangle([l,b,r,t],(rc,gc,bc,50),(rc,gc,bc,25))
                        draw.text((l,t),text,(rc,gc,bc,50),font=font)
                        #reset
                        n+=1
                        i=0
        if n>0:
            img=img.convert('RGB')
            bys=img.tobytes()
            vid.write(bys)
        img.close()
        try: #FPV Cam Reciever
            s.settimeout(0.001)
            while True:
                try:
                    c+=sr(buff)
                except ste:
                    break
            s.settimeout(tout)
            a = c.rfind(b'--ThisRandomString')
            if a>=0:
                ss(b'ok')
                cs(c[a:])
                c=b''
            else:
                cs(c)
                c=b''
        except ste:
            s.shutdown(rdwr)
            s.close()
            s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1) #Zero latency TCP
            conn.shutdown(rdwr)
            conn.close()
            if logging: fw("Network Issues!\n")
            print('disconnected timeout')
            break
        except se:
            s.close()
            s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1) #Zero latency TCP
            conn.close()
            print('disconnected error')
            break
        except KeyboardInterrupt:
            s.shutdown(rdwr)
            s.close()
            s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1) #Zero latency TCP
            conn.shutdown(rdwr)
            conn.close()
            print('disconnected')
            break

vid.close()
proc.terminate()
proc.close()
