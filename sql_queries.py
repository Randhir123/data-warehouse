import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

ARN             = config.get('IAM_ROLE', 'ARN')
LOG_DATA        = config.get('S3', 'LOG_DATA')
LOG_JSONPATH    = config.get('S3', 'LOG_JSONPATH')
SONG_DATA       = config.get('S3', 'SONG_DATA')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplay"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS song"
artist_table_drop = "DROP TABLE IF EXISTS artist"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES

staging_events_table_create= ("""
CREATE TABLE IF NOT EXISTS staging_events
(
    staging_event_id     BIGINT IDENTITY(0,1) NOT NULL,
    artist               VARCHAR,
    auth                 VARCHAR,
    firstName            VARCHAR,
    gender               VARCHAR,
    itemInSession        VARCHAR,       
    lastName             VARCHAR,
    length               VARCHAR,
    level                VARCHAR,
    location             VARCHAR,
    method               VARCHAR,
    page                 VARCHAR,
    registration         VARCHAR,    
    sessionid            INTEGER NOT NULL DISTKEY SORTKEY,
    song                 VARCHAR,
    status               INTEGER,
    ts                   BIGINT NOT NULL,
    userAgent            VARCHAR,
    user_id              INTEGER
);
""")

staging_songs_table_create = ("""
CREATE TABLE IF NOT EXISTS staging_songs
(
    num_songs           INTEGER,
    artist_id           VARCHAR NOT NULL DISTKEY SORTKEY,
    artist_latitude     VARCHAR,
    artist_longitude   VARCHAR,
    artist_location     VARCHAR,
    artist_name         VARCHAR NOT NULL,
    song_id             VARCHAR NOT NULL,
    title               VARCHAR NOT NULL,
    duration            NUMERIC,
    year                INTEGER
);
""")

songplay_table_create = ("""
CREATE TABLE IF NOT EXISTS songplay
(
    songplay_id    INTEGER NOT NULL IDENTITY(0,1) SORTKEY,
    start_time     TIMESTAMP NOT NULL,
    user_id        VARCHAR NOT NULL DISTKEY,
    level          VARCHAR(10) NOT NULL,
    song_id        VARCHAR NOT NULL,
    artist_id      VARCHAR NOT NULL,
    session_id     VARCHAR NOT NULL,
    location       VARCHAR,
    user_agent     VARCHAR
);
""")

user_table_create = ("""
CREATE TABLE IF NOT EXISTS users
(
    user_id        INTEGER NOT NULL SORTKEY,
    first_name     VARCHAR NOT NULL,
    last_name      VARCHAR,
    gender         VARCHAR(1) NOT NULL,
    level          VARCHAR(50) NOT NULL
) diststyle all;
""")

song_table_create = ("""
CREATE TABLE IF NOT EXISTS song
(
    song_id        VARCHAR NOT NULL SORTKEY,
    title          VARCHAR NOT NULL,
    artist_id      VARCHAR NOT NULL,
    year           INTEGER NOT NULL,
    duration       NUMERIC NOT NULL
) diststyle all;
""")

artist_table_create = ("""
CREATE TABLE IF NOT EXISTS artist
(
    artist_id      VARCHAR NOT NULL SORTKEY,
    name           VARCHAR NOT NULL,
    location       VARCHAR,
    latitude       NUMERIC,
    longitude      NUMERIC
) diststyle all;
""")

time_table_create = ("""
CREATE TABLE IF NOT EXISTS time
(
    start_time    TIMESTAMP NOT NULL SORTKEY,
    hour          SMALLINT,
    day           SMALLINT,
    week          SMALLINT,
    month         SMALLINT,
    year          SMALLINT,
    weekday       SMALLINT
) diststyle all;
""")

# STAGING TABLES

staging_events_copy = ("""
    COPY staging_events FROM {}
    credentials 'aws_iam_role={}'
    format as json {}
    STATUPDATE ON
    region 'us-west-2';
""").format(LOG_DATA, ARN, LOG_JSONPATH)
                       
staging_songs_copy = ("""
    COPY staging_songs FROM {}
    credentials 'aws_iam_role={}'
    format as json 'auto'
    ACCEPTINVCHARS AS '^'
    STATUPDATE ON
    region 'us-west-2';
""").format(SONG_DATA, ARN)

# FINAL TABLES

songplay_table_insert = ("""
INSERT INTO songplay (start_time, user_id, level, song_id, artist_id, session_id, location, user_agent) 
    SELECT  DISTINCT TIMESTAMP 'epoch' + se.ts/1000 * INTERVAL '1 second'   AS start_time,
            se.user_id                   AS user_id,
            se.level                    AS level,
            ss.song_id                  AS song_id,
            ss.artist_id                AS artist_id,
            se.sessionId                AS session_id,
            se.location                 AS location,
            se.userAgent                AS user_agent
    FROM staging_events se
    JOIN staging_songs ss
    ON (se.artist = ss.artist_name)
    WHERE se.page = 'NextSong';
""")

user_table_insert = ("""
INSERT INTO users (user_id, first_name, last_name, gender, level)
    SELECT  DISTINCT se.user_id          AS user_id,
            se.firstName                AS first_name,
            se.lastName                 AS last_name,
            se.gender                   AS gender,
            se.level                    AS level
    FROM staging_events se
    WHERE se.page = 'NextSong';
""")

song_table_insert = ("""
INSERT INTO song (song_id, title, artist_id, year, duration)
    SELECT  DISTINCT ss.song_id         AS song_id,
            ss.title                    AS title,
            ss.artist_id                AS artist_id,
            ss.year                     AS year,
            ss.duration                 AS duration
    FROM staging_songs ss;
""")

artist_table_insert = ("""
INSERT INTO artist (artist_id, name, location,latitude, longitude)
    SELECT  DISTINCT ss.artist_id       AS artist_id,
            ss.artist_name              AS name,
            ss.artist_location          AS location,
            ss.artist_latitude          AS latitude,
            ss.artist_longitude         AS longitude
    FROM staging_songs ss;
""")

time_table_insert = ("""
INSERT INTO time (start_time, hour, day, week, month, year, weekday)
    SELECT  DISTINCT TIMESTAMP 'epoch' + se.ts/1000 \
                * INTERVAL '1 second'        AS start_time,
            EXTRACT(hour FROM start_time)    AS hour,
            EXTRACT(day FROM start_time)     AS day,
            EXTRACT(week FROM start_time)    AS week,
            EXTRACT(month FROM start_time)   AS month,
            EXTRACT(year FROM start_time)    AS year,
            EXTRACT(week FROM start_time)    AS weekday
    FROM    staging_events se
    WHERE se.page = 'NextSong';
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
