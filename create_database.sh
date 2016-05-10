#!/bin/env bash

BUILD_N="$TRAVIS_BUILD_ID"_"$TRAVIS_JOB_ID"
echo $BUILD_N

psql -c "create database testdatabase_$BUILD_N;" -U postgres
