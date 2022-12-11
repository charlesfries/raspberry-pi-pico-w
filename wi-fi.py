import network
import socket
import time
import machine

import secrets

MAX_WAIT = 10

led = machine.Pin('LED', machine.Pin.OUT)

def setupNetwork():
    print(f'Connecting to {secrets.SSID}')

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.SSID, secrets.PASSWORD)

    max_wait = MAX_WAIT
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('Connecting...')
        time.sleep(1)

    if wlan.status() != 3:
        raise RuntimeError('Could not connect')
    else:
        print('Connected')
        status = wlan.ifconfig()
        print( 'ip = ' + status[0] )

    return wlan

def setupUi():
    while (True):
        led.on()
        time.sleep(1)
        led.off()
        time.sleep(1)

def setupServer():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

    s = socket.socket()
    s.bind(addr)
    s.listen(1)

    while True:
        try:
            print('Test')

            cl, addr = s.accept()
            print('client connected from', addr)
            request = cl.recv(1024)
            print(request)

            request = str(request)
            led_on = request.find('/light/on')
            led_off = request.find('/light/off')
            print( 'led on = ' + str(led_on))
            print( 'led off = ' + str(led_off))

            stateis = "DEFAULT..."

            if led_on == 6:
                print("led on")
                led.on()
                stateis = "LED is ON"

            if led_off == 6:
                print("led off")
                led.off()
                stateis = "LED is OFF"

            html = """<!DOCTYPE html>
            <html>
                <head> <title>Pico W</title> </head>
                <body> <h1>Pico W</h1>
                    <p>%s</p>
                </body>
            </html>
            """

            response = html % stateis

            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            cl.send(response)
            cl.close()

        except OSError as e:
            cl.close()
            print('connection closed')
    
setupNetwork()
setupServer()
# setupUi()
    
