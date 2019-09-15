from flask import Flask
from flask import render_template
import folium
from flask import request
import osmnx as ox
import pickle

app = Flask(__name__, template_folder='front')

@app.route('/')
@app.route('/index')
def index():

    address = request.args.get('address')
    print(address)
    start_coords = (46.9540700, 142.7360300)
    # G = ox.graph_from_place(address, network_type='drive')

    G = pickle.load(open('harbor.pkl', 'rb'))
    graph_map = ox.plot_graph_folium(G, edge_width=2)
    # print('hi2')
    return render_template('index.html', title='Home', folium=graph_map._repr_html_())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)