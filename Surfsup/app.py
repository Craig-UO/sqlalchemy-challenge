# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def homepage():
    """List all available api routes."""
    return (
        f"Dates should be in the format YYYY-MM-DD<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start date<br/>"
        f"/api/v1.0/start date/end date<br/>"
    )


@app.route("/api/v1.0/precipitation")
def year_precip():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Gathering the most recent 12 months of data"""
    # Find the most recent date in the data set.

    # Import this descending function so the dates can be ordered starting with the most recent
    from sqlalchemy import desc

    # Query to order the dates descending and grab the first entry, which is the most recent
    most_recent_date = session.query(Measurement).order_by(Measurement.date.desc()).first()

    # Calculate the date one year from the last date in data set.
    # Convert date string to timestamp
    recent_date_str = dt.datetime.strptime(most_recent_date.date, '%Y-%m-%d')

    # Use the datetime utility to subtract one year from this date
    year_ago_date = recent_date_str - dt.timedelta(days = 365)

    # Convert the date from one year ago to a string to match those in the data set
    year_ago_date_string = year_ago_date.strftime('%Y-%m-%d')

    # Perform a query to retrieve the date and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago_date_string).all()

    session.close()

    # Create a dictionary from the row data and append to a list of precipitation for the year by dates
    year_precip = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        year_precip.append(prcp_dict)

    return jsonify(year_precip)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Gathering the most recent 12 months of data"""
    # Find the most recent date in the data set.

    # Import this descending function so the dates can be ordered starting with the most recent
    from sqlalchemy import desc

    # Query to retrieve all the stations
    stations = session.query(Station.station, Station.name).order_by(Station.station.asc()).all()

    session.close()

    # Create a dictionary from the row data and append to a list of precipitation for the year by dates
    station_list = []
    for station, name in stations:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_list.append(station_dict)

    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Gathering the most recent 12 months of data for the most active station - USC00519281 in Waihee"""

    # Set the ID for the most active station
    active_station = 'USC00519281'
    
    # Determine the most recent data for this station
    most_recent = session.query(Measurement).filter(Measurement.station == active_station).order_by(Measurement.date.desc()).first()
    
    # Import this descending function so the dates can be ordered starting with the most recent
    from sqlalchemy import desc

    # Convert date string to timestamp
    most_recent_str = dt.datetime.strptime(most_recent.date, '%Y-%m-%d')

    # Use the datetime utility to subtract one year from this date
    year_ago = most_recent_str - dt.timedelta(days = 365)

    # Convert the date from one year ago to a string to match those in the data set
    year_ago_str = year_ago.strftime('%Y-%m-%d')

    # Perform a query to retrieve 12 months of tobs (temperature observations)
    year_temps = (session.query(Measurement.tobs, Measurement.date).filter(Measurement.date >= year_ago_str)
              .filter(Measurement.station == active_station).all())
    
    session.close()

    # Create a dictionary from the row data and append to a list of precipitation for the year by dates
    tobs_list = []
    for tobs, date in year_temps:
        tobs_dict = {}
        tobs_dict["tobs"] = tobs
        tobs_dict["date"] = date
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


@app.route("/api/v1.0/<start_date>")
def from_date(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Gathering minimum temperature, average temperature, and maximum temperature for the specified start date"""
    
    # Query to retrieve the values
    
    tobs_results = (session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))
                    .filter(Measurement.date >= start_date).all())

    session.close()

    # Create a list from the results
    tobs_stats = []
    for min, avg, max in tobs_results:
        tobs_stats_dict = {}
        tobs_stats_dict["Minimum Temperature"] = min
        tobs_stats_dict["Average Temperature"] = avg
        tobs_stats_dict["Maximum Temperature"] = max
        tobs_stats.append(tobs_stats_dict)

    return jsonify(tobs_stats)


@app.route("/api/v1.0/<start_date>/<end_date>")
def tobs_period(start_date, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Gathering minimum temperature, average temperature, and maximum temperature for the specified date range"""

    # Check that the end date is not before the start date and inform the user if so
    if start_date <= end_date:
        # Query to retrieve the values
    
        tobs_period_results = (session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))
                        .filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all())

        session.close()

        # Create a list from the results
        tobs_stats_period = []
        for min, avg, max in tobs_period_results:
            tobs_stats_period_dict = {}
            tobs_stats_period_dict["Minimum Temperature"] = min
            tobs_stats_period_dict["Average Temperature"] = avg
            tobs_stats_period_dict["Maximum Temperature"] = max
            tobs_stats_period.append(tobs_stats_period_dict)

        return jsonify(tobs_stats_period)
    
    else:
        return("The end date must not be before the start date, and dates must be given as yyyy-mm-dd")

if __name__ == '__main__':
    app.run(debug=True)