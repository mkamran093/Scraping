from flask import Flask, request, render_template_string, session, redirect, url_for
from igc_scraper import IGCScraper
from pwg_scraper import PWGScraper
from pilkington_scraper import PilkingtonScraper
from mygrant_scraper import MyGrantScraper

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
        .add-to-cart-btn {
            padding: 5px 10px;
            background-color: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
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
    <form method="POST" action="/add-to-cart">
        <input type="hidden" name="part_number" value="{{ pwg_data.get('part_details', 'N/A') }}">
        <table>
            <tr>
                <th>Part Number</th>
                <th>Availability</th>
                <th>Location</th>
                <th>Action</th>
            </tr>
            <tr>
                <td>{{ pwg_data.get('part_details', 'N/A') }}</td>
                <td>{{ pwg_data.get('ref_qty', 'N/A') }}</td>
                <td>{{ pwg_data.get('location', 'N/A') }}</td>
                <td><button type="submit" class="add-to-cart-btn">Add to Cart</button></td>
            </tr>
        </table>
    </form>
    {% else %}
    {% if request.method == 'POST' %}
    <h2>PWG Data</h2>
    <p>Data not found on PWG website.</p>
    {% endif %}
    {% endif %}

    {% if igc_data %}
    <h2>IGC Data</h2>
    <form method="POST" action="/add-to-cart">
        <table>
            <tr>
                <th>Part Number</th>
                <th>Price 1</th>
                <th>In Stock</th>
                <th>Location</th>
                <th>Action</th>
            </tr>
            <tr>
                <td>{{ igc_data.part_number }}</td>
                <td>{{ igc_data.price1 }}</td>
                <td>{{ igc_data.in_stock }}</td>
                <td>{{ igc_data.location }}</td>
                <td>
                    <input type="hidden" name="part_number" value="{{ item.part_number }}">
                    <button type="submit" class="add-to-cart-btn">Add to Cart</button>
                </td>
            </tr>
        </table>
    </form>
    {% else %}
    {% if request.method == 'POST' %}
    <h2>IGC Data</h2>
    <p>Data not found on IGC website.</p>
    {% endif %}
    {% endif %}

    {% if pilkington_data %}
    <h2>Pilkington Data</h2>
    <form method="POST" action="/add-to-cart">
        <input type="hidden" name="part_number" value="{{ pilkington_data.get('part_no', 'N/A') }}">
        <table>
            <tr>
                <th>Part Number</th>
                <th>Part Name</th>
                <th>Price</th>
                <th>Location</th>
                <th>Action</th>
            </tr>
            <tr>
                <td>{{ pilkington_data.get('part_no', 'N/A') }}</td>
                <td>{{ pilkington_data.get('part_name', 'N/A') }}</td>
                <td>{{ pilkington_data.get('price', 'N/A') }}</td>
                <td>{{ pilkington_data.get('location', 'N/A') }}</td>
                <td><button type="submit" class="add-to-cart-btn">Add to Cart</button></td>
            </tr>
        </table>
    </form>
    {% else %}
    {% if request.method == 'POST' %}
    <h2>Pilkington Data</h2>
    <p>Data not found on Pilkington website.</p>
    {% endif %}
    {% endif %}

    {% if mygrant_data %}
    <h2>MyGrant Data</h2>
    <form method="POST" action="/add-to-cart">
        <table>
            <tr>
                <th>Location</th>
                <th>Part Number</th>
                <th>Price</th>
                <th>Availability</th>
                <th>Action</th>
            </tr>
            {% for item in mygrant_data %}
            <tr>
                <td>{{ item.location }}</td>
                <td>{{ item.part_number }}</td>
                <td>{{ item.price }}</td>
                <td>{{ item.availability }}</td>
                <td>
                    <input type="hidden" name="part_number" value="{{ item.part_number }}">
                    <button type="submit" class="add-to-cart-btn">Add to Cart</button>
                </td>
            </tr>
            {% endfor %}
        </table>
    </form>
    {% else %}
    {% if request.method == 'POST' %}
    <h2>MyGrant Data</h2>
    <p>Data not found on MyGrant website.</p>
    {% endif %}
    {% endif %}
</body>
</html>
"""

def parse_pwg_data(data_string):
    lines = data_string.split("\n")
    ref_qty = lines[0].split(": ")[1] if len(lines) > 0 else "N/A"
    part_details = lines[1].split(": ")[1] if len(lines) > 1 else "N/A"
    location = lines[2].split(":: ")[1] if len(lines) > 2 else "N/A"
    return {
        "ref_qty": ref_qty,
        "part_details": part_details,
        "location": location
    }


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

def parse_mygrant_data(data_list):
    parsed_data = []
    for item in data_list:
        location = item[0] if len(item) > 0 else "N/A"
        availability = item[1] if len(item) > 1 else "N/A"
        part_number = item[2] if len(item) > 2 else "N/A"
        price = item[3] if len(item) > 3 else "N/A"
        parsed_data.append({
            "location": location,
            "part_number": part_number,
            "price": price,
            "availability": availability
        })
    return parsed_data

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/', methods=['GET', 'POST'])
def index():
    pwg_data = igc_data = pilkington_data = mygrant_data = None
    if request.method == 'POST':
        if 'part_number' in request.form:
            part_number = request.form['part_number']
            # Add part_number to session cart
            cart = session.get('cart', [])
            if part_number not in cart:
                cart.append(part_number)
            session['cart'] = cart
            return redirect(url_for('index'))
        
        user_input = request.form['user_input']

        # Call the scrapers with the user input
        try:
            pwg_string = PWGScraper(user_input)
            pwg_data = parse_pwg_data(pwg_string)
        except:
            pwg_data = None
        
        try:
            igc_data = IGCScraper(user_input)
        except:
            igc_data = None

        try:
            pilkington_string = PilkingtonScraper(user_input)
            pilkington_data = parse_pilkington_data(pilkington_string)
        except:
            pilkington_data = None

        try:
            mygrant_list = MyGrantScraper(user_input)
            mygrant_data = parse_mygrant_data(mygrant_list)
        except:
            mygrant_data = None

    return render_template_string(HTML_TEMPLATE, pwg_data=pwg_data, igc_data=igc_data, pilkington_data=pilkington_data, mygrant_data=mygrant_data)

if __name__ == '__main__':
    app.run(debug=True)