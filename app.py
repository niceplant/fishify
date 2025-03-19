from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Database connection
DB_NAME = "fishify"
DB_USER = "fishify_user"
DB_PASSWORD = "ncepl075"
DB_HOST = "localhost"
DB_PORT = "5432"

def connect_db():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

# Ensure the listings table exists
def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            price INT NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

create_table()

# Route to serve the frontend
@app.route('/')
def home():
    return render_template('index.html')

# Route to fetch all listings
@app.route('/api/listings', methods=['GET'])
def get_listings():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, location, price FROM listings")
    listings = cursor.fetchall()
    cursor.close()
    conn.close()

    # Convert to dictionary format
    return jsonify([
        {"id": row[0], "name": row[1], "location": row[2], "price": row[3]}
        for row in listings
    ])

# Route to add a new listing
@app.route('/api/add-listing', methods=['POST'])
def add_listing():
    data = request.json
    name = data.get("name")
    location = data.get("location")
    price = data.get("price")

    if not name or not location or not price:
        return jsonify({"error": "Missing fields"}), 400

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO listings (name, location, price) VALUES (%s, %s, %s)",
                   (name, location, price))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Listing added successfully"}), 201

if __name__ == '__main__':
    app.run(debug=True)
