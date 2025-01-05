from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# Initialize SQLite database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS Borehole (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        hole_id TEXT UNIQUE,
                        azimuth REAL,
                        inclination REAL,
                        depth REAL
                    )''')
    conn.commit()
    conn.close()

# ✅ Fixed: Proper JSON Response Handling for Errors
@app.errorhandler(500)
def handle_500_error(error):
    return jsonify({"error": "Internal Server Error", "details": str(error)}), 500

@app.errorhandler(404)
def handle_404_error(error):
    return jsonify({"error": "Resource Not Found"}), 404

# ✅ Homepage (No Change)
@app.route('/')
def home():
    return '''
    <h1>Directional Drilling App</h1>
    <form action="/add" method="post">
        Hole ID: <input type="text" name="hole_id" required><br>
        Azimuth: <input type="number" step="0.01" name="azimuth" required><br>
        Inclination: <input type="number" step="0.01" name="inclination" required><br>
        Depth: <input type="number" step="0.01" name="depth" required><br>
        <input type="submit" value="Submit">
    </form>
    <a href="/easiernav">View Data</a>
    '''

# ✅ Add Borehole Data (Improved Error Handling)
@app.route('/add', methods=['POST'])
def add_data():
    try:
        hole_id = request.form['hole_id']
        azimuth = float(request.form['azimuth'])
        inclination = float(request.form['inclination'])
        depth = float(request.form['depth'])

        conn = get_db_connection()
        conn.execute('INSERT INTO Borehole (hole_id, azimuth, inclination, depth) VALUES (?, ?, ?, ?)',
                     (hole_id, azimuth, inclination, depth))
        conn.commit()
        conn.close()
        return jsonify({"message": "Borehole data added successfully!"}), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "Duplicate Hole ID. Please use a unique ID."}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Fetch Borehole Data (Proper JSON Return)
@app.route('/easiernav', methods=['GET'])
def get_data():
    try:
        conn = get_db_connection()
        data = conn.execute('SELECT * FROM Borehole').fetchall()
        conn.close()
        return jsonify([dict(row) for row in data])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Fix for Missing Favicon Errors
@app.route('/favicon.ico')
def favicon():
    return '', 204

# ✅ Initialize Database and Run
if __name__ == "__main__":
    init_db()
    app.run(debug=True)

