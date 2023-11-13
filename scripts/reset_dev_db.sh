#!/bin/sh 

rm ./data/db.sqlite 
cat ./app/sql/weather_create_table.sql | sqlite3 ./data/db.sqlite
source_weather_cli ./data/may --database-url ./data/db.sqlite
