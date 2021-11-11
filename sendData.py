import smbus2
import bme280
from datetime import datetime

import asyncio
from azure.iot.device.aio import IoTHubDeviceClient
from device_provisioning_service import Device
import os
import sys
import json



def read_sensor_data():

    port = 1
    address = 0x76
    bus = smbus2.SMBus(port)

    bme280.load_calibration_params(bus, address)
    data = bme280.sample(bus, address)

    temp = round(data.temperature, 2)
    pressure = round(data.pressure, 2)
    humidity = round(data.humidity, 2)

    # calculates the real temperature compesating CPU heating
 
    data = {}
    data["temperature"] = temp
    data["pressure"] = pressure
    data["humidity"] = humidity

    return data


async def main():

    scopeID = "0ne00418E68"
    deviceId = "2igcbzlamnm" 
    key = "q28EJ5LplSye6kLHCO7k6jD7S8+F7LWrqkgIUxKMbrw="
    #print(os.environ)
    scopeID = os.getenv('SCOPE_ID', scopeID)
    deviceId = os.getenv('DEVICE_ID', deviceId)
    key = os.getenv('DEVICE_KEY', key)

    if scopeID is None or deviceId is None or key is None:
        print("scopeID or deviceId or key are not set - no Authentication!")
        sys.exit(1)

    dps = Device(scopeID, deviceId, key)

    conn_str = await dps.connection_string

    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)
    await device_client.connect()

    try:
        # init sensor
        data = read_sensor_data()

        print("got data from sense hat: {}".format(data))

        json_body = json.dumps(data)
        print(" message for azure: {}".format(json_body))

        await device_client.send_message(json_body)

        await asyncio.sleep(1)

    except:
        print("Unexpected error:", sys.exc_info()[0])

    await device_client.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
