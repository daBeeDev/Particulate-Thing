#!/usr/bin/env python3

import logging
import time
import csv
import sys
from collections import deque
from pms5003 import PMS5003, ReadTimeoutError

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S")

pms5003 = PMS5003()
time.sleep(1.0)

file_name = 'sensor_readings.csv'

# Time windows in seconds
TWELVE_HOURS = 12 * 3600
ONE_HOUR = 3600
TEN = 600
FIVE = 300
ONE = 60

# Store readings in deques
recent_readings_12h = deque()
recent_readings_1h = deque()
recent_readings_10m = deque()
recent_readings_5m = deque()
recent_readings_1m = deque()

# Open the CSV file for appending readings
with open(file_name, mode='a', newline='') as file:
    writer = csv.writer(file)

    # Write a header row if file is new
    writer.writerow(["Timestamp", "PM1.0", "PM2.5", "PM10"])

    try:
        while True:
            try:
                readings = pms5003.read()
                timestamp = time.time()  # Unix timestamp for easy time comparison
                pm1_0 = round(readings.pm_ug_per_m3(1.0), 2)
                pm2_5 = round(readings.pm_ug_per_m3(2.5), 2)
                pm10 = round(readings.pm_ug_per_m3(10), 2)

                # Add new reading to both deques (12 hours and 1 hour)
                new_reading = {
                    'timestamp': timestamp,
                    'pm1_0': pm1_0,
                    'pm2_5': pm2_5,
                    'pm10': pm10
                }

		recent_readings_1m.append(new_reading)
		recent_readings_5m.append(new_reading)
		recent_readings_10m.append(new_reading)
		recent_readings_1h.append(new_reading)
                recent_readings_12h.append(new_reading)

                # Remove readings older than 12 hours and 1 hour
                cutoff_time_1m = timestamp - ONE
                cutoff_time_5m = timestamp - FIVE
                cutoff_time_10m = timestamp - TEN
                cutoff_time_12h = timestamp - TWELVE_HOURS
                cutoff_time_1h = timestamp - ONE_HOUR

		while recent_readings_1m and recent_readings_1m[0]['timestamp'] < cutoff_time_1m:
                    recent_readings_1m.popleft()

		while recent_readings_5m and recent_readings_5m[0]['timestamp'] < cutoff_time_5m:
                    recent_readings_5m.popleft()

		while recent_readings_10m and recent_readings_10m[0]['timestamp'] < cutoff_time_10m:
                    recent_readings_10m.popleft()

                while recent_readings_12h and recent_readings_12h[0]['timestamp'] < cutoff_time_12h:
                    recent_readings_12h.popleft()

                while recent_readings_1h and recent_readings_1h[0]['timestamp'] < cutoff_time_1h:
                    recent_readings_1h.popleft()

		# Calculate 1 min
                if recent_readings_1m:
                    pm1_0_mean_1m = round(sum([r['pm1_0'] for r in recent_readings_1m]) / len(recent_readings_1m), 2)
                    pm1_0_max_1m = max([r['pm1_0'] for r in recent_readings_1m])
                    pm2_5_mean_1m = round(sum([r['pm2_5'] for r in recent_readings_1m]) / len(recent_readings_1m), 2)
                    pm2_5_max_1m = max([r['pm2_5'] for r in recent_readings_1m])
                    pm10_mean_1m = round(sum([r['pm10'] for r in recent_readings_1m]) / len(recent_readings_1m), 2)
                    pm10_max_1m = max([r['pm10'] for r in recent_readings_1m])
		
		# Calculate 5 min
                if recent_readings_5m:
                    pm1_0_mean_5m = round(sum([r['pm1_0'] for r in recent_readings_5m]) / len(recent_readings_5m), 2)
                    pm1_0_max_5m = max([r['pm1_0'] for r in recent_readings_5m])
                    pm2_5_mean_5m = round(sum([r['pm2_5'] for r in recent_readings_5m]) / len(recent_readings_5m), 2)
                    pm2_5_max_5m = max([r['pm2_5'] for r in recent_readings_5m])
                    pm10_mean_5m = round(sum([r['pm10'] for r in recent_readings_5m]) / len(recent_readings_5m), 2)
                    pm10_max_5m = max([r['pm10'] for r in recent_readings_5m])

		 # Calculate 10 min
                if recent_readings_10m:
                    pm1_0_mean_10m = round(sum([r['pm1_0'] for r in recent_readings_10m]) / len(recent_readings_10m), 2)
                    pm1_0_max_10m = max([r['pm1_0'] for r in recent_readings_10m])
                    pm2_5_mean_10m = round(sum([r['pm2_5'] for r in recent_readings_10m]) / len(recent_readings_10m), 2)
                    pm2_5_max_10m = max([r['pm2_5'] for r in recent_readings_10m])
                    pm10_mean_10m = round(sum([r['pm10'] for r in recent_readings_10m]) / len(recent_readings_10m), 2)
                    pm10_max_10m = max([r['pm10'] for r in recent_readings_10m])

                # Calculate 12 hour
                if recent_readings_12h:
                    pm1_0_mean_12h = round(sum([r['pm1_0'] for r in recent_readings_12h]) / len(recent_readings_12h), 2)
                    pm1_0_max_12h = max([r['pm1_0'] for r in recent_readings_12h])
                    pm2_5_mean_12h = round(sum([r['pm2_5'] for r in recent_readings_12h]) / len(recent_readings_12h), 2)
                    pm2_5_max_12h = max([r['pm2_5'] for r in recent_readings_12h])
                    pm10_mean_12h = round(sum([r['pm10'] for r in recent_readings_12h]) / len(recent_readings_12h), 2)
                    pm10_max_12h = max([r['pm10'] for r in recent_readings_12h])

                # Calculate 1 hour
                if recent_readings_1h:
                    pm1_0_mean_1h = round(sum([r['pm1_0'] for r in recent_readings_1h]) / len(recent_readings_1h), 2)
                    pm1_0_max_1h = max([r['pm1_0'] for r in recent_readings_1h])
                    pm2_5_mean_1h = round(sum([r['pm2_5'] for r in recent_readings_1h]) / len(recent_readings_1h), 2)
                    pm2_5_max_1h = max([r['pm2_5'] for r in recent_readings_1h])
                    pm10_mean_1h = round(sum([r['pm10'] for r in recent_readings_1h]) / len(recent_readings_1h), 2)
                    pm10_max_1h = max([r['pm10'] for r in recent_readings_1h])

                # Clear the screen and print updated values
                sys.stdout.write("\033[H\033[J")  # ANSI escape sequence to clear screen
                sys.stdout.write(f"			Particulate Sensor!\n")
                sys.stdout.write(f"\n")
                sys.stdout.write(f"\n")
                sys.stdout.write(f"Sensor Readings  - PM1.0: {pm1_0}       PM2.5: {pm2_5}        PM10: {pm10}\n")
                sys.stdout.write(f"\n")
                sys.stdout.write(f"10-min Mean/Max  - PM1.0: {pm1_0_mean_10m}/{pm1_0_max_10m}, PM2.5:  {pm2_5_mean_10m}/{pm2_5_max_10m}, PM10: {pm10_mean_10m}/{pm10_max_10m}\n")
                sys.stdout.write(f"1-hour Mean/Max  - PM1.0: {pm1_0_mean_1h}/{pm1_0_max_1h}, PM2.5:  {pm2_5_mean_1h}/{pm2_5_max_1h}, PM10: {pm10_mean_1h}/{pm10_max_1h}\n")
                sys.stdout.write(f"12-hour Mean/Max - PM1.0: {pm1_0_mean_12h}/{pm1_0_max_12h}, PM2.5:  {pm2_5_mean_12h}/{pm2_5_max_12h}, PM10: {pm10_mean_12h}/{pm10_max_12h}\n")
                sys.stdout.flush()  # Forcefully flush the output buffer

                # Write the data to the CSV file
                writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp)), pm1_0, pm2_5, pm10])
            
            except ReadTimeoutError:
                logging.error("Read timeout, reinitializing PMS5003 sensor")
                pms5003 = PMS5003()

            # Add a 1-second delay between readings
            time.sleep(1)

    except KeyboardInterrupt:
        logging.info("Program interrupted. Exiting...")
        pass
