from bs4 import BeautifulSoup
import requests
import time
import json

def send_whatsapp_message(data_list):
    message = "JustLife\n"
    for entry in data_list:
        message += f"Reference: {entry['Reference']}\n"
        message += f"Type: {entry['Type']}\n"
        message += f"Region: {entry['Region']}\n"
        message += f"Zone: {entry['Zone']}\n"
        message += f"Start Date: {entry['StartDate']}\n"
        message += f"Duration: {entry['Duration']}\n"
        message += f"Number Of Professionals: {entry['NumberOfProfessionals']}\n"
        message += f"Material: {entry['Material']}\n"
        message += f"Booking Amount: {entry['BookingAmount']}\n"
        message += f"Payment Method: {entry['PaymentMethod']}\n"
        message += f"https://partner.justlife.com{entry['Link']}"

    url = "https://api.green-api.com/waInstance7103851613/sendMessage/2fa5ad1223a5476e84eac4b6e5c81b9d75f2ba058f7e4ec29b"
    payload = {
        "chatId": "120363151154658973@g.us",
        "message": message
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(response.text.encode('utf8'))

def extract_data_from_table(soup):
    table = soup.select_one('.table.table-bordered.table-striped.table-hover.sonata-ba-list')
    if not table:
        return None

    rows = table.select('tbody tr')
    if not rows:
        return None

    extracted_data = []

    for row in rows:
        cells = row.select('td')
        if cells:
            row_data = {
                'Reference': cells[0].get_text().strip(),
                'Link': cells[0].select_one('a')['href'] if cells[0].select_one('a') else None,
                'Type': cells[1].get_text().strip(),
                'Region': cells[2].get_text().strip(),
                'Zone': cells[3].get_text().strip(),
                'StartDate': cells[4].get_text().strip(),
                'Duration': cells[5].get_text().strip(),
                'NumberOfProfessionals': cells[6].get_text().strip(),
                'Material': cells[7].get_text().strip(),
                'BookingAmount': cells[8].get_text().strip(),
                'PaymentMethod': cells[9].get_text().strip()
            }
            extracted_data.append(row_data)

    return extracted_data

def is_logged_in(soup):
    return bool(soup.select_one('.login-box-msg') is None)

session = None  # Start with no session
no_data_counter = 0  # Initialize a counter for "No data found" cases
fetched_references = set()  # Initialize a set to store fetched "Reference" values

csrf_token = None  # Initialize csrf_token before the conditional check

while True:
    try:
        if session is None:
            session = requests.Session()

            pre_login_page = session.get('https://partner.justlife.com/login')
            soup = BeautifulSoup(pre_login_page.text, 'html.parser')
            csrf_token_element = soup.find('input', {'name': '_csrf_token'})
            if csrf_token_element:
             csrf_token = csrf_token_element.get('value')
            else:
             print("CSRF token element not found.")
             csrf_token = None  # Set csrf_token to None when not found

            payload = {
                '_username': 'gentzae',
                '_password': 'gentzae123',
                '_csrf_token': csrf_token
            }

            post = session.post('https://partner.justlife.com/login_check', data=payload)

            soup = BeautifulSoup(post.text, 'html.parser')
            if is_logged_in(soup):
                print("Login successful!")
            else:
                print("Login failed!")
                session = None
                continue
        r = session.get('https://partner.justlife.com/booking-request/list')
        soup = BeautifulSoup(r.text, 'html.parser')

        if not is_logged_in(soup):
            print("Session expired. Attempting to re-login.")
            session = None
            continue

        data = extract_data_from_table(soup)
        if data:
            new_entries = [entry for entry in data if entry['Reference'] not in fetched_references]

            if new_entries:
                print("\rNew data fetched successfully!", new_entries)

                # Send new data via WhatsApp
                send_whatsapp_message(new_entries)

                # Update fetched_references set
                for entry in new_entries:
                    fetched_references.add(entry['Reference'])

            no_data_counter = 0  # Reset the counter when data is found

        else:
            no_data_counter += 1  # Increment the counter
            print(f"\rNo data found ({no_data_counter})", end='', flush=True)

    except requests.exceptions.RequestException as e:
        print(f"\rAn error occurred: {e}", end='', flush=True)

    time.sleep(3)