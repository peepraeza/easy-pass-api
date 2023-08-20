from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/easy-pass/details', methods=['POST'])
def scrape_data():
    email = request.json.get('email')
    password = request.json.get('password')
    key_mappings = {
        'หมายเลข OBU': 'idTag',
        'ชื่อบัตร': 'cardName',
        'จำนวนเงิน': 'balance',
        'เลขสมาร์ทการ์ด (S/N)': 'smartCardNo',
        'ทะเบียนรถ': 'licensePlate',
    }
    
    s = requests.Session()

    url = "https://www.thaieasypass.com/en/member/signin"

    payload = f'email={email}&password={password}'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = s.post(url, headers=headers, data=payload)

    if response.status_code != 200:
        return jsonify({"error": "data not found."}), 400


    soup = BeautifulSoup(response.text, 'html.parser')

     # Check if "head-table" class exists
    head_table = soup.find_all(class_="head-table")
    if not head_table:
        return jsonify({"error": "data not found."}), 400


    # Extract headers with class "head-table"
    original_headers  = [header.get_text().strip() for header in head_table[0].find_all("td")]

    # Map headers to their English counterparts only if they exist in key_mappings
    headers = [key_mappings.get(header) for header in original_headers if header in key_mappings]

    # Extract data corresponding to each header
    data_list = []
    for table_row in soup.find_all(class_="head-table")[0].find_next_siblings("tr"):
        row_data = [td.get_text().strip() for header, td in zip(original_headers, table_row.find_all("td")) if header in key_mappings]
        if len(row_data) == len(headers):  # Ensure the row has the same number of columns as headers
            data_list.append(dict(zip(headers, row_data)))

    return jsonify(data_list)

@app.route('/', methods=['GET'])
def get():
    return "Hello, World"

if __name__ == '__main__':
    app.run(debug=True)