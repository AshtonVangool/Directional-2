from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# Initialize SQLite Database with Extended Features
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # Expanded Borehole Table to Cover All Features
    conn.execute('''CREATE TABLE IF NOT EXISTS Borehole (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        hole_id TEXT UNIQUE,
                        azimuth REAL,
                        inclination REAL,
                        depth REAL,
                        northing REAL,
                        easting REAL,
                        tvd REAL,
                        deviation REAL
                    )''')

    # Survey Data Table
    conn.execute('''CREATE TABLE IF NOT EXISTS Survey (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        hole_id TEXT,
                        survey_point REAL,
                        azimuth REAL,
                        inclination REAL,
                        depth REAL,
                        northing REAL,
                        easting REAL,
                        tvd REAL,
                        FOREIGN KEY (hole_id) REFERENCES Borehole(hole_id)
                    )''')

    # Collision Check Table
    conn.execute('''CREATE TABLE IF NOT EXISTS CollisionCheck (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        hole_id TEXT,
                        collision_zone_start REAL,
                        collision_zone_end REAL,
                        risk_level TEXT,
                        FOREIGN KEY (hole_id) REFERENCES Borehole(hole_id)
                    )''')

    conn.commit()
    conn.close()

# HTML Template Expanded for All Features
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Directional Drilling Management</title>
    <script>
        async function submitBorehole() {
            const formData = {
                hole_id: document.getElementById('hole_id').value,
                azimuth: parseFloat(document.getElementById('azimuth').value),
                inclination: parseFloat(document.getElementById('inclination').value),
                depth: parseFloat(document.getElementById('depth').value),
                northing: parseFloat(document.getElementById('northing').value),
                easting: parseFloat(document.getElementById('easting').value),
                tvd: parseFloat(document.getElementById('tvd').value),
                deviation: parseFloat(document.getElementById('deviation').value)
            };
            const response = await fetch('/add_borehole', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            const result = await response.json();
            alert(result.message);
            fetchBoreholes();
        }

        async function fetchBoreholes() {
            const response = await fetch('/get_boreholes');
            const boreholes = await response.json();
            const list = document.getElementById('boreholes');
            list.innerHTML = '';
            boreholes.forEach(borehole => {
                const item = document.createElement('li');
                item.textContent = `Hole ID: ${borehole.hole_id}, Azimuth: ${borehole.azimuth}`;
                list.appendChild(item);
            });
        }

        window.onload = fetchBoreholes;
    </script>
</head>
<body>
    <h1>Directional Drilling Management</h1>
    <form onsubmit="event.preventDefault(); submitBorehole();">
        Hole ID: <input type="text" id="hole_id" required><br>
        Azimuth: <input type="number" step="0.01" id="azimuth" required><br>
        Inclination: <input type="number" step="0.01" id="inclination" required><br>
        Depth: <input type="number" step="0.01" id="depth" required><br>
        Northing: <input type="number" step="0.01" id="northing" required><br>
        Easting: <input type="number" step="0.01" id="easting" required><br>
        TVD: <input type="number" step="0.01" id="tvd" required><br>
        Deviation: <input type="number" step="0.01" id="deviation" required><br>
        <button type="submit">Submit Borehole</button>
    </form>
    <h2>Borehole List</h2>
    <ul id="boreholes"></ul>
</body>
</html>
'''

# Homepage Route
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

# Add Borehole Data
@app.route('/add_borehole', methods=['POST'])
def add_borehole():
    data = request.json
    conn = get_db_connection()
    try:
        conn.execute('''INSERT INTO Borehole (hole_id, azimuth, inclination, depth, northing, easting, tvd, deviation)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                     (data['hole_id'], data['azimuth'], data['inclination'], data['depth'],
                      data['northing'], data['easting'], data['tvd'], data['deviation']))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Hole ID already exists!"}), 400
    finally:
        conn.close()

    return jsonify({"message": "Borehole added successfully!"})

# Fetch All Borehole Data
@app.route('/get_boreholes', methods=['GET'])
def get_boreholes():
    conn = get_db_connection()
    data = conn.execute('SELECT * FROM Borehole').fetchall()
    conn.close()
    return jsonify([dict(row) for row in data])

# Initialize the database on startup
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
