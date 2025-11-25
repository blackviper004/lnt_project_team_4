from machine import I2C, Pin
from ina219 import INA219
import utime
import urequests
import network
import gc

# WiFi credentials
SSID = 'DESKTOP-46E39EE 7990'
PASSWORD = 'Desktop-911'

# ThingSpeak settings
THING_SPEAK_URL = "http://api.thingspeak.com/update"
CHANNEL_API_KEY = "I638PBS4B8SO1WN0"

# I2C initialization (SDA GP0, SCL GP1)
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)

# INA219 initialization
ina = INA219(i2c)
ina.set_calibration_32V_1A()

# Digital smoke sensor on GP14
smoke_sensor = Pin(14, Pin.IN)

# Buzzer on GP15
buzzer = Pin(15, Pin.OUT)


# Connect to WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            pass
    print("Connected:", wlan.ifconfig())


# Send data to ThingSpeak
def send_to_thingspeak(current, voltage, power, smoke_digital):
    try:
        url = "{}?api_key={}&field2={}&field3={}&field4={}&field1={}".format(
            THING_SPEAK_URL, CHANNEL_API_KEY, current, voltage, power, smoke_digital
        )

        response = urequests.get(url)
        print("TS Response:", response.text)
        response.close()
        gc.collect()

    except Exception as e:
        print("Error sending:", e)
        utime.sleep(5)


# Main
def main():
    connect_wifi()

    while True:
        try:
            # INA219 readings
            current = ina.current
            voltage = ina.bus_voltage
            power = current * voltage

            # Digital smoke detection
            smoke_digital = smoke_sensor.value()  # 0 = smoke detected

            if smoke_digital == 0:
                print("🔥🔥🔥 WARNING! Smoke Detected!")
                buzzer.value(1)
            else:
                buzzer.value(0)

            print("Current: {:.2f} mA | Voltage: {:.2f} V | Power: {:.2f} mW | Smoke: {}".format(
                current, voltage, power, smoke_digital
            ))

            # Send to ThingSpeak
            send_to_thingspeak(current, voltage, power, smoke_digital)

            # Maintain strict 15-second interval
            utime.sleep(20)

        except Exception as e:
            print("Error:", e)
            utime.sleep(2)


main()
