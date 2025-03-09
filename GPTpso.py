#All code is generated by chatGPT
import csv
import random
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import linear_sum_assignment  # Hungarian algorithm for repair

# -----------------------------
# 1. Data Handling and Plotting
# -----------------------------

# Define the bounding box (for plotting purposes)
min_latitude = 59.894492
max_latitude = 59.981147
min_longitude = 10.6689
max_longitude = 10.775569


def euclidean_distance(lat1, lon1, lat2, lon2):
    """
    Compute Euclidean distance between two (lat, lon) points, scaled by 10.
    """
    return 10 * np.sqrt((lon1 - lon2) ** 2 + (lat1 - lat2) ** 2)


def read_locations_from_csv(file_path, name_key, lat_key, lon_key):
    """Read locations from a CSV file given the header keys."""
    locations = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            locations.append({
                "name": row[name_key],
                "latitude": float(row[lat_key]),
                "longitude": float(row[lon_key])
            })
    return locations


def plot_locations(city_locations, customer_locations):
    """Plot taxi hot-spots (blue) and customer requests (red numbered) on a map."""
    plt.figure(figsize=(10, 8))
    # Plot taxi locations
    for location in city_locations:
        plt.scatter(location["longitude"], location["latitude"], color="blue", marker="o",
                    label="Taxi Hot-Spot" if location == city_locations[0] else "")
        plt.text(location["longitude"], location["latitude"], location["name"], fontsize=8, ha='right')
    # Plot customer locations
    for i, location in enumerate(customer_locations):
        plt.scatter(location["longitude"], location["latitude"], color="red", marker="o",
                    label="Customer Request" if i == 0 else "")
        plt.text(location["longitude"], location["latitude"], f"{i + 1}", fontsize=8,
                 ha='center', color="black", fontweight="bold")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Taxi Hot-Spots and Customer Requests in Oslo")
    plt.legend()
    plt.grid(True)
    plt.show()


# File paths to CSV files
taxi_csv_file = "data/TaxistandsOslo.csv"
customers_csv_file = "random_customers.csv"

# Read taxi locations and customer locations from CSV files
taxi_locations = read_locations_from_csv(taxi_csv_file, "Location", "Latitude", "Longitude")
customer_locations = read_locations_from_csv(customers_csv_file, "name", "latitude", "longitude")
plot_locations(taxi_locations, customer_locations)


# -----------------------------
# 2. Binary PSO for Assignment
# -----------------------------
def compute_cost(X, taxi_locations, customer_locations):
    """
    Compute the total cost of an assignment matrix X (a permutation matrix).
    For each taxi i, find the customer j (where X[i][j]==1) and sum the Euclidean distances.
    """
    n = X.shape[0]
    total_cost = 0.0
    for i in range(n):
        j = np.argmax(X[i])
        total_cost += euclidean_distance(
            taxi_locations[i]["latitude"], taxi_locations[i]["longitude"],
            customer_locations[j]["latitude"], customer_locations[j]["longitude"]
        )
    return total_cost


def repair_solution(prob_matrix):
    """
    Use the Hungarian algorithm to generate a valid assignment matrix.
    Given the probability matrix, we maximize the sum of probabilities.
    Since linear_sum_assignment minimizes cost, we minimize -prob_matrix.
    Returns a valid permutation matrix X.
    """
    n = prob_matrix.shape[0]
    row_ind, col_ind = linear_sum_assignment(-prob_matrix)
    X_new = np.zeros((n, n), dtype=int)
    for i, j in zip(row_ind, col_ind):
        X_new[i, j] = 1
    return X_new


def pso_assignment(taxi_locations, customer_locations, num_particles, w, c1, c2, stagnation_limit=10):
    """
    Solve the taxi-customer assignment problem using Binary PSO.
    Each particle represents a candidate solution as an n x n permutation matrix.
    The algorithm runs until there is no improvement in the global best cost for
    'stagnation_limit' consecutive iterations.
    """
    n = len(taxi_locations)  # number of taxis/customers
    # Initialize the swarm
    swarm = []
    for _ in range(num_particles):
        # Create a random valid assignment (permutation matrix)
        perm = np.random.permutation(n)
        X = np.zeros((n, n), dtype=int)
        for i in range(n):
            X[i, perm[i]] = 1
        # Initialize a velocity matrix (continuous values)
        V = np.random.rand(n, n) * 0.1
        cost = compute_cost(X, taxi_locations, customer_locations)
        particle = {
            "X": X,
            "V": V,
            "pbest_X": X.copy(),
            "pbest_cost": cost
        }
        swarm.append(particle)

    # Initialize global best
    gbest_cost = float('inf')
    gbest_X = None
    for particle in swarm:
        if particle["pbest_cost"] < gbest_cost:
            gbest_cost = particle["pbest_cost"]
            gbest_X = particle["pbest_X"].copy()

    iteration = 0
    stagnant_counter = 0
    previous_best_cost = gbest_cost

    # Run until no improvement for 'stagnation_limit' consecutive iterations
    while stagnant_counter < stagnation_limit:
        iteration += 1
        for particle in swarm:
            r1 = np.random.rand(n, n)
            r2 = np.random.rand(n, n)
            particle["V"] = (w * particle["V"] +
                             c1 * r1 * (particle["pbest_X"] - particle["X"]) +
                             c2 * r2 * (gbest_X - particle["X"]))
            # Map velocity to probabilities using a sigmoid function
            prob_matrix = 1 / (1 + np.exp(-particle["V"]))
            # Repair solution using the Hungarian algorithm based on prob_matrix
            X_new = repair_solution(prob_matrix)
            particle["X"] = X_new

            cost = compute_cost(particle["X"], taxi_locations, customer_locations)
            if cost < particle["pbest_cost"]:
                particle["pbest_cost"] = cost
                particle["pbest_X"] = particle["X"].copy()
            if cost < gbest_cost:
                gbest_cost = cost
                gbest_X = particle["X"].copy()

        print(f"Iteration {iteration}: Global Best Cost = {gbest_cost:.4f}")

        if gbest_cost < previous_best_cost:
            stagnant_counter = 0
        else:
            stagnant_counter += 1
        previous_best_cost = gbest_cost

    print(
        f"No improvement for {stagnation_limit} consecutive iterations. Convergence achieved after {iteration} iterations.")
    return gbest_X, gbest_cost


# -----------------------------
# 3. Run Binary PSO Assignment
# -----------------------------
# Ensure we use the same number of taxis and customers
n = min(len(taxi_locations), len(customer_locations))
taxi_locations = taxi_locations[:n]
customer_locations = customer_locations[:n]

# PSO parameters
num_particles = 100
w = 1.5
c1 = 3.5
c2 = 3.5

best_assignment, best_cost = pso_assignment(taxi_locations, customer_locations, num_particles, w, c1, c2)

print("\nBest Assignment Matrix (Rows = Taxis, Columns = Customers):")
print(best_assignment)
print("Best Total Cost:", best_cost)


# -----------------------------
# 4. Plot the Final Assignment
# -----------------------------
def plot_assignment(taxi_locations, customer_locations, assignment_matrix):
    """Plot taxi locations, customer locations, and draw assignment lines."""
    plt.figure(figsize=(10, 8))
    n = assignment_matrix.shape[0]

    # Plot taxi locations (blue circles) with labels
    for i, taxi in enumerate(taxi_locations):
        plt.scatter(taxi["longitude"], taxi["latitude"], color="blue", marker="o", s=100)
        plt.text(taxi["longitude"], taxi["latitude"], f"T{i + 1}", fontsize=10, ha='right', color="blue")

    # Plot customer locations (red crosses) with labels
    for j, customer in enumerate(customer_locations):
        plt.scatter(customer["longitude"], customer["latitude"], color="red", marker="x", s=100)
        plt.text(customer["longitude"], customer["latitude"], f"C{j + 1}", fontsize=10, ha='left', color="red")

    # Draw lines from each taxi to its assigned customer
    for i in range(n):
        j = np.argmax(assignment_matrix[i])
        taxi = taxi_locations[i]
        customer = customer_locations[j]
        plt.plot([taxi["longitude"], customer["longitude"]],
                 [taxi["latitude"], customer["latitude"]],
                 "g--", lw=1)

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Final Taxi-to-Customer Assignment")
    plt.grid(True)
    plt.show()


plot_assignment(taxi_locations, customer_locations, best_assignment)
