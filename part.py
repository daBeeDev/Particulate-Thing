#!/usr/bin/env python3

import logging
import time
import csv
from pms5003 import PMS5003, ReadTimeoutError

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S")

logging.info("""particulates.py - Print readings from the PMS5003 particulate sensor.

Press Ctrl+C to exit!

""")

pms5003 = PMS5003()
time.sleep(1.0)

# Open a CSV file for writing readings
with open('sensor_readings.csv', mode='a', newline='') as file:
    writer = csv.writer(file)
    
    # Write a header row (only once at the beginning of the file if it's new)
    writer.writerow(["Timestamp", "PM1.0", "PM2.5", "PM10"])

    try:
        while True:
            try:
                readings = pms5003.read()
                logging.info(readings)

                # Extract necessary data from the readings object
                # Assuming readings is an object with attributes pm_ug_per_m3 values (adjust based on your object)
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                pm1_0 = readings.pm_ug_per_m3(1.0)
                pm2_5 = readings.pm_ug_per_m3(2.5)
                pm10 = readings.pm_ug_per_m3(10)
                
                # Write the data to the CSV file
                writer.writerow([timestamp, pm1_0, pm2_5, pm10])
            
            except ReadTimeoutError:
                pms5003 = PMS5003()
            
            # Add a 1-second delay between readings
            time.sleep(1)

    except KeyboardInterrupt:
        logging.info("Program interrupted. Exiting...")
        pass
