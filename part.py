#!/usr/bin/env python3

import logging
import time
import csv
from pms5003 import PMS5003, ReadTimeoutError
from collections import deque
from statistics import mean

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S")

logging.info("""particulates.py - Print readings from the PMS5003 particulate sensor.

Press Ctrl+C to exit!

""")

pms5003 = PMS5003()
time.sleep(1.0)

# Initialize deque to store recent readings (timestamp, pm1_0, pm2_5, pm10)
data_points = deque()

# Define time periods for 5 minutes and 1 hour in seconds
FIVE_MINUTES = 300
ONE_HOUR = 3600

def calculate_average(data, key):
    """Calculate the average of a specific key (e.g., PM1.0, PM2.5, PM10) from a list of data points."""
    if data:
        return mean([point[key] for point in data])
    return None

def filter_recent_data(data_points, duration):
    """Filter out data points older than the given duration (in seconds)."""
    cutoff_time = time.time() - duration
    return [point for point in data_points if point['timestamp'] >= cutoff_time]

# Open a CSV file for writing readings
with open('sensor_readings.csv', mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "PM1.0", "PM2.5", "PM10"])  # Write a header row

    try:
        while True:
            try:
                readings = pms5003.read()
                logging.info(readings)

                # Extract necessary data from the readings object (adjust this part based on the object structure)
                timestamp = time.time()  # Use Unix timestamp for easy time comparison
                pm1_0 = readings.pm_ug_per_m3(1.0)
                pm2_5 = readings.pm_ug_per_m3(2.5)
                pm10 = readings.pm_ug_per_m3(10)

                # Append the new reading to data_points deque
                data_points.append({
                    'timestamp': timestamp,
                    'pm1_0': pm1_0,
                    'pm2_5': pm2_5,
                    'pm10': pm10
                })

                # Also write the new data to the CSV file
                writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), pm1_0, pm2_5, pm10])

                # Filter data points for the last 5 minutes and 1 hour
                data_5_min = filter_recent_data(data_points, FIVE_MINUTES)
                data_1_hour = filter_recent_data(data_points, ONE_HOUR)

                # Calculate averages for the last 5 minutes and 1 hour
                avg_5_min_pm1_0 = calculate_average(data_5_min, 'pm1_0')
                avg_5_min_pm2_5 = calculate_average(data_5_min, 'pm2_5')
                avg_5_min_pm10 = calculate_average(data_5_min, 'pm10')

                avg_1_hour_pm1_0 = calculate_average(data_1_hour, 'pm1_0')
                avg_1_hour_pm2_5 = calculate_average(data_1_hour, 'pm2_5')
                avg_1_hour_pm10 = calculate_average(data_1_hour, 'pm10')

                # Log the averages
                logging.info(f"5-min Avg - PM1.0: {avg_5_min_pm1_0}, PM2.5: {avg_5_min_pm2_5}, PM10: {avg_5_min_pm10}")
                logging.info(f"1-hour Avg - PM1.0: {avg_1_hour_pm1_0}, PM2.5: {avg_1_hour_pm2_5}, PM10: {avg_1_hour_pm10}")
            
            except ReadTimeoutError:
                pms5003 = PMS5003()

            # Add a 1-second delay between readings
            time.sleep(1)

    except KeyboardInterrupt:
        logging.info("Program interrupted. Exiting...")
        pass
