import numpy as np
import pandas as pd
import os
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, render_template

# create engine to hawaii.sqlite
db_path = os.path.join("Resources","hawaii.sqlite")
engine = create_engine(f"sqlite:///{db_path}")
# con = engine.connect()

# reflect an existing database into a new model
HI_base = automap_base()
HI_base.metadata.create_all(engine)

# reflect the tables
HI_base.prepare(engine, reflect=True)

# Save references to each table
hi_meas = HI_base.classes.measurement
hi_stati = HI_base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind=engine)
session

# Find the most recent date in the data set.
meas_db = pd.read_sql_query("select * from measurement", engine)
date_sort = meas_db.sort_values("date", ascending=False)
date_sort["dateind"] = pd.to_datetime(date_sort["date"])
date_sort = date_sort.set_index("dateind")
last_year = date_sort.sort_index().last('365D')

# Passenger = Base.classes.passenger

app = Flask(__name__)


@app.route("/")
def welcome():
    """List all options"""
    return (
        f"Available Routes:<br/>"
        f"/<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start date<br/>"
        f"/api/v1.0/start date/end date<br/>^<br/>"
        "Please for start date and end date, enter the date in the format of 'yyyy-mm-dd' replacing 'start date' and 'end date'<br/>"
        "Data is between 2010-01-01 and 2017-08-23"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():

    year_prec = last_year.drop(['id', 'station', 'date', 'tobs'], axis=1).reset_index()
    prec_html = year_prec.to_dict(orient="split")

    return jsonify(prec_html)


@app.route("/api/v1.0/stations")
def stations():

    stations = meas_db.groupby("station").count().sort_values(["id"], ascending=False)
    stations = stations.drop(['id', 'date', 'prcp', 'tobs'], axis=1).reset_index()
    stat_html = stations.to_dict(orient="split")

    return jsonify(stat_html)

@app.route("/api/v1.0/tobs")
def tobs():

    act_stat = last_year.loc[last_year["station"] =='USC00519281']
    act_stat = act_stat.drop(['id', 'date', 'station', 'tobs'], axis=1).reset_index()
    act_stat_html = act_stat.to_dict(orient="split")

    return jsonify(act_stat_html)

@app.route("/api/v1.0/<start>")
def start(start):

    start_que = meas_db.loc[meas_db["date"] >= start]
    start_anly = start_que["tobs"].agg(["min","max","mean"]).reset_index()
    start_json = start_anly.to_dict(orient="split")

    return jsonify(start_json)   

@app.route("/api/v1.0/<start>/<end>")
def start_to_end(start, end):

    start_que = meas_db.loc[(meas_db["date"] >= start) & (meas_db["date"] <= end)]
    start_anly = start_que["tobs"].agg(["min","max","mean"]).reset_index()
    start_json = start_anly.to_dict(orient="split")

    return jsonify(start_json) 

if __name__ == '__main__':
    app.run(debug=True)

session.close()