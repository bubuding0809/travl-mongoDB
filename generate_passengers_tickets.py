import random
from faker import Faker

def generate_ticket_info(capacity):
  row_config_map ={
    "small": ['A', 'B', 'C', 'D', 'E', 'F'],
    "large": ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
  }

  max_rows = capacity // len(row_config_map['large']) if capacity > 200 else capacity // len(row_config_map['small'])

  # Generate seat row and column
  seat_row = random.randint(1, max_rows)
  seat_col = random.choice(row_config_map['large'] if capacity > 200 else row_config_map['small'])
  
  # Get seat class based on seat row
  if seat_row <= 3:
    seat_class = 'First'
  elif 3 < seat_row <= 10:
    seat_class = 'Business'
  else:
    seat_class = 'Economy'
  
  return f"{seat_row}{seat_col}", seat_class
  
  
def generate_passenger():
  fake = Faker()
  return {
    "firstName": fake.first_name(),
    "lastName": fake.last_name(),
    "passportNumber": fake.bothify(text='?#######?', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
    "nationality": fake.country_code(
      representation="alpha-3"
      ),
    'age': random.randint(18, 80),
    'flights': []
  }
  
  
if __name__ == "__main__":
  pass