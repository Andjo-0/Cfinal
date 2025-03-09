import csv
from dataclasses import dataclass
from typing import List
import matplotlib.pyplot as plt
import numpy as np


@dataclass
class City:
    name: str
    north: float
    east: float

@dataclass
class CityDist:
    city1: City
    city2: City
    distance_cost: float
    pheromone: float

@dataclass
class ant:
    current_city: City
    visited_cities: List[City]
    next_city: City

@dataclass
class next_move:
    city: City
    probability: float


def read_cities(filepath: str) -> List[City]:
    cities = []
    with open(filepath, newline='', encoding='latin1') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            try:
                city = City(
                    name=row['City'],
                    north=float(row['North']),
                    east=float(row['East'])
                )
                cities.append(city)
            except ValueError as e:
                print(f"Error converting row {row}: {e}")
    return cities


def plot_cities(cities: List[City], distances: List[CityDist]):
    plt.figure(figsize=(10, 8))

    # Plot each city as a blue circle
    for city in cities:
        plt.scatter(city.east, city.north, c='blue', marker='o', zorder=3)
        plt.annotate(city.name, (city.east, city.north), textcoords="offset points", xytext=(5, 5), ha='left',
                     fontsize=8)

    # Draw lines between cities and label distances
    for dist in distances:
        x_values = [dist.city1.east, dist.city2.east]
        y_values = [dist.city1.north, dist.city2.north]
        plt.plot(x_values, y_values, 'gray', linestyle='dashed', linewidth=1, alpha=0.5, zorder=2)

        # Midpoint for distance label
        mid_x = (dist.city1.east + dist.city2.east) / 2
        mid_y = (dist.city1.north + dist.city2.north) / 2
        plt.text(mid_x, mid_y, f"{dist.distance_cost:.1f}", fontsize=7, color='red', ha='center',
                 bbox=dict(facecolor='white', alpha=0.5))

    plt.xlabel("East")
    plt.ylabel("North")
    plt.title("City Locations and Distances")
    plt.grid(True, zorder=0)
    plt.show()


def euclidean_distance(city1: City, city2: City) -> float:
    return np.sqrt((city2.east - city1.east) ** 2 + (city2.north - city1.north) ** 2)

def cost_all_cities(cities: List[City]) -> List[CityDist]:
    cost_cities = []
    for i, city1 in enumerate(cities):
        for j in range(i + 1, len(cities)):  # Avoid duplicate pairs
            city2 = cities[j]
            distance = euclidean_distance(city1, city2)
            cost_cities.append(CityDist(city1, city2, distance,1))
    return cost_cities

def find_city_dist(city_dists: List[CityDist], city1: City, city2: City) -> CityDist | None: #GPT
    return next((cd for cd in city_dists
                 if (cd.city1 == city1 and cd.city2 == city2) or (cd.city1 == city2 and cd.city2 == city1)), None)

def find_sum(cities, city_dists:List[CityDist],ant):
    sum = 0
    for i in range(len(cities)):

        if ant.current_city == cities[i] or ant.visited_cities.count(cities[i])!=0:
            continue

        next_move =find_city_dist(city_dists, cities[i], ant.current_city)

        sum += next_move.distance_cost*next_move.pheromone

    return sum


def Ant_Colony_Optimization(cities: List[City], distances: List[CityDist], number_of_ants, pheromone_weight, heuristic_weight, evaporation_rate, iterations):

    ants= []

    for n in range(iterations):
        for i in range(number_of_ants):
            visited_cities = []
            city_nr = np.random.randint(0, len(cities))
            visited_cities.append(cities[city_nr])
            ant = ant(current_city=cities[city_nr],
                      visited_cities=visited_cities)
            ants.append(ant)

        for ant in ants:
            Probability = 0
            next_move_list = []
            for city in cities:

                if ant.current_city == city or ant.visited_cities.count(
                        city) != 0:  # Skips if its been already visited or if its the same city
                    continue

                next_city = find_city_dist(distances, ant.current_city, city)

                Probability = (next_city.pheromone * (1 / next_city.distance_cost)) / (find_sum(cities, distances, ant))

                move_probability = next_move(city=city, probability=Probability)
                next_move_list.append(move_probability)

            next_move_list.sort(key=lambda move: move.probability, reverse=True)

            ant.next_city = next_move_list[0]

        for dist in distances:
            dist.pheromone = (1 - evaporation_rate) * dist.pheromone

        for ant in ants:
            dist = find_city_dist(distances, ant.current_city, ant.next_city)
            dist.pheromone += 0.2


def main():
    filepath = "data/byerFixed.csv"  # Adjust the path if necessary
    cities = read_cities(filepath)
    cost_cities = cost_all_cities(cities)
    if not cities:
        print("No cities loaded!")
        return
    plot_cities(cities,cost_cities)


if __name__ == "__main__":
    main()
