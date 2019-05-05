import requests
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
from io import BytesIO
import json
from googlemaps import Client

HOST_NAME = 'localhost'
PORT_NUMBER = 9000

data_lst = []
counter = 0

def distance_computer(start_coordinates_1, end_coordinates_1, start_coordinates_2, end_coordinates_2, radius):
    radius = int(radius)
    key = "XXXXXXXXXX"
    units = "metric"
    url_ = "https://maps.googleapis.com/maps/api/distancematrix/json"
    r_1 = requests.get(url=url_, params={'units':units, 'origins':start_coordinates_1, 'destinations':start_coordinates_2, 'key':key})
    data_1 = r_1.json()
    distance_start = data_1['rows'][0]['elements'][0]['distance']['value']
    r_2 = requests.get(url= url_,params={'units':units,'origins':end_coordinates_1,'destinations':end_coordinates_2,'key':key})
    data_2 = r_2.json()
    distance_end = data_2['rows'][0]['elements'][0]['distance']['value']
    return distance_start < radius*1000 and distance_end < radius*1000

def coordinate_encoder(address):
    gmaps = Client(key="XXXXXXXXXX")
    coordinates = gmaps.geocode(address)[0]['geometry']['location']
    coords_lat = str(coordinates["lat"])
    coords_lng = str(coordinates["lng"])
    coords_total = coords_lat + "," + coords_lng
    return coords_total

def receive_data(user_data):
    global counter
    global data_lst
    possible = []
    for i in data_lst:
    	if distance_computer(coordinate_encoder(user_data[1]), coordinate_encoder(user_data[2]), coordinate_encoder(i["start"]), coordinate_encoder(i["dest"]), user_data[3]):
    		possible.append(i)
    data_lst.append({"id": counter, "name": user_data[0], "start": coordinate_encoder(user_data[1]), "dest": coordinate_encoder(user_data[2]), "radius": user_data[3]})
    counter += 1
    return possible

# SIMULATE ONLY

receive_data(["Dave", "43.7644024,-79.4134805", "43.6653396,-79.4005598", 5])
receive_data(["John", "43.768989, -79.408924", "43.6598228,-79.3892913", 5])
receive_data(["Tiffany", "43.688797, -79.347554", "43.6595444,-79.3832849", 5])
receive_data(["Kelsey", "43.664337, -79.433915", "43.6564131,-79.3880401", 5])

class MyHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def handle_http(self, status_code, path):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        content = '{"status": "GET"}'
        return bytes(content, 'UTF-8')

    def do_GET(self):
        response = self.handle_http(200, self.path)
        self.wfile.write(response)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body.decode("utf-8"))["content"]
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = BytesIO()
        temp = json.dumps({"content": receive_data(data)})
        response.write(bytes(temp, "utf-8"))
        print(data)
        print(type(data))
        self.wfile.write(response.getvalue())
    
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


if __name__ == '__main__':
    server_class = HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print(time.asctime(), 'Server Starts - %s:%s' % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), 'Server Stops - %s:%s' % (HOST_NAME, PORT_NUMBER))
