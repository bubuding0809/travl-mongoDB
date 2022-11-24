import json
import random
import geopy.distance
from datetime import datetime, timedelta


PLANE_SPEED_KM_HR = 804.672 # km per hour
PLANE_SPEED_KM_MIN = PLANE_SPEED_KM_HR / 60 # km per minute
SG_ICAO = "WSSS" # icao code
FLIGHT_COST_DOLLAR_PER_MIN = 6 # USD per minute


with open("./migration_data/Airport.json", "r") as f:
    airport_data = json.load(f)
    
icao_data_map = {airport["icao"]: airport for airport in airport_data}

def generateRandomFlightTiming(single_date, flight_time):
    hours, mins = flight_time
    randomHour = random.randint(0, 23)
    randomMinute = random.choice(list(range(0, 60, 15)))
    departDateTime = single_date + timedelta(hours=randomHour, minutes=randomMinute)
    arriveDateTime = departDateTime + timedelta(hours=hours, minutes=mins)
    
    return (departDateTime.strftime("%Y-%m-%d %H:%M:%S"), arriveDateTime.strftime("%Y-%m-%d %H:%M:%S"))


def get_flight_time(icaoOrigin, icaoDest):
    origin_x = icao_data_map[icaoOrigin]["latitude"]
    origin_y = icao_data_map[icaoOrigin]["longitude"]

    dest_x = icao_data_map[icaoDest]["latitude"]
    dest_y = icao_data_map[icaoDest]["longitude"]

    return geopy.distance.distance((origin_x, origin_y), (dest_x, dest_y)).km / PLANE_SPEED_KM_HR


def iter_date_range(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def generate_flights(from_date, to_date, flights_per_day):
    flight_data = []
    for airport in airport_data:
        if airport["icao"] == SG_ICAO or airport['iata'] is None: continue
        
        flight_time = get_flight_time(SG_ICAO, airport["icao"])
        hours = int(flight_time)
        mins = int((flight_time - hours) * 60)
        
        for single_date in iter_date_range(datetime(*from_date), datetime(*to_date)):
            for _ in range(flights_per_day):
                departDateTimeTo, arriveDateTimeTo = generateRandomFlightTiming(single_date, (hours, mins))
                departDateTimeFrom, arriveDateTimeFrom = generateRandomFlightTiming(single_date, (hours, mins))
                capacity = random.randrange(150, 300)
                
                flight_data.append({
                    "departureDatetime": departDateTimeTo,
                    "arrivalDatetime": arriveDateTimeTo,
                    "originAirport": SG_ICAO,
                    "destinationAirport": airport["icao"],
                    "priceUSD": round(flight_time * 60 *  FLIGHT_COST_DOLLAR_PER_MIN * random.uniform(0.8, 1.2), 2),
                    'totalCapacity': capacity,
                    'balanceCapacity': capacity,
                    'passengers': [],
                })
                
                flight_data.append({
                    "departureDatetime": departDateTimeFrom,
                    "arrivalDatetime": arriveDateTimeFrom,
                    "originAirport": airport["icao"],
                    "destinationAirport": SG_ICAO,
                    "priceUSD": round(flight_time * 60 *  FLIGHT_COST_DOLLAR_PER_MIN * random.uniform(0.8, 1.2), 2),
                    'totalCapacity': capacity,
                    'balanceCapacity': capacity,
                    'passengers': [],
                })
    
    return flight_data

if __name__ == "__main__":
    data = generate_flights([2022, 11, 1], [2023, 3, 1], random.randint(2, 4))
    with open("Flight.json", "w") as f:
        json.dump(data, f, indent=2)





