import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- Google Sheets Setup ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Aapki Sheet ID jo aapne link mein bheji thi
SHEET_ID = "11k63x80AQ9mkUjpyHe1QXqum4mreNGOfWwCA7gjysao"
sheet = client.open_by_key(SHEET_ID).sheet1

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/user')
def user_page():
    return render_template('user.html')

@app.route('/volunteer')
def volunteer_page():
    return render_template('volunteer.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.json
        user_name = data.get('name')
        user_help = data.get('helpType')
        user_contact = data.get('contact')
        user_pin = int(data.get('pincode'))
        user_role = data.get('role')

        # 1. Sheet mein data add karna (Name, HelpType, Contact, PinCode, Role)
        sheet.append_row([user_name, user_help, user_contact, user_pin, user_role])
        
        # 2. Matching Logic
        all_records = sheet.get_all_records()
        matches = []
        opposite_role = "Volunteer" if user_role == "User" else "User"
        
        for record in all_records:
            # Logic: Role opposite ho aur HelpType same ho
            if record.get('Role') == opposite_role and record.get('HelpType') == user_help:
                db_pin = int(record.get('PinCode', 0))
                distance = abs(user_pin - db_pin)
                record['distance'] = distance
                matches.append(record)
        
        # Kareeb wale matches pehle (Sort by distance)
        matches = sorted(matches, key=lambda x: x['distance'])
        
        return jsonify({"status": "success", "matches": matches})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)