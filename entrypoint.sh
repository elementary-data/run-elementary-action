#!/usr/bin/env bash

WAREHOUSE_TYPE=$1
PROFILES_YML=$2
ELEMENTARY_CONF_YML=$3
EDR_COMMAND=$4

echo "Installing Elementary with '$WAREHOUSE_TYPE' adapter."
pip3 install "elementary-data[$WAREHOUSE_TYPE]"

echo "Configuring Dbt profile."
mkdir -p ~/.dbt
echo "$BIGQUERY_KEYFILE" > ~/.dbt/bigquery_keyfile.json
echo "$PROFILES_YML" > ~/.dbt/profiles.yml

echo "Running the edr command."
$EDR_COMMAND
