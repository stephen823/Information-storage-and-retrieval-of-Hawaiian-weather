import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import os
cwd = os.getcwd()
print("My current working directory is: {} ".format(cwd))
os.chdir("/Users/apple/Desktop/bootcamp/9-Advanced-Data-Storage-and-Retrieval/sqlalchemy-challenge")
cwd = os.getcwd()
print("My current working directory is: {} ".format(cwd))
################################################## 
#Database Setup
##################################################

engine = create_engine("sqlite:///hawaii.sqlite")


#reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

cwd = os.getcwd()
print("My current working directory is: {} ".format(cwd))

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station



# Flask Setup
#################################################
app = Flask(__name__)




@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
#Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
def precipitation():
    #Start Session
    session=Session(engine)

    #Query result
    last_twelve=session.query(Measurement.date,func.avg(Measurement.prcp)).\
    filter(Measurement.date>='2016-08-23').\
    group_by(Measurement.date).\
    order_by(Measurement.date).all()
    session.close()
    #Define Dictionary
    precipitation_dict={}
    for i in range(len(last_twelve)):
        precipitation_dict[last_twelve[i][0]]=last_twelve[i][1]
    #Return the JSON representation of your dictionary.
    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
    #Query result
    session=Session(engine)
    observation_counts=session.query(Measurement.station,func.count(Measurement.id)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.id).desc()).all()
    session.close()
    #Create list of Stations
    station_list=[]
    for i in range(len(observation_counts)):
        station_list.append(observation_counts[i][0])


    #Return a JSON list of stations from the dataset
    return jsonify(station_list)



@app.route("/api/v1.0/tobs")
#Query the dates and temperature observations of the most active station for the last year of data.
  
#Return a JSON list of temperature observations (TOBS) for the previous year.
def tobs():
    #Query the dates and temperature observations of the most active station for the last year of data.
    session=Session(engine)
    Station_list=session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    MA_station=Station_list[0][0]

    MA_station_data=session.query(Measurement.date,Measurement.tobs).\
    filter(Measurement.date>='2016-08-23').\
    filter(Measurement.station==MA_station).all()
    session.close()

    #Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(MA_station_data)



@app.route("/api/v1.0/<start>")
def start(start):
    #When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
    session=Session(engine)
    TMIN_TAVG_TMAX=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()
    return jsonify(TMIN_TAVG_TMAX)



@app.route("/api/v1.0/<start>/<end>")
#When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
def calc_temps(start, end):
    session=Session(engine)
    TMIN_TAVG_TMAX_se=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    return jsonify(TMIN_TAVG_TMAX_se)


if __name__ == "__main__":
    app.run(debug=True)
