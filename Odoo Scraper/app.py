from flask import Flask, request, render_template_string
from igc_scraper import IGCScraper
from pwg_scraper import PWGScraper
from pilkington_scraper import PilkingtonScraper

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Part Information Scraper</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <h1>Part Information Scraper</h1>
    <form method="POST">
        <label for="user_input">Enter part number:</label>
        <input type="text" id="user_input" name="user_input" required>
        <button type="submit">Search</button>
    </form>
    {% if pwg_data %}
    <h2>PWG Data</h2>
    <table>
        <tr>
            <th>Part Number</th>
            <th>Available Quantity</th>
            <th>Location</th>
        </tr>
        <tr>
            <td>{{ pwg_data.get('part_details', 'N/A') }}</td>
            <td>{{ pwg_data.get('ref_qty', 'N/A') }}</td>
            <td>{{ pwg_data.get('location', 'N/A') }}</td>
        </tr>
    </table>
    {% endif %}
    {% if igc_data %}
    <h2>IGC Data</h2>
    <table>
        <tr>
            <th>Part Number</th>
            <th>Price 1</th>
            <th>In Stock</th>
            <th>Location</th>
        </tr>
        {% for item in igc_data %}
        <tr>
            <td>{{ item.part_number }}</td>
            <td>{{ item.price1 }}</td>
            <td>{{ item.in_stock }}</td>
            <td>{{ item.location }}</td>
        </tr>
        {% endfor %}
    </table>
{% endif %}

    {% if pilkington_data %}
    <h2>Pilkington Data</h2>
    <table>
        <tr>
            <th>Part Number</th>
            <th>Part Name</th>
            <th>Price</th>
            <th>Location</th>
        </tr>
        <tr>
            <td>{{ pilkington_data.get('part_no', 'N/A') }}</td>
            <td>{{ pilkington_data.get('part_name', 'N/A') }}</td>
            <td>{{ pilkington_data.get('price', 'N/A') }}</td>
            <td>{{ pilkington_data.get('location', 'N/A') }}</td>
        </tr>
    </table>
    {% endif %}
</body>
</html>
"""

def parse_pwg_data(data_string):
    lines = data_string.split("\n")
    ref_qty = lines[0].split(": ")[1] if len(lines) > 0 else "N/A"
    part_details = lines[1] if len(lines) > 1 else "N/A"
    location = lines[2].split(":: ")[1] if len(lines) > 2 else "N/A"
    return {
        "ref_qty": ref_qty,
        "part_details": part_details,
        "location": location
    }

def parse_igc_data(data_list):
    parsed_data = []
    for item in data_list:
        part_number = item[0] if len(item) > 0 else "N/A"
        price1 = item[1] if len(item) > 1 else "N/A"
        in_stock = item[2] if len(item) > 2 else "N/A"
        location = item[3] if len(item) > 3 else "N/A"
        parsed_data.append({
            "part_number": part_number,
            "price1": price1,
            "in_stock": in_stock,
            "location": location
        })
    return parsed_data


def parse_pilkington_data(data_string):
    lines = data_string.split("\n")
    part_no = lines[0].split(": ")[1] if len(lines) > 0 else "N/A"
    part_name = lines[1].split(": ")[1] if len(lines) > 1 else "N/A"
    price = lines[2].split(": ")[1] if len(lines) > 2 else "N/A"
    location = lines[3].split(": ")[1] if len(lines) > 3 else "N/A"
    return {
        "part_no": part_no,
        "part_name": part_name,
        "price": price,
        "location": location
    }

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/', methods=['GET', 'POST'])
def index():
    pwg_data = igc_data = pilkington_data = None
    if request.method == 'POST':
        user_input = request.form['user_input']
        
        # Call the scrapers with the user input
        pwg_string = PWGScraper(user_input)
        igc_list = IGCScraper(user_input)
        pilkington_string = PilkingtonScraper(user_input)

        if pwg_string:
            pwg_data = parse_pwg_data(pwg_string)
        if igc_list:
            igc_data = parse_igc_data(igc_list)
        if pilkington_string:
            pilkington_data = parse_pilkington_data(pilkington_string)


    return render_template_string(HTML_TEMPLATE, pwg_data=pwg_data, igc_data=igc_data, pilkington_data=pilkington_data)

if __name__ == '__main__':
    app.run(debug=True)