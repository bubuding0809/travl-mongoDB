from datetime import datetime
import os
import utils
from dotenv import load_dotenv
from pymongo import MongoClient, WriteConcern, errors, ReadPreference, read_concern
import certifi
import generate_passengers_tickets
from bson import ObjectId

load_dotenv()

def callback(session):
  db = session.client['travl_db']
  
  # _id of user that is performing the transaction
  userId = 'cl92lvec40000obt1t62zu8ca'
  
  # _id of the flight that the user is booking
  flightId = ObjectId('636f976323bf341c1d810294')
  
  # New passenger information
  passenger = {
    **generate_passengers_tickets.generate_passenger(),
    'user': userId,
    'flights': [flightId],
  }
  
  # Insert the new passenger into the database
  new_passenger = db.Passenger.insert_one(passenger, session=session)
  
  # Update the flight balance capacity and add the new passenger id to the passenger list
  db.Flight.update_one(
    {'_id': flightId},
    {'$inc': {'balanceCapacity': -1}, '$push': {'passengers': new_passenger.inserted_id}},
    session=session
  )
  
  # Generate a ticket for the passenger and insert into the database
  ticket_seat, ticket_class = generate_passengers_tickets.generate_ticket_info(250)
  time_stamp = datetime.now()
  new_ticket = db.Ticket.insert_one({
    'flight': flightId,
    'passenger': new_passenger.inserted_id,
    'seat': ticket_seat,
    'class': ticket_class,
    'createdAt': time_stamp,
    'updatedAt': time_stamp,
  })
  
  # Update the user ticket list to include the new ticket
  db.User.update_one({'_id': userId}, {'$push': {'tickets': new_ticket}, 'persons': new_passenger.inserted_id})
  
  print(f'User {userId} purchased ticket {new_ticket.inserted_id} for {passenger["lastName"]} for flight {flightId}')
  
  
if __name__ == "__main__":
  wc_majority = WriteConcern("majority", wtimeout=1000)
  client = MongoClient(os.getenv('DATABASE_URL'), tlsCAFile=certifi.where())
  
  # Start a client session
  with client.start_session() as session:
    # Start a transaction with the session to execute a flight ticket purchase operation
    session.with_transaction(
      callback, 
      read_concern=read_concern.ReadConcern('local'), 
      write_concern=wc_majority, 
      read_preference=ReadPreference.PRIMARY
    )
    print('Transaction completed')

