import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- SMART GOOGLE SHEETS SETUP (Vercel + Local) ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Vercel par hum 'GOOGLE_CREDENTIALS' naam ka variable use karenge
creds_raw = os.environ.get('GOOGLE_CREDENTIALS')

try:
    if creds_raw:
        # Agar Vercel environment mein credentials mil gayi
        creds_info = json.loads(creds_raw)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
    else:
        # Local system ke liye credentials.json file
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    
    client = gspread.authorize(creds)
    SHEET_ID = "11k63x80AQ9mkUjpyHe1QXqum4mreNGOfWwCA7gjysao"
    sheet = client.open_by_key(SHEET_ID).sheet1
except Exception as e:
    print(f"Database Connection Error: {e}")

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
        
        # --- 1. DATA CLEANING ---
        user_name = str(data.get('name')).strip().title()
        user_contact = str(data.get('contact')).replace(" ", "").strip()
        user_pin = int(data.get('pincode'))
        user_role = str(data.get('role')).strip()
        user_help = str(data.get('helpType')).strip().title()

        all_records = sheet.get_all_records()

        # --- 2. UNIVERSAL DUPLICATE CHECK (For Both Roles) ---
        # Ye check karega ki kya same Contact + same Role pehle se exists karta hai
        is_duplicate = any(
            str(record.get('Contact')).replace(" ", "").strip() == user_contact and 
            str(record.get('Role')).strip() == user_role 
            for record in all_records
        )

        if not is_duplicate:
            # Agar naya data hai, toh append karo
            new_row = [user_name, user_help, user_contact, user_pin, user_role]
            sheet.append_row(new_row)
            # Nayi entry ke baad records refresh karein matching ke liye
            all_records = sheet.get_all_records()
            status_msg = "success"
        else:
            # Agar duplicate hai, toh sirf msg set karo, append_row mat karo
            status_msg = "already_existed"
        
        # --- 3. SMART MATCHING LOGIC ---
        matches = []
        seen_contacts = set() # Taaki results mein ek hi banda do baar na dikhe
        opposite_role = "Volunteer" if user_role == "User" else "User"
        
        for record in all_records:
            db_contact = str(record.get('Contact')).replace(" ", "").strip()
            db_role = str(record.get('Role')).strip()
            db_help = str(record.get('HelpType')).strip().title()

            # Conditions: Opposite Role + Same Help Type + Unique Contact in Results
            if db_role == opposite_role and db_help == user_help and db_contact not in seen_contacts:
                try:
                    db_pin = int(record.get('PinCode', 0))
                    distance = abs(user_pin - db_pin)
                    
                    record['distance'] = distance
                    matches.append(record)
                    seen_contacts.add(db_contact)
                except:
                    continue
        
        # Distance ke hisaab se sort karein (Sabse kareeb wala sabse upar)
        matches = sorted(matches, key=lambda x: x.get('distance', 9999))
        
        return jsonify({
            "status": "success", 
            "message": status_msg, 
            "matches": matches
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)})
        
# Vercel needs this to handle serverless execution
if __name__ == '__main__':
    app.run(debug=True)
