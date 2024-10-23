#!/usr/bin/env python3

import logging
import time
import csv
import sys
import os
from collections import deque
from pms5003 import PMS5003, ReadTimeoutError

# Logging configuration
logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Initialize sensor
pms5003 = PMS5003()
time.sleep(1.0)

# Constants
file_name = 'sensor_readings.csv'
TWELVE_HOURS = 12 * 3600
ONE_HOUR = 3600
TEN = 600
FIVE = 300
ONE = 60

# Deques for recent readings
recent_readings = {
    '12h': deque(),
    '1h': deque(),
    '10m': deque(),
    '5m': deque(),
    '1m': deque()
}

# Start time
start_time = time.time()

# Function to write CSV header
def write_csv_header(writer):
    writer.writerow(["Timestamp", "PM1.0", "PM2.5", "PM10"])

# Function to read and process sensor data
def read_sensor_data():
    readings = pms5003.read()
    timestamp = time.time()
    pm1_0 = round(readings.pm_ug_per_m3(1.0), 2)
    pm2_5 = round(readings.pm_ug_per_m3(2.5), 2)
    pm10 = round(readings.pm_ug_per_m3(10), 2)
    
    return timestamp, pm1_0, pm2_5, pm10

# Function to add a reading to deques
def add_reading_to_deques(timestamp, pm1_0, pm2_5, pm10):
    new_reading = {
        'timestamp': timestamp,
        'pm1_0': pm1_0,
        'pm2_5': pm2_5,
        'pm10': pm10
    }
    
    for key in recent_readings:
        recent_readings[key].append(new_reading)

# Function to remove old readings from deques
def remove_old_readings(timestamp):
    for key in recent_readings:
        cutoff_time = timestamp - (ONE if key == '1m' else 
                                    FIVE if key == '5m' else 
                                    TEN if key == '10m' else 
                                    ONE_HOUR if key == '1h' else 
                                    TWELVE_HOURS)
        while recent_readings[key] and recent_readings[key][0]['timestamp'] < cutoff_time:
            recent_readings[key].popleft()

# Function to calculate mean and max values
def calculate_statistics(deque_readings):
    if not deque_readings:
        return None, None
    
    mean_value = round(sum([r['pm1_0'] for r in deque_readings]) / len(deque_readings), 2)
    max_value = max([r['pm1_0'] for r in deque_readings])
    return mean_value, max_value

# Function to display readings in terminal
def display_readings(pm1_0, pm2_5, pm10):
    sys.stdout.write("\033[H\033[J")  # Clear screen
    sys.stdout.write(f"                        Particulate Sensor!\n\n\n")
    sys.stdout.write(f"Live Sensor Readings  -  PM1.0: {pm1_0}       PM2.5: {pm2_5}        PM10: {pm10}\n\n\n")

    # Calculate statistics for each time window and display them
    for key in recent_readings:
        pm1_0_mean, pm1_0_max = calculate_statistics(recent_readings[key])
        pm2_5_mean, pm2_5_max = calculate_statistics(recent_readings[key])
        pm10_mean, pm10_max = calculate_statistics(recent_readings[key])

        if pm1_0_mean is not None:
            sys.stdout.write(f" (Mean/Max)  {key}  -  PM1.0: {pm1_0_mean:5.2f} / {pm1_0_max:4.0f} "
                             f"| PM2.5:  {pm2_5_mean:5.2f} / {pm2_5_max:4.0f} "
                             f"| PM10: {pm10_mean:5.2f} / {pm10_max:4.0f}\n")
    
    # Display runtime
    elapsed_time = time.time() - start_time
    elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
    sys.stdout.write(f"\033[999;0HRuntime: {elapsed_str}")
    sys.stdout.flush()

# Main function to run the sensor readings
def main():
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # Write header if file is new
        if os.stat(file_name).st_size == 0:
            write_csv_header(writer)

        try:
            while True:
                try:
                    timestamp, pm1_0, pm2_5, pm10 = read_sensor_data()
                    
                    # Add reading to deques
                    add_reading_to_deques(timestamp, pm1_0, pm2_5, pm10)

                    # Remove old readings
                    remove_old_readings(timestamp)

                    # Display current readings
                    display_readings(pm1_0, pm2_5, pm10)

                    # Write the data to the CSV file
                    writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp)), pm1_0, pm2_5, pm10])

                except ReadTimeoutError:
                    logging.error("Read timeout, reinitializing PMS5003 sensor")
                    global pms5003
                    pms5003 = PMS5003()

                time.sleep(1)

        except KeyboardInterrupt:
            logging.info("Program interrupted. Exiting...")

if __name__ == "__main__":
    main()
