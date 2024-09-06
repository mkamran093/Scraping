from flask import Flask, request, render_template_string, session, redirect, url_for, Response
from igc_scraper import IGCScraper
from pwg_scraper import PWGScraper
from pilkington_scraper import PilkingtonScraper
from mygrant_scraper import MyGrantScraper
import undetected_chromedriver as uc
import logging
import psutil
import logging
import json

for proc in psutil.process_iter(['pid', 'name']):
        try:
            if 'chrome' in proc.info['name']:
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

webdriver_path = "undetected_chromedriver.exe"

options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--user-data-dir=C:\\Users\\NeXbit\\AppData\\Local\\Google\\Chrome\\User Data")
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--disable-gpu")  # Disable GPU acceleration  
driver = uc.Chrome(options=options)

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
    <script src="https://cdnjs.cloudflare.com/ajax/libs/htmx/1.9.10/htmx.min.js"></script>
</head>
<body>
    <h1>Part Information Scraper</h1>
    <form hx-post="/search" hx-target="#results">
        <label for="user_input">Enter part number:</label>
        <input type="text" id="user_input" name="user_input" required>
        <button type="submit">Search</button>
    </form>

    <div id="results">
        <div id="pwg-results"></div>
        <div id="igc-results"></div>
        <div id="pilkington-results"></div>
        <div id="mygrant-results"></div>
    </div>

    <script>
        htmx.on("htmx:afterSettle", function(event) {
            if (event.detail.target.id === "results") {
                var userInput = document.getElementById("user_input").value;
                var source = new EventSource("/stream-results?user_input=" + encodeURIComponent(userInput));
                source.onmessage = function(event) {
                    var data = JSON.parse(event.data);
                    document.getElementById(data.source + "-results").innerHTML = data.html;
                    if (data.source === "mygrant") {
                        source.close();
                    }
                };
            }
        });
    </script>
</body>
</html>
"""

def parse_pwg_data(data_string):
    parsed_data = []
    for item in data_string:
        part_name = item[0] if len(item) > 0 else "N/A"
        description = item[1] if len(item) > 1 else "N/A"
        availability = item[2] if len(item) > 2 else "N/A"
        location = item[3] if len(item) > 3 else "N/A"
        parsed_data.append({
            "part_name": part_name,
            "description": description,
            "availability": availability,
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

def generate_table_html(data, source):

    if source == 'pwg':
        return f"""
        <h2>PWG Data</h2>
        <form method="POST" action="/add-to-cart">
            <table>
                <tr>
                    <th>Part Number</th>
                    <th>Description</th>
                    <th>Availability</th>
                    <th>Location</th>
                    <th>Action</th>
                </tr>
                {"\n".join([f"""
                <tr>
                    <input type="hidden" name="part_number" value="{item.get('part_name', 'N/A')}">
                    <td>{item.get('part_name', 'N/A')}</td>
                    <td>{item.get('description', 'N/A')}</td>
                    <td>{item.get('availability', 'N/A')}</td>
                    <td>{item.get('location', 'N/A')}</td>
                    <td><button type="submit" class="add-to-cart-btn">Add to Cart</button></td>
                </tr>
                """ for item in data])}
            </table>
        </form>
        """
    if source == 'igc':
        return f"""
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
                    <td>{data.get('part_number', 'N/A')}</td>
                    <td>{data.get('price1', 'N/A')}</td>
                    <td>{data.get('in_stock', 'N/A')}</td>
                    <td>{data.get('location', 'N/A')}</td>
                    <td>
                        <input type="hidden" name="part_number" value="{data.get('part_number', 'N/A')}">
                        <button type="submit" class="add-to-cart-btn">Add to Cart</button>
                    </td>
                </tr>
            </table>
        </form>
        """
    if source == 'pilkington':
        return f"""
        <h2>Pilkington Data</h2>
        <form method="POST" action="/add-to-cart">
            <input type="hidden" name="part_number" value="{data.get('part_no', 'N/A')}">
            <table>
                <tr>
                    <th>Part Number</th>
                    <th>Part Name</th>
                    <th>Price</th>
                    <th>Location</th>
                    <th>Action</th>
                </tr>
                <tr>
                    <td>{data.get('part_no', 'N/A')}</td>
                    <td>{data.get('part_name', 'N/A')}</td>
                    <td>{data.get('price', 'N/A')}</td>
                    <td>{data.get('location', 'N/A')}</td>
                    <td><button type="submit" class="add-to-cart-btn">Add to Cart</button></td>
                </tr>
            </table>
        </form>
        """
    if source == 'mygrant':
        return f"""
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
                {"\n".join([f"""
                <tr>
                    <td>{item.get('location', 'N/A')}</td>
                    <td>{item.get('part_number', 'N/A')}</td>
                    <td>{item.get('price', 'N/A')}</td>
                    <td>{item.get('availability', 'N/A')}</td>
                    <td>
                        <input type="hidden" name="part_number" value="{item.get('part_number', 'N/A')}">
                        <button type="submit" class="add-to-cart-btn">Add to Cart</button>
                    </td>
                </tr>
                """ for item in data])}
            </table>
        </form>
        """

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/search', methods=['POST'])
def search():
    user_input = request.form['user_input']
    session['user_input'] = user_input
    return """
    <div id="pwg-results">Fetching PWG data...</div>
    <div id="igc-results">Fetching IGC data...</div>
    <div id="pilkington-results">Fetching Pilkington data...</div>
    <div id="mygrant-results">Fetching MyGrant data...</div>
    """

@app.route('/stream-results')
def stream_results():

    user_input = request.args.get('user_input')
    def generate():
        try:
            pwg_string = PWGScraper(user_input, driver, logger)
            pwg_data = parse_pwg_data(pwg_string)
            yield f"data: {json.dumps({'source': 'pwg', 'html': generate_table_html(pwg_data, 'pwg')})}\n\n"
        except Exception as e:
            logging.error(f"Error fetching PWG data: {e}")
            yield f"data: {json.dumps({'source': 'pwg', 'html': '<p>Error fetching PWG data</p>'})}\n\n"

        try:
            igc_data = IGCScraper(user_input, driver, logger)
            yield f"data: {json.dumps({'source': 'igc', 'html': generate_table_html(igc_data, 'igc')})}\n\n"
        except Exception as e:
            logging.error(f"Error fetching IGC data: {e}")
            yield f"data: {json.dumps({'source': 'igc', 'html': '<p>Error fetching IGC data</p>'})}\n\n"

        try:
            pilkington_string = PilkingtonScraper(user_input, driver, logger)
            pilkington_data = parse_pilkington_data(pilkington_string)
            yield f"data: {json.dumps({'source': 'pilkington', 'html': generate_table_html(pilkington_data, 'pilkington')})}\n\n"
        except Exception as e:
            logging.error(f"Error fetching Pilkington data: {e}")
            yield f"data: {json.dumps({'source': 'pilkington', 'html': '<p>Error fetching Pilkington data</p>'})}\n\n"

        try:
            mygrant_list = MyGrantScraper(user_input, driver, logger)
            mygrant_data = parse_mygrant_data(mygrant_list)
            yield f"data: {json.dumps({'source': 'mygrant', 'html': generate_table_html(mygrant_data, 'mygrant')})}\n\n"
        except Exception as e:
            logging.error(f"Error fetching MyGrant data: {e}")
            yield f"data: {json.dumps({'source': 'mygrant', 'html': '<p>Error fetching MyGrant data</p>'})}\n\n"

    return Response(generate(), content_type='text/event-stream')
    
@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    part_number = request.form['part_number']
    cart = session.get('cart', [])
    if part_number not in cart:
        cart.append(part_number)
    session['cart'] = cart
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
