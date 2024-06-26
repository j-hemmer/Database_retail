from flask import Flask, render_template, request, jsonify
import geopandas as gpd
import folium
from folium import plugins
import mysql.connector
from folium.plugins import HeatMap
from shapely.geometry import Point
from admin_actions import *
from config import *

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/map')
def show_map():
    # REPLACE WITH YOUR PATH TO THE .SHP FILE
    # Also make sure all of the supporting files are present as well
    gdf = gpd.read_file('/Users/john/Spring2024/DSCI551/Retail_Database/states/cb_2018_us_state_500k.shp')

    # Create a map using Folium
    # gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()
    # Chose center of the contiguous US as the starting center
    map = folium.Map(location=[39.8283, -98.5795], zoom_start=5)

    # Add GeoPandas GeoDataFrame to the map and setup database connections
    folium.GeoJson(gdf).add_to(map)
    connection = connect_to_database(1)
    connection2 = connect_to_database(2)

    # Get points from both of the databases
    points = get_points_from_database(connection)
    points2 = get_points_from_database(connection2)

    all_points = points + points2
    gdf_points = gpd.GeoDataFrame(geometry=[Point(p[0], p[1]) for p in all_points], crs="EPSG:4326")
    # https://www.flexprojector.com/
    # Used flexprojector to get an appropriate coordinate system
    # Using Albers equal conic area
    # gdf_points = gdf_points.to_crs(9822)
    gdf_points['geometry'] = gdf_points['geometry'].buffer(0.05)
    gdf_points_json = gdf_points.to_json()
    folium.GeoJson(gdf_points_json).add_to(map)


    # Add points to the map as markers
    for point in points:
        # Point: [y coordinate, x coordinate, address, opening hours, closing hours, store code]
        # This is the order used in the sql expression used to retrieve the data
        # Create popup string
        popup_string = "Store code:\t"
        popup_string += str(point[5])
        popup_string += "\nAddress:\t"
        popup_string += str(point[2])
        popup_string += "\nOpening Hours:\t"
        popup_string += str(point[3])
        popup_string += "\nClosing Hours:\t"
        popup_string += str(point[4])
        folium.Marker(location=[point[1], point[0]],popup=popup_string, icon=folium.Icon(color='green')).add_to(map)
        # Create a buffer of radius 1000 around the icon
        # Not including because radius is in pixels
        # folium.CircleMarker([point[1], point[0]], radius=1000, color='green', fill=True, fill_color='green', fill_opacity=0.2).add_to(map)

    for point in points2:
        popup_string = "Store code:\t"
        popup_string += str(point[5])
        popup_string += "\nAddress:\t"
        popup_string += str(point[2])
        popup_string += "\nOpening Hours:\t"
        popup_string += str(point[3])
        popup_string += "\nClosing Hours:\t"
        popup_string += str(point[4])
        folium.Marker(location=[point[1], point[0]],popup=popup_string, icon = folium.Icon(color='red')).add_to(map)

    legend_html = '''
         <div style="position: fixed; 
                     bottom: 50px; left: 50px; width: 150px; height: 170px; 
                     border:2px solid grey; z-index:9999; font-size:14px;
                     ">&nbsp; Legend <br>
                       &nbsp; Stores from shard 1: &nbsp; <i class="fa fa-map-marker fa-2x" style="color:green"></i><br>
                       &nbsp; Stores from shard 2: &nbsp; <i class="fa fa-map-marker fa-2x" style="color:red"></i><br>
                       &nbsp; Buffer: &nbsp; <svg height="20" width="20"><circle cx="10" cy="10" r="10" fill="rgb(0, 144, 255)" /></svg>
          </div>
         '''
    map.get_root().html.add_child(folium.Element(legend_html))


    # Save the map to an HTML file
    map.save('templates/map.html')

    connection.close()
    # Render the map HTML template
    return render_template('map.html')

@app.route('/delete_store', methods=['GET', 'POST'])
def delete_store():
    if request.method == 'POST':
        # Get form data
        store_code = request.form['store_code']

        # Delete store information from the database
        remove_store(store_code)

        return render_template('index.html')
    else:
        return render_template('delete_store_page.html')

@app.route('/insert_store', methods=['GET', 'POST'])
def insert_store():
    if request.method == 'POST':
        # Get form data
        store_code = request.form['store_code']
        address = request.form['address']
        opening_time = request.form['opening_time']
        closing_time = request.form['closing_time']
        x_coord = request.form['x']
        y_coord = request.form['y']
        # Insert store information into the database
        insert_new_store(store_code, address, opening_time, closing_time, x_coord, y_coord)


        return render_template('index.html')
    else:
        return render_template('insert_store.html')

@app.route('/insert_inventory', methods=['GET', 'POST'])
def insert_inventory():
    if request.method == 'POST':
        # Get form data 
        item_code = request.form['item_code']
        store_code = request.form['store_code']
        item_name = request.form['item_name']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        # Insert store information into the database
        print(type(request.form['item_code']))
        print(type(request.form['store_code']))
        print(type(request.form['item_name']))
        print(type(request.form['quantity']))
        print(type(request.form['price']))
        stock_new_item(request.form['item_code'], request.form['store_code'], request.form['item_name'], int(request.form['quantity']), float(request.form['price']))


        return render_template('insert_inventory.html')
    else:
        return render_template('insert_inventory.html')

@app.route('/update_hours', methods=['GET', 'POST'])
def update_hours():
    if request.method == 'POST':
        # Get form data
        store_id = request.form['store_id']
        opening_hours = request.form['opening_hours']
        closing_hours = request.form['closing_hours']

        # Update store hours in the database
        success = update_store_hours(store_id, opening_hours, closing_hours)

        if success:
            # Redirect to index page
            return render_template('index.html')
        else:
            # Display error message if the store code doesn't exist
            return render_template('error.html', message='Store code does not exist')
    else:
        return render_template('update_hours.html')

@app.route('/fetch_data', methods=['GET', 'POST'])
def fetch_data():
    if request.method == 'POST':
        store_id = request.form['store_id']
        result = fetch_store_data(store_id)
        if result:
            column_names = [col[0] for col in result]
            data_text = f"Data fetched successfully for Store ID: {store_id}\nColumns: "
            count = 0
            for column in column_names:
                if count < 4:
                    count += 1
                    continue
                data_text += str(column) + " "
            data_text += "\n"
            for data in result[0]:
                data_text += str(data) + " "
            return render_template('fetch_data_result.html', data_text=data_text)
        else:
            return render_template('fetch_data_result.html', data_text=f"Nothing found for store ID: {store_id}")
    else:
        return render_template('fetch_data.html')

def home():
    return render_template('index.html')

@app.route('/view_items', methods=['GET', 'POST'])
def view_items_route():
    store_codes = get_all_stores()
    print(store_codes)
    if request.method == 'POST':
        # Render the view_items page
        store_code = request.form['store_code']
        shard_data = get_shard(store_code)
        shard_creds = shard_connections[shard_data]
        connection_via_shard = mysql.connector.connect(**shard_creds)
        connection_cursor = connection_via_shard.cursor()
        mini_query = "SELECT item_name, item_code, store_code, quantity FROM Vendor"
        connection_cursor.execute(mini_query)
        data = connection_cursor.fetchall()
        output = [[i[0], i[1], i[2], i[3]] for i in data]
        return render_template('view_items.html', store_codes=store_codes, data = output)
    else:
        return render_template('view_items.html', store_codes=store_codes)

@app.route('/filter_items', methods=['GET', 'POST'])
def filter_items():
    # Retrieve form data
    store_id = request.form.get('store_id')
    item_code = request.form.get('itemCode')
    item_name = request.form.get('itemName')

    # Call the view_items function passing the retrieved data
    items = view_items(store_id, item_code, item_name)

    # Render the view_items template with the filtered items
    return render_template('items_table.html', items=items)

@app.route('/restock_item', methods=['GET', 'POST'])
def restock_item_route():
    if request.method == 'POST':
        item_code = request.form['item_code']
        store_code = request.form['store_code']
        quantity = int(request.form['quantity'])

    # Call the restock_item function with the provided parameters
        restock_item(item_code, store_code, quantity)
        return render_template('restock_item.html')
    else:
        return render_template('restock_item.html')




@app.route('/price_change', methods=['GET', 'POST'])
def price_change_route():
    if request.method == 'POST':
        item_code = request.form['item_code']
        store_code = request.form['store_code']
        price = request.form['price']

        # Call the price_change function with the provided parameters
        price_change(item_code, store_code, price)

        return render_template('price_change.html')
    else:
        return render_template('price_change.html')

@app.route('/remove_item', methods=['GET' , 'POST'])
def remove_item_route():
    if request.method == 'POST':
        item_code = request.form['item_code']
        store_code = request.form['store_code']

        # Call the price_change function with the provided parameters
        remove_item(item_code, store_code)

        return render_template('remove_item.html')
    else:
        return render_template('remove_item.html')


# Define other routes similarly
if __name__ == '__main__':
    app.run(debug=True, port=5001)
