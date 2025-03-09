import csv
import random

# Define the bounding box for generating random customer locations
min_latitude = 59.894492
max_latitude = 59.981147
min_longitude = 10.6689
max_longitude = 10.775569

def generate_random_locations(num_locations=20):
    random_locations = []
    for i in range(num_locations):
        latitude = round(random.uniform(min_latitude, max_latitude), 6)
        longitude = round(random.uniform(min_longitude, max_longitude), 6)
        random_locations.append({
            "name": f"Spot {i+1}",
            "latitude": latitude,
            "longitude": longitude
        })
    return random_locations

def write_locations_to_csv(locations, file_path):
    with open(file_path, mode="w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["name", "latitude", "longitude"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for loc in locations:
            writer.writerow(loc)

if __name__ == "__main__":
    random.seed(42)  # Set seed for reproducibility
    locations = generate_random_locations(20)
    write_locations_to_csv(locations, "random_customers.csv")
    print("20 random customer locations generated and saved to random_customers.csv")
