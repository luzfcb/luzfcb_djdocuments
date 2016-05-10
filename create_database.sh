#!/bin/env bash

BUILD_N="$(echo $TRAVIS_JOB_NUMBER | tr '.' '_')"
psql -c "create database testdatabase_$BUILD_N;" -U postgres
export DATABASE_URL="postgres://postgres:@localhost:5432/testdatabase_$BUILD_N"
echo "DATABASE_URL=${DATABASE_URL}"


