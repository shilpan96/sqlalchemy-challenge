import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Create engine using the `hawaii.sqlite` database file
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(engine,reflect=True)


# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################

app = Flask ( __name__)

#################################################
# Flask Routes
#################################################


@app.route("/")
def welcome():
    return (

        f"<h>Welcome to my Home Page</h><br>"
        f"<strong>Available Routes:</strong><br/>"
        f"<strong>1- </strong>/api/v1.0/precipitation<br/>"
        f"<strong>2- </strong>/api/v1.0/stations<br/>"
        f"<strong>3- </strong>/api/v1.0/tobs<br/>"
        f"<strong>4- </strong>/api/v1.0/<start>/<end>"

    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(Measurement.date, Measurement.prcp)\
              .filter(Measurement.date >=dt.date(2016,8,23)).all()

    session.close()

    # Create a dictionary from the results date as keys and prcp as values   
    prcp_dict = {}
    for date, prcp in results:
        prcp_dict[date] = prcp
    return jsonify(prcp_dict) 

@app.route("/api/v1.0/stations")
def stations():
    session= Session(engine)
    results = session.query(Station.station).all()

    session.close()
    return jsonify(results)

@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)
    active_stations = pd.DataFrame(session.query(Measurement.station,Measurement.prcp),\
        columns=['Station','Observation Counts']).groupby('Station').count()\
            .sort_values('Observation Counts', ascending = False)
    active_station = active_stations.index[0]
    results = session.query(Measurement.tobs).filter(Measurement.date >= dt.date(2016,8,23))\
             .filter(Measurement.station==active_station).all()
    session.close()
    return jsonify(results)


# create start route
@app.route("/api/v1.0/min_max_avg/<start>")
def start(start):
    # create session link
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date."""

    # take any date and convert to yyyy-mm-dd format for the query
    start_dt = dt.datetime.strptime(start, '%Y-%m-%D')

    # query data for the start date value
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_dt).all()

    session.close()

    # Create a list to hold results
    t_list = []
    for result in results:
        r = {}
        r["StartDate"] = start_dt
        r["TMIN"] = result[0]
        r["TAVG"] = result[1]
        r["TMAX"] = result[2]
        t_list.append(r)

    # jsonify the result
    return jsonify(t_list)

@app.route("/api/v1.0/min_max_avg/<start>/<end>")
def start_end(start, end):
    # create session link
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start and end dates."""

    # take start and end dates and convert to yyyy-mm-dd format for the query
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d')
    end_dt = dt.datetime.strptime(end, "%Y-%m-%d")

    # query data for the start date value
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_dt).filter(Measurement.date <= end_dt)

    session.close()

    # Create a list to hold results
    t_list = []
    for result in results:
        r = {}
        r["StartDate"] = start_dt
        r["EndDate"] = end_dt
        r["TMIN"] = result[0]
        r["TAVG"] = result[1]
        r["TMAX"] = result[2]
        t_list.append(r)

    # jsonify the result
    return jsonify(t_list)




if __name__ == '__main__':
    app.run(debug=False)