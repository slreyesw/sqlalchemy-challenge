# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station= Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
#Create Home route

@app.route("/")
def home():
     return (
        f"Available Routes:<br/>"
        f"/api/v1.0/percipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f'To search by a start date: <br/> Enter dates as YYYY-DD-MM after "/api/v1.0/" <br/> Example: /api/v1.0/2016-01-01<br/><br/>'
        f"To search by a start date and end date: <br/> Enter dates as YYYY-DD-MM after '/api/v1.0/' <br/> Example: /api/v1.0/2016-01-01/2016-01-02-01 <br/>")

#Create percipitation route
@app.route("/api/v1.0/percipitation")
def percipitation():
#create session 
   session = Session(engine)
#query the last year of data
   last_12_months = session.query(Measurement.date, Measurement.prcp).\
         filter(Measurement.date > "2016-08-22").\
         order_by(Measurement.date.desc()).all()

   session.close()
#store the data in a list and jsonify
   prcp_data = []
   for date, prcp in last_12_months:
         date_dict = {}
         date_dict[date] = prcp
         prcp_data.append(date_dict)
   return jsonify(prcp_data)

#create stations route
@app.route("/api/v1.0/stations")
def stations():
   session= Session(engine)
   #query the stations
   act_station = session.query(Measurement.station).\
      group_by(Measurement.station).\
      order_by(func.count(Measurement.station).desc()).all()

   session.close()
   station_names= list(np.ravel(act_station))
   return jsonify(station_names)
#create tobs route
@app.route("/api/v1.0/tobs")
def tobs():
   session = Session(engine)
#create query for the last year of most active station
   last_12_mo_act= session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date > "2016-08-22").\
    filter(Measurement.station == "USC00519281").all()
   
   session.close()
#store data in a list and jsonify
   tobs_data= []
   for x, tobs in last_12_mo_act:
      date_dict = {}
      date_dict[x] = tobs
      tobs_data.append(date_dict)
   
   tobs_temp= list(np.ravel(tobs_data))
   return jsonify(tobs_temp)

#create start date route
@app.route("/api/v1.0/<start>")
def start_date(start):
   session = Session(engine)
#create query for start dates
   start_functions = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
         filter(Measurement.date > start).\
         group_by(Measurement.date).all()   
   session.close()
#store start data in list and jsonify
   start_data = []
   for date, min, avg, max in start_functions:
         start_dict = {}
         start_dict["Date"] = date
         start_dict["TMIN"] = min
         start_dict["TAVG"] = avg
         start_dict["TMAX"] = max
         start_data.append(start_dict)

   return jsonify(start_data)

#create start and end route
@app.route("/api/v1.0/<start>/<end>")
def between(start, end):
   session = Session(engine)
#create query for dates in between start and end date
   between_functions = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
      filter(Measurement.date > start).\
      filter(Measurement.date < end).\
      group_by(Measurement.date).all()   
    
   session.close()
#store in a list and jsonify
   between_data = []
   for date, min, avg, max in between_functions:
               between_dict = {}
               between_dict["Date"] = date
               between_dict["TMIN"] = min
               between_dict["TAVG"] = avg
               between_dict["TMAX"] = max
               between_data.append(between_dict)

   return jsonify(between_data)

if __name__ == '__main__':
    app.run(debug=True)