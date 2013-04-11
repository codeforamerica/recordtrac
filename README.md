public-records
==============

This is a portal to display public record requests to the community and the City of Oakland.


## Installation

This application requires [Postgres](http://www.postgresapp.com/) and Xcode developer tools to be installed.

    /Applications/Postgres.app/Contents/MacOS/bin/psql
    CREATE DATABASE publicrecords;

In a new window:

    git clone git://github.com/codeforamerica/public-records.git
    cd public-records
    sudo pip install -r requirements.txt
    mkdir uploads

[![Build Status](https://travis-ci.org/codeforamerica/public-records.png?branch=master)](https://travis-ci.org/codeforamerica/public-records)