from flask import Flask
from flask import render_template
import folium
from flask import request
import osmnx as ox
import pickle

from cars_interface import get_plot

app = Flask(__name__, template_folder='front')

@app.route('/')
@app.route('/index')
def index():
    address = request.args.get('address')
    fplot, best_improvement = get_plot(address)
    return render_template('index.html', title='Home', folium=fplot._repr_html_(), best_improvement=best_improvement * 100)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
