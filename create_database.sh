#!/bin/env bash

psql -c 'create database testdatabase_${TRAVIS_BUILD_ID}_${TRAVIS_JOB_ID};' -U postgres
