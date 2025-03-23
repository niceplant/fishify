from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

# Configure Upload Folder
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

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
            price INT NOT NULL,
            image_url TEXT
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

create_table()

# Serve frontend files
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/view-gear')
def view_gear():
    return render_template('va.html')

@app.route('/for-renters')
def for_renters():
    return render_template('for-renters.html')

@app.route('/become-partner')
def become_partner():
    return render_template('b.html')


# Fetch all listings
@app.route('/api/listings', methods=['GET'])
def get_listings():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, location, price, image_url FROM listings")
    listings = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify([
        {"id": row[0], "name": row[1], "location": row[2], "price": row[3], "image_url": row[4]}
        for row in listings
    ])

# Handle new listing with image upload
@app.route('/api/add-listing', methods=['POST'])
def add_listing():
    name = request.form.get("name")
    location = request.form.get("location")
    price = request.form.get("price")
    image = request.files.get("image")

    if not name or not location or not price or not image:
        return jsonify({"error": "Missing fields"}), 400

    # Save image
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
    image.save(image_path)
    image_url = f"/{image_path}"

    # Insert into database
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO listings (name, location, price, image_url) VALUES (%s, %s, %s, %s)",
                   (name, location, price, image_url))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Listing added successfully", "image_url": image_url}), 201

# Serve uploaded images


if __name__ == "__main__":
    app.run(debug=True)