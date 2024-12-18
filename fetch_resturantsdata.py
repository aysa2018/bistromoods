import requests
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Load environment variables from .env file
load_dotenv()

# Yelp API setup
API_KEY = os.getenv("YELP_API_KEY") 
headers = {"Authorization": f"Bearer {API_KEY}"}
url = "https://api.yelp.com/v3/businesses/search"

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
connection = engine.connect()
metadata = db.MetaData()
restaurants = db.Table('Restaurants', metadata, autoload_with=engine)

# Insert data into Restaurants table
Session = sessionmaker(bind=engine)
session = Session()

# Total number of restaurants to fetch
total_entries = 200
limit_per_request = 50  # Maximum Yelp allows per request

# Loop to fetch and insert data
for offset in range(0, total_entries, limit_per_request):
    params = {
        "location": "New York, NY",
        "categories": "restaurants",
        "limit": limit_per_request,
        "offset": offset  # Increment offset for pagination according to the Yelp documentation
    }

    # Fetch data from Yelp API
    response = requests.get(url, headers=headers, params=params)
    data = response.json().get('businesses', [])
    
    for business in data:
        new_entry = {
            'Name': business['name'],
            'Address': business['location']['address1'],
            'Latitude': business['coordinates']['latitude'],
            'Longitude': business['coordinates']['longitude'],
            'CuisineType': business['categories'][0]['title'] if business['categories'] else None,
            'PriceRange': business.get('price', ''),
            'Rating': business['rating'],
            'YelpURL': business['url']
        }
        
        # Check if the restaurant already exists in the database
        existing_restaurant = session.query(restaurants).filter_by(YelpURL=new_entry['YelpURL']).first()
        
        if existing_restaurant is None:  # Only insert if it does not exist
            insert_stmt = db.insert(restaurants).values(new_entry)
            session.execute(insert_stmt)
            print(f"Inserted: {new_entry['Name']}")
        else:
            print(f"Restaurant already exists: {new_entry['Name']}")

# Commit the transaction and close the session
session.commit()
session.close()

