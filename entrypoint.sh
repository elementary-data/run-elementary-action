#!/usr/bin/env bash

WAREHOUSE_TYPE=$1
PROFILES_YML=$2
EDR_COMMAND=$3
BIGQUERY_KEYFILE=$4

echo "Installing Elementary with '$WAREHOUSE_TYPE' adapter."
pip3 install "elementary-data[$WAREHOUSE_TYPE]"



echo "Configuring Dbt profile."
mkdir -p ~/.dbt
echo $PROFILES_YML > ~/.dbt/profiles.yml
echo $BIGQUERY_KEYFILE > /tmp/bigquery_keyfile.json

echo "Running the edr command."
bash -c $EDR_COMMAND
