#!/bin/env bash

BUILD_N="$TRAVIS_JOB_NUMBER"
echo $BUILD_N

psql -c "create database testdatabase_$BUILD_N;" -U postgres
