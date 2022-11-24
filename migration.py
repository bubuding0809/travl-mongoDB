from collections import defaultdict
import os
import random
from datetime import datetime
from dotenv import load_dotenv
import pymongo
import generate_passengers_tickets
import utils

load_dotenv()

# Migration of country data embedded with currency data and covid data
def migrate_country_data(db):
  country_data = utils.load_json('./migration_data/Country.json')
  covid_data = utils.load_json('./migration_data/Covid.json')
  currency_data = utils.load_json('./migration_data/Currency.json')
  
  # Group covid data by country
  covid_map = defaultdict(list)
  for covid in covid_data:
    covid_map[covid['alpha3']].append({
      'date': datetime.strptime(covid['entryDate'], '%Y-%m-%d'),
      'totalCases': covid['totalCaseNo'],
      'totalDeaths': covid['totalDeathNo'],
      'newCases': covid['newCaseNo'],
      'newDeaths': covid['newDeathNo'],
    })
  
  currency_map = {currency['isoCode']: currency for currency in currency_data}
  
  data = []
  for country in country_data:
    data.append({
      '_id': country['alpha3'],
      'countryName': country['countryName'],
      'region': country['region'],
      'currency': currency_map[country['isoCode']],
      'covidCases': covid_map[country['alpha3']],
    })
    
  # Ensure that the Country collection is empty before migration
  db.Country.delete_many({})
  
  # Migration of country data
  db.Country.insert_many(data)
  
  # Create index for currency iso code
  db.Country.create_index([('currency.isoCode', pymongo.ASCENDING)], name='currency_isoCode_index')
  
  print('Country data migration completed')


# Migration of forex data
def migrate_forex_data(db):
  forex_data = utils.load_json('./migration_data/Forex.json')
  currency_data = utils.load_json('./migration_data/Currency.json')
  currency_map = {currency['isoCode']: currency for currency in currency_data}
  
  data = []
  for forex in forex_data:
    data.append({
      'date': datetime.strptime(forex['entryDate'], '%Y-%m-%d'),
      'rate': forex['rate'],
      'currencyBase': currency_map[forex['currencyBase']],
      'currencyAgainst': currency_map[forex['currencyAgainst']],
    })
  
  # Ensure that the Forex collection is empty before migration
  db.Forex.drop()
  
  # Migration of forex data
  db.Forex.insert_many(data)
  
  # Create compond index for base currency, against currency and date
  db.Forex.create_index([('currencyBase.isoCode', pymongo.ASCENDING), ('currencyAgainst.isoCode', pymongo.ASCENDING), ('date', pymongo.ASCENDING)], name='forex_index')
  
  print('Forex data migration completed')


# Migration of city data embedded with country data
def migrate_city_data(db):
  city_data = utils.load_json('./migration_data/City.json')
  country_data = utils.load_json('./migration_data/Country.json')
  currency_data = utils.load_json('./migration_data/Currency.json')
  
  
  country_map = {country['alpha3']: country for country in country_data}
  currency_map = {currency['isoCode']: currency for currency in currency_data}
  
  data = []
  for city in city_data:
    country = country_map[city['alpha3']]
    data.append({
      '_id': city['cid'],
      'cityName': city['cityName'],
      'location': {
        'type': 'Point',
        'coordinates': [city['longitude'], city['latitude']],
      },
      'capital': city['capital'],
      'population': city['population'],
      'country': {
        'alpha3': country['alpha3'],
        'countryName': country['countryName'],
        'region': country['region'],
        'currency': currency_map[country['isoCode']],
      }
    })
    
  # Ensure that the Covid collection is empty before migration
  db.City.delete_many({})
  
  # Migration of covid data
  db.City.insert_many(data)

  # Create full text search index on city name, country name and country alpha3
  db.City.create_index([
    ('cityName', pymongo.TEXT,),
    ('country.countryName', pymongo.TEXT), 
    ('country.alpha3', pymongo.TEXT)], 
    weights={'cityName': 2, 'country.countryName': 1,'country.alpha3': 1,}, name='text_search_index',)
  
  print('City data migration completed')
  
  
def migrate_hospital_data(db):
  city_data = utils.load_json('./migration_data/City.json')
  city_Map = {city['cid']: city for city in city_data}
  hospital_data = utils.load_json('./migration_data/Hospital.json')
  
  data = []
  for hospital in hospital_data:
    longitude = hospital['longitude'] if hospital['longitude'] else city_Map[hospital['cid']]['longitude']
    latitude = hospital['latitude'] if hospital['latitude'] else city_Map[hospital['cid']]['latitude']
    data.append({
      'hospitalName': hospital['hospitalName'],
      'address': hospital['address'],
      'phone': hospital['phoneNo'],
      'Location': {
        'type': 'Point',
        'coordinates': [longitude, latitude],
      },
      'city': hospital['cid'],
    })
  
  # Ensure that the Hospital collection is empty before migration
  db.Hospital.delete_many({})
  
  # Migration of hospital data
  db.Hospital.insert_many(data)
  
  # Create 2dsphere index on location
  db.Hospital.create_index([('Location', pymongo.GEOSPHERE)], name='location_index')
  
  print('Hospital data migration completed')


def migrate_airport_data(db):
  airport_data = utils.load_json('./migration_data/Airport.json')
  
  data=[]
  for airport in airport_data:
    data.append({
      '_id': airport['icao'],
      'iata': airport['iata'],
      'airportName': airport['airportName'],
      'Location': {
        'type': 'Point',
        'coordinates': [airport['longitude'], airport['latitude']],
      },
      'timezone': airport['timezone'],
      'city': airport['cid'],
    })
  
  # Ensure that the Airport collection is empty before migration
  db.Airport.delete_many({})
  
  # Migration of airport data
  db.Airport.insert_many(data)
  
  print('Airport data migration completed')
  

def migrate_flight_data(db):
  flight_data = utils.load_json('./migration_data/Flight.json')
  data = []
  for flight in flight_data:
    data.append({
      **flight,
      'departureDatetime': datetime.strptime(flight['departureDatetime'], '%Y-%m-%d %H:%M:%S'),
      'arrivalDatetime': datetime.strptime(flight['arrivalDatetime'], '%Y-%m-%d %H:%M:%S'),
    })

  # Ensure that the Flight collection is empty before migration
  db.Flight.drop()
  
  # Migration of flight data
  db.Flight.insert_many(data)
  
  # Create index for origin and destination airports
  db.Flight.create_index([('originAirport', pymongo.ASCENDING)], name='originAirport_index')
  db.Flight.create_index([('destinationAirport', pymongo.ASCENDING)], name='destinationAirport_index')
  db.Flight.create_index([('departureDatetime', pymongo.ASCENDING)], name='departureDatetime_index')
  
  print('Flight data migration completed')


def migrate_user_data(db):
  user_data = utils.load_json('./migration_data/User.json')
  
  data = []
  for user in user_data:
    data.append({
      '_id': user['id'],
      'email': user['email'],
      'name': user['name'],
      'image': user['image'],
      'tickets': [],
      'persons': []
    })
  
  # Ensure that the User collection is empty before migration
  db.User.delete_many({})
  
  # Migration of user data
  db.User.insert_many(data)
  
  generate_flight_ticket_purchase(db)
  
  print('User data migration completed')

  
def generate_flight_ticket_purchase(db):
  users = db.User.find()
  flights = list(db.Flight.find({}, {'totalCapacity': 1, 'balanceCapacity': 1, 'flightId': '$_id', '_id': 0}))
  
  for user in users:
    
    # for each user generate 25-40 tickets
    for i in range(random.randrange(25, 40)):
      
      # Randomly select a flight that is not full
      while True:
        flight = random.choice(flights)
        if flight['balanceCapacity'] > 0:
          break
      
      # Generate a fake passenger and insert into the database
      passenger = generate_passengers_tickets.generate_passenger()
      new_passenger = db.Passenger.insert_one({
        **passenger,
        'user': user['_id'],
        'flights': [flight['flightId']],
      })
      
      # Update the flight balance capacity and add the new passenger id to the passenger list
      flight['balanceCapacity'] -= 1
      db.Flight.update_one(
        {'_id': flight['flightId']},
        {'$inc': {'balanceCapacity': -1}, '$push': {'passengers': new_passenger.inserted_id}}
      )
      
      # Generate a ticket for the passenger and insert into the database
      ticket_seat, ticket_class = generate_passengers_tickets.generate_ticket_info(flight['totalCapacity'])
      time_stamp = datetime.now()
      new_ticket = {
        'flight': flight['flightId'],
        'passenger': new_passenger.inserted_id,
        'seat': ticket_seat,
        'class': ticket_class,
        'createdAt': time_stamp,
        'updatedAt': time_stamp,
      }
      
      # Update the user ticket list to include the new ticket
      db.User.update_one({'_id': user['_id']}, {'$push': {'tickets': new_ticket, 'persons': new_passenger.inserted_id}})
      
      print(f'User {user["name"]} purchased ticket for flight {flight["flightId"]} - ticket: {i}')
    

if __name__ == "__main__":
  connection_string = os.environ.get('DATABASE_URL')
  db = utils.load_db(connection_string, 'travl_db')
  
  migrate_country_data(db)
  migrate_forex_data(db)
  migrate_city_data(db)
  migrate_hospital_data(db)
  migrate_airport_data(db)
  migrate_flight_data(db)
  migrate_user_data(db)
  
  print('Migration completed')