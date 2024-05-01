from flask import Flask, render_template, request, jsonify
import geopandas as gpd
import folium
from folium import plugins
import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'dsci551'
}

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/map')
def show_map():
    # REPLACE WITH YOUR PATH TO THE .SHP FILE
    # Also make sure all of the supporting files are present as well
    gdf = gpd.read_file('/Users/john/Spring2024/DSCI551/Retail_Database/shapefile_of_us/cb_2018_us_nation_5m.shp')

    # Create a map using Folium
    map = folium.Map(location=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()], zoom_start=5)

    # Add GeoPandas GeoDataFrame to the map and setup database connections
    folium.GeoJson(gdf).add_to(map)
    connection = connect_to_database(1)
    connection2 = connect_to_database(2)

    # Get points from both of the databases
    points = get_points_from_database(connection)
    points2 = get_points_from_database(connection2)

    # Add points to the map as markers
    for point in points:
        # Point: [y coordinate, x coordinate, address]
        # Create popup string
        popup_string = "Address:\t"
        popup_string += str(point[2])
        popup_string += "\nOpening Hours:\t"
        popup_string += str(point[3])
        popup_string += "\nClosing Hours:\t"
        popup_string += str(point[4])
        folium.Marker(location=[point[1], point[0]],popup=popup_string, icon=folium.Icon(color='green')).add_to(map)
    
    for point in points2:
        folium.Marker(location=[point[1], point[0]], icon = folium.Icon(color='red')).add_to(map)
    
    legend_html = '''
         <div style="position: fixed; 
                     bottom: 50px; left: 50px; width: 150px; height: 90px; 
                     border:2px solid grey; z-index:9999; font-size:14px;
                     ">&nbsp; Legend <br>
                       &nbsp; Stores from shard 1 &nbsp; <i class="fa fa-map-marker fa-2x" style="color:green"></i><br>
                       &nbsp; Stores from shard 2 &nbsp; <i class="fa fa-map-marker fa-2x" style="color:red"></i>
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
        delete_store_info(store_code)
        
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
        insert_store_info(store_code, address, opening_time, closing_time, x_coord, y_coord)
        

        return render_template('index.html')
    else:
        return render_template('insert_store.html')
    
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
            # Redirect to index page or any other page as needed
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



# BACKEND
def get_shard(store_code):
    # Assuming number of shards is equal to the length of shard_connections
    # Store code needs to be an integer
    # Num shards is 2 I believe
    # just going to use 2
    # num_shards = len(shard_connections)
    return (int(store_code) % 2)+ 1

def home():
    return render_template('index.html')

def insert_store():
    if request.method == 'POST':
        # Handle form submission here
        pass
    else:
        return render_template('insert_store.html')
    
def get_points_from_database(connection):
    # Query the database to get x and y coordinates of the points from out stores
    cursor = connection.cursor()
    cursor.execute("SELECT x, y, address, opening_time, closing_time FROM Stores")
    points = cursor.fetchall()
    cursor.close()
    return points

def connect_to_database(shard):
    try:
        # Modify this function based on the shard configuration
        mydb = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=f"shard{shard}_db"
        )
        return mydb
    except mysql.connector.Error as err:
        # Handle connection error
        raise Exception(f"Error connecting to MySQL database: {err}")

def insert_store_info(store_code, address, opening_time, closing_time, x, y):
    # Get shard based on store code
    shard = get_shard(store_code)

    # Connect to the database depending on our shard and create cursor
    mydb = connect_to_database(shard)
    cursor = mydb.cursor()

    # Insert the values into the database
    if float(y) < 25 or float(y) > 85:
        x = None
        y = None
    if float(x) < -120 or float(x) > -70:
        y = None
        x = None

    sql = "INSERT INTO Stores (store_code, address, opening_time, closing_time, x, y) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (store_code, address, opening_time, closing_time, x, y)
    cursor.execute(sql, val)
    
    # Commit and close everything
    mydb.commit()
    cursor.close()
    mydb.close()

def update_store_hours(store_id, opening_hours, closing_hours):
    # Based on an existing store, you can update the stores opening and closing hours
    # Reloads if the store does not exist
    shard = get_shard(store_id)  
    mydb = connect_to_database(shard)
    cursor = mydb.cursor()
    sql = "UPDATE Stores SET opening_time = %s, closing_time = %s WHERE store_code = %s"
    val = (opening_hours, closing_hours, store_id) 
    cursor.execute(sql, val)
    if cursor.rowcount == 0:
        # If no rows were affected, it means the store code doesn't exist
        cursor.close()
        mydb.close()
        return False
    else:
        mydb.commit()
        cursor.close()
        mydb.close()
        return True

def fetch_store_data(store_id):
    # Getting the store data from a certain store ID
    # Reloads if the store ID does not exist
    shard = get_shard(store_id) 
    mydb = connect_to_database(shard)
    cursor = mydb.cursor()
    sql = "SELECT * FROM Stores WHERE store_code = %s"
    val = (store_id,)
    cursor.execute(sql, val)
    result = cursor.fetchall()
    cursor.close()
    mydb.close()
    return result


def delete_store_info(store_code):
    try:
        # Get shard based on store code
        shard = get_shard(store_code)

        # Connect to the database depending on our shard and create cursor
        mydb = connect_to_database(shard)
        cursor = mydb.cursor()

        # Delete the row from the database
        sql = "DELETE FROM Stores WHERE store_code = %s"
        val = (store_code,)
        cursor.execute(sql, val)

        # Commit and close everything
        mydb.commit()
        cursor.close()

        return True, "Store information deleted successfully!"
    except mysql.connector.Error as err:
        return False, f"Error deleting store information from MySQL database: {err}"



# Define other routes similarly
if __name__ == '__main__':
    app.run(debug=True, port=5001)
