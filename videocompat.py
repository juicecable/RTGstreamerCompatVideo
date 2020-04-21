#Copyright (c) 2020 Derek Frombach
import socket
import time

remhost='0.0.0.0'
host='0.0.0.0'
remport=8081
port=8082
tout=5.0
buff=1500
logging=True

#Opening the local IP and initalizing recieve buffer
q=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP/IP socket
q.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Unbind when done
q.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1) #Zero latency TCP
q.bind((host,port)) #Start server
q.listen(1) #Listen for connections
#print(conn.getsockopt(socket.IPPROTO_IP, 14))

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1) #Zero latency TCP
#print(conn.getsockopt(socket.IPPROTO_IP, 14))

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
    while True:
        try:
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
