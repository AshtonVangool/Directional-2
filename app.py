from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# Initialize SQLite Database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Borehole (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hole_id TEXT UNIQUE,
            azimuth REAL,
            inclination REAL,
            depth REAL,
            northing REAL,
            easting REAL,
            tvd REAL,
            deviation REAL
        )
    ''')
    conn.commit()
    conn.close()

# Serve HTML with JavaScript included properly
@app.route('/')
def home():
    return '''
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
                try {
                    const response = await fetch('/add_borehole', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(formData)
                    });
                    const result = await response.json();
                    alert(result.message);
                } catch (error) {
                    alert("Error submitting data: " + error);
                }
            }
        </script>
    </head>
    <body>
        <h1>Directional Drilling Management</h1>
        <form onsubmit="event.preventDefault(); submitBorehole();">
            Hole ID: <input type="text" id="hole_id" required><br>
            Azimuth: <input type="number" id="azimuth" required><br>
            Inclination: <input type="number" id="inclination" required><br>
            Depth: <input type="number" id="depth" required><br>
            Northing: <input type="number" id="northing" required><br>
            Easting: <input type="number" id="easting" required><br>
            TVD: <input type="number" id="tvd" required><br>
            Deviation: <input type="number" id="deviation" required><br>
            <button type="submit">Submit Borehole</button>
        </form>
    </body>
    </html>
    '''

@app.route('/add_borehole', methods=['POST'])
def add_borehole():
    data = request.json
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO Borehole (hole_id, azimuth, inclination, depth, northing, easting, tvd, deviation) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                     (data['hole_id'], data['azimuth'], data['inclination'], data['depth'],
                      data['northing'], data['easting'], data['tvd'], data['deviation']))
        conn.commit()
        return jsonify({"message": "Borehole added successfully!"})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Hole ID already exists!"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# Initialize database when app starts
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
