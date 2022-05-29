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
con = engine.connect()

# reflect an existing database into a new model
HI_base = automap_base()
HI_base.metadata.create_all(con)

# reflect the tables
HI_base.prepare(con, reflect=True)

# Save references to each table
hi_meas = HI_base.classes.measurement
hi_stati = HI_base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind=con)
session

# Find the most recent date in the data set.
meas_db = pd.read_sql_query("select * from measurement", con)
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
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    year_prec = last_year.reset_index(drop=True, inplace=True)
    year_prec = year_prec.drop(['id', 'station', 'date', 'tobs'], axis=1)
    prec_html = year_prec.to_json()

    return prec_html


@app.route("/api/v1.0/stations")
def stations():

    stations = meas_db.groupby("station").count().sort_values(["id"], ascending=False)
    stations = stations.drop(['id', 'date', 'prcp', 'tobs'], axis=1)
    stat_html = stations.to_json()
    return stat_html

@app.route("/api/v1.0/tobs")
def tobs():

    act_stat = last_year.loc[last_year["station"] =='USC00519281']
    act_stat = act_stat.drop(['id', 'date', 'station', 'tobs'], axis=1)
    act_stat_html = act_stat.to_json()

    return act_stat_html

# @app.route("/api/v1.0/start")
# def start():

#     last_year = date_sort.sort_index().last('365D')
#     year_prec = last_year.drop(['id', 'station', 'date', 'tobs'], axis=1)
#     prec_json = year_prec.to_html(classes="year_prec")

# @app.route("/api/v1.0/start_to_end")
# def start_to_end():

#     last_year = date_sort.sort_index().last('365D')
#     year_prec = last_year.drop(['id', 'station', 'date', 'tobs'], axis=1)
#     prec_json = year_prec.to_html(classes="year_prec")

    return prec_json   

if __name__ == '__main__':
    app.run(debug=True)

session.close()