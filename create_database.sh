#!/bin/env bash

BUILD_N="$(echo $TRAVIS_JOB_NUMBER | tr '.' '_')"

psql -c "create database testdatabase_$BUILD_N;" -U postgres
