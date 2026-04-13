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
        user_contact = str(data.get('contact')).strip()
        user_pin = int(data.get('pincode'))
        user_role = data.get('role')
        user_help = data.get('helpType')
        user_name = data.get('name')

        # --- STEP 1: STRICT DUPLICATE CHECK ---
        all_records = sheet.get_all_records()
        already_exists = False
        
        for record in all_records:
            if str(record.get('Contact')) == user_contact:
                already_exists = True
                break

        # Agar data pehle se hai, toh kuch mat karo (No update, No insert)
        if not already_exists:
            new_row = [user_name, user_help, user_contact, user_pin, user_role]
            sheet.append_row(new_row)
            status_msg = "success"
        else:
            # Agar already hai, toh hum sirf matches dikhayenge, data enter nahi karenge
            status_msg = "already_existed"
        
        # --- STEP 2: MATCHING LOGIC (Results hamesha dikhenge) ---
        all_records = sheet.get_all_records()
        matches = []
        opposite_role = "Volunteer" if user_role == "User" else "User"
        
        for record in all_records:
            if record.get('Role') == opposite_role and record.get('HelpType') == user_help:
                db_pin = int(record.get('PinCode', 0))
                distance = abs(user_pin - db_pin)
                record['distance'] = distance
                matches.append(record)
        
        matches = sorted(matches, key=lambda x: x['distance'])
        
        return jsonify({
            "status": "success", 
            "message": status_msg, 
            "matches": matches
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)