# customer_interface.py

from flask import Flask, render_template, request
from customer_actions import get_shard, search_items

app = Flask(__name__, template_folder="templates")

# Mock function to get store options (replace with actual implementation)
def get_store_options():
    return [(1, 'Figueroa'), (2, 'Jefferson')]  # Example store options

@app.route('/')
def index():
    store_options = get_store_options()
    return render_template('user_interface.html', store_options=store_options)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        item_name = request.form['item_name']
        store_code = int(request.form['store_code'])
        in_stock = int(request.form['in_stock'])
        price_min = float(request.form['price_min']) if request.form['price_min'] else None
        price_max = float(request.form['price_max']) if request.form['price_max'] else None
        sort = int(request.form['sort'])
        results = search_items(item_name, store_code, in_stock, price_min, price_max, sort)
        return render_template('search_results.html', results=results)
    else:
        return render_template('search_results.html', results=None)

if __name__ == "__main__":
    app.run(debug=True, port=8080)









