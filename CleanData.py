import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Aapki Sheet ID
SHEET_ID = "11k63x80AQ9mkUjpyHe1QXqum4mreNGOfWwCA7gjysao"
sheet = client.open_by_key(SHEET_ID).sheet1

def clean_smart_duplicates():
    try:
        # Saara data fetch karein
        data = sheet.get_all_records()
        if not data:
            print("Sheet khali hai!")
            return

        unique_records = {}
        
        # Logic: Contact + HelpType ka unique set banana
        for record in data:
            contact = str(record.get('Contact')).strip()
            help_type = str(record.get('HelpType')).strip()
            
            # Key banaiye dono ko combine karke
            # Example: "9876543210-Food"
            unique_key = f"{contact}-{help_type}"
            
            # Latest entry ko save karein
            unique_records[unique_key] = record

        # Headers nikaalein
        headers = list(data[0].keys())
        clean_rows = [headers]
        
        for key in unique_records:
            row = [unique_records[key].get(h) for h in headers]
            clean_rows.append(row)

        # Sheet update karein
        sheet.clear()
        sheet.update('A1', clean_rows)
        
        print(f"Cleaned! Kept {len(clean_rows)-1} unique help requests.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    clean_smart_duplicates()