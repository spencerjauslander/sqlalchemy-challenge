# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# '/' Page
# Start at the homepage. List all the available routes.
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/yyyy-mm-dd<br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

# '/api/v1.0/precipitation' Page
# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    recent_data = dt.datetime.strptime(recent_date[0], '%Y-%m-%d')
    query1 = dt.date(recent_data.year, recent_data.month, recent_data.day)
    query2 = dt.date(query1.year -1, query1.month, query1.day)
    sel1 = [measurement.date,measurement.prcp]
    query_result1 = session.query(*sel1).filter(measurement.date >= query2).all()
    session.close()

    last12months = []
    for date, prcp in query_result1:
        last12months_dict = {}
        last12months_dict["Date"] = date
        last12months_dict["Precipitation"] = prcp
        last12months.append(last12months_dict)

    return jsonify(last12months)

# '/api/v1.0/stations' Page
# Return a JSON list of stations from the dataset.
@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    sel2 = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    query_result2 = session.query(*sel2).all()
    session.close()

    stations = []
    for station,name,lat,lon,elevation in query_result2:
        stations_dict = {}
        stations_dict["Station"] = station
        stations_dict["Name"] = name
        stations_dict["Lat"] = lat
        stations_dict["Lon"] = lon
        stations_dict["Elevation"] = elevation
        stations.append(stations_dict)

    return jsonify(stations)

# '/api/v1.0/tobs' Page
# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.
@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    sel2 = [measurement.station,func.count(measurement.id)]
    mostactivestations = session.query(*sel2).\
    group_by(measurement.station).\
    order_by(func.count(measurement.id).desc()).all()
    sel3 = [measurement.date,measurement.tobs]
    queryresult = session.query(*sel3).filter(measurement.station == mostactivestations[0][0]).all()
    session.close()

    tobs1 = []
    for date, tobs in queryresult:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobs1.append(tobs_dict)

    return jsonify(tobs1)

# '/api/v1.0/<start>' Page
# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature 
# For a specified start
@app.route('/api/v1.0/<start>')
def get_t_start(start):
    session = Session(engine)
    queryresult = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()
    session.close()

    tobs2 = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs2.append(tobs_dict)

    return jsonify(tobs2)

# '/api/v1.0/<start>/<end>' Page
# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature 
# For a specified start-end range.
@app.route('/api/v1.0/<start>/<stop>')
def get_t_start_stop(start,stop):
    session = Session(engine)
    queryresult = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= stop).all()
    session.close()

    tobs3 = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs3.append(tobs_dict)

    return jsonify(tobs3)

if __name__ == '__main__':
    app.run(debug=True)