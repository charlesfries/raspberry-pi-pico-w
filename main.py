import network
import ubinascii
import socket
from time import sleep
from machine import Pin

import keys

MAX_WAIT = 10

led = Pin("LED", Pin.OUT)


def setupUi():
    for i in range(3):
        led.on()
        sleep(0.5)
        led.off()
        sleep(0.5)


def setupNetwork():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    mac = ubinascii.hexlify(network.WLAN().config("mac"), ":").decode()
    print("MAC Address:", mac)

    print("Connecting to", keys.SSID)
    wlan.connect(keys.SSID, keys.PASSWORD)

    max_wait = MAX_WAIT
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print("Connecting...")
        sleep(1)

    if wlan.status() != 3:
        raise RuntimeError("Could not connect")
    else:
        status = wlan.ifconfig()
        print("Connected with IP Address:", status[0])
        led.on()

    return wlan


def setupServer():
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]

    connection = socket.socket()
    connection.bind(addr)
    connection.listen(1)

    while True:
        try:
            client, addr = connection.accept()
            print("Client connected from", addr[0])
            request = client.recv(1024)
            # print(request)

            request = str(request)
            led_on = request.find("/light/on")
            led_off = request.find("/light/off")
            print("LED on:", str(led_on))
            print("LED off:", str(led_off))

            state = "UNKNOWN"

            if led_on == 6:
                print("LED on")
                led.on()
                state = "ON"

            if led_off == 6:
                print("LED off")
                led.off()
                state = "OFF"

            html = (
                """
                <!DOCTYPE html>
                <html>
                    <head>
                        <title>Raspberry Pi Pico W</title>
                    </head>
                    <body>
                        <h1>Raspberry Pi Pico W</h1>
                        <p>LED is %s</p>
                        <form action="/light/on">
                            <input type="submit" value="On " />
                        </form>
                        <form action="/light/off">
                            <input type="submit" value="Off" />
                        </form>
                    </body>
                </html>
            """
                % state
            )

            client.send("HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n")
            client.send(html)
            client.close()

        except OSError as e:
            client.close()
            print("Client disconnected")


setupUi()
setupNetwork()
setupServer()
