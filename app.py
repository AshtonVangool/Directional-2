from flask import Flask, request, jsonify, render_template_string
import sqlite3

app = Flask(__name__)

# Initialize the SQLite database
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

# ✅ HTML Template Served Directly from Flask (No External Fetch Requests)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Directional Drilling App</title>
    <script>
        async function submitData() {
            const formData = {
                hole_id: document.getElementById('hole_id').value,
                azimuth: parseFloat(document.getElementById('azimuth').value),
                inclination: parseFloat(document.getElementById('inclination').value),
                depth: parseFloat(document.getElementById('depth').value)
            };
            const response = await fetch('/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            const result = await response.json();
            alert(result.message);
        }

        async function fetchEntries() {
            const response = await fetch('/easiernav');
            const entries = await response.json();
            const list = document.getElementById('entries');
            list.innerHTML = '';
            entries.forEach(entry => {
                const item = document.createElement('li');
                item.textContent = `Hole ID: ${entry.hole_id}, Azimuth: ${entry.azimuth}`;
                list.appendChild(item);
            });
        }

        window.onload = fetchEntries;
    </script>
</head>
<body>
    <h1>Directional Drilling App</h1>
    <form onsubmit="event.preventDefault(); submitData();">
        Hole ID: <input type="text" id="hole_id" required><br>
        Azimuth: <input type="number" step="0.01" id="azimuth" required><br>
        Inclination: <input type="number" step="0.01" id="inclination" required><br>
        Depth: <input type="number" step="0.01" id="depth" required><br>
        <button type="submit">Submit</button>
    </form>
    <h2>Entries</h2>
    <ul id="entries"></ul>
</body>
</html>
'''

# ✅ Serve the HTML and Backend Together (No CORS Needed)
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

# ✅ Add Borehole Data
@app.route('/add', methods=['POST'])
def add_data():
    data = request.json
    hole_id = data['hole_id']
    azimuth = data['azimuth']
    inclination = data['inclination']
    depth = data['depth']

    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO Borehole (hole_id, azimuth, inclination, depth) VALUES (?, ?, ?, ?)',
                     (hole_id, azimuth, inclination, depth))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Hole ID already exists. Please try again."}), 400
    finally:
        conn.close()
    return jsonify({"message": "Borehole data added successfully!"})

# ✅ Fetch Borehole Data
@app.route('/easiernav', methods=['GET'])
def get_data():
    conn = get_db_connection()
    data = conn.execute('SELECT * FROM Borehole').fetchall()
    conn.close()
    return jsonify([dict(row) for row in data])

if __name__ == "__main__":
    init_db()
    app.run(debug=True)


