import csv
import random
import matplotlib.pyplot as plt
import numpy as np

# Define the bounding box based on provided locations
min_latitude = 59.894492
max_latitude = 59.981147
min_longitude = 10.6689
max_longitude = 10.775569

def euclidean_distance(lat1, lon1, lat2, lon2):
    return np.sqrt((lon1 - lon2) ** 2 + (lat1 - lat2) ** 2)

# Function to read city locations from a CSV file
def read_locations_from_csv(file_path):
    locations = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            locations.append({
                "name": row["Location"],
                "latitude": float(row["Latitude"]),
                "longitude": float(row["Longitude"])
            })
    return locations

# Function to generate random locations within the bounding box
def generate_random_locations(num_locations=20):
    random_locations = []
    for i in range(num_locations):
        latitude = round(random.uniform(min_latitude, max_latitude), 6)
        longitude = round(random.uniform(min_longitude, max_longitude), 6)
        random_locations.append({"name": f"Spot {i+1}", "latitude": latitude, "longitude": longitude})
    return random_locations

# Function to plot locations
def plot_locations(city_locations, random_locations):
    plt.figure(figsize=(10, 8))

    # Plot city locations (blue dots)
    for location in city_locations:
        plt.scatter(location["longitude"], location["latitude"], color="blue", marker="o", label="City" if location == city_locations[0] else "")
        plt.text(location["longitude"], location["latitude"], location["name"], fontsize=8, ha='right')

    # Plot random locations (red numbered dots)
    for i, location in enumerate(random_locations):
        plt.scatter(location["longitude"], location["latitude"], color="red", marker="o", label="Random Spot" if i == 0 else "")
        plt.text(location["longitude"], location["latitude"], f"{i+1}", fontsize=8, ha='center', color="black", fontweight="bold")

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Map of Oslo Locations with Random Spots")
    plt.legend()
    plt.grid(True)
    plt.show()

# File path to CSV file (change this if needed)
csv_file_path = "data/TaxistandsOslo.csv"

# Read data and generate random locations
city_locations = read_locations_from_csv(csv_file_path)
random_locations = generate_random_locations()

# Plot all locations
plot_locations(city_locations, random_locations)

rows = 20
cols = 20
default_value = 0

matrix = [[default_value for _ in range(cols)] for _ in range(rows)]

for row in matrix:
    print(row)
