# Data Warehouse

## Introduction
A music streaming startup, Sparkify, has grown their user base and song database and want to move their processes and data onto the cloud. Their data resides in S3, in a directory of JSON logs on user activity on the app, as well as a directory with JSON metadata on the songs in their app.

The purpose of the project is to build an ETL pipeline that extracts their data from S3, stages them in Redshift, and transforms data into a set of dimensional tables for their analytics team to continue finding insights in what songs their users are listening to.

## Dataset
The first dataset contains the song data in JSON format. Files are partitioned by first three letters of each song's track ID, e.g. `song_data/A/B/C/TRABCEI128F424C983.json`. Example of a single song file:

    {
        "num_songs": 1, 
        "artist_id": "ARJIE2Y1187B994AB7", 
        "artist_latitude": null, 
        "artist_longitude": null, 
        "artist_location": "", 
        "artist_name": "Line Renaud", 
        "song_id": "SOUPIRU12A6D4FA1E1", 
        "title": "Der Kleine Dompfaff", 
        "duration": 152.92036, 
        "year": 0
    }
The second dataset contains the log metadata. The log files are paratitioned by year and month, e.g., `log_data/2018/11/2018-11-12-events.json`. Example entry in a log file:

    {
        "artist": "Pavement",
        "auth": "Logged in",
        "firstName": "Sylvie",
        "gender": "F",
        "iteminSession": 0,
        "lastName": "Cruz",
        "length": 99.16036,
        "level": "free",
        "location": "Kiamath Falls, OR",
        "method": "PUT",
        "page": "NextSong",
        "registration": 1.540266e+12,
        "sessionId": 345,
        "song": "Mercy: The Laundromat",
        "status": 200,
        "ts": 1541990258796,
        "userAgent": "Mozzilla/5.0...",
        "userId": 10
    }

These data are stored in two staging tables - `staging_events` for event dataset and `staging_songs` for
song dataset. 

## Database Schema

To represent this data for analytical use cases, a Star Schema is appropriate. 

The dimension tables are -

1. `users` - users in the app

        user_id
        first_name
        last_name
        gender
        level

2. `song`  - songs in music database

        song_id
        title
        artist_id
        year
        duration

3. `artist` - artists in music database

        artist_id
        name
        location
        latitude
        longtitude

4. `time` - timestamps of records in songplays

        start_time
        hour
        day
        week
        month
        year
        weekday

The fact table is - `songplays` and it contains foreign keys to four dimension tables.

    songplay_id
    start_time REFERENCES time(start_time)
    user_id REFERENCES users(user_id)
    song_id REFERENCES song(song_id)
    artist_id REFERENCES artist(artist_id)
    level
    session_id
    location
    user_agent

## ETL Process

We create a Redshift cluster using Intrastructure-as-Code. The data in S3 buckets are copied to the corresponding staging
tables.

Once data is available in staging SQL Tables, the ETL is SQL-to-SQL. The SQL queries to create tables and insert data into the tables
are available in `sql_queries.py`.

To run the ETL pipeline, defined in `etl.py`, first run `create_tables.py` from the console to create all the tables

    python create_tables.py

To run the command from a Jupyter notebook cell, precede the above with an exclamation.

    ! python create_tables.py

and then run `etl.py` to insert data into staging tables and then from staging tables to the tables in star schema.

    python etl.py

## Test

To verify that the ETL process is a success, we can go the Redshift cluster in AWS Console and verify that the tables are created with right schema and data is correctly populated.
