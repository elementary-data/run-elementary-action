#!/usr/bin/env bash

WAREHOUSE_TYPE=$1
PROFILES_YML=$2
ELEMENTARY_CONF_YML=$3
SHOULD_RUN_MONITOR=$4
SHOULD_RUN_SEND_REPORT=$5

echo "Installing Elementary with '$WAREHOUSE_TYPE' adapter."
pip3 install "elementary-data[$WAREHOUSE_TYPE]"

echo "Configuring Elementary."
mkdir -p ~/.edr
echo "$ELEMENTARY_CONF_YML" > ~/.edr/config.yml

echo "Configuring Dbt."
mkdir -p ~/.dbt
echo "$BIGQUERY_KEYFILE" > ~/.dbt/bigquery_keyfile.json
echo "$PROFILES_YML" > ~/.dbt/profiles.yml

if [ "$SHOULD_RUN_MONITOR" = "true" ]; then
    edr monitor
fi

if [ "$SHOULD_RUN_SEND_REPORT" = "true" ]; then
    edr monitor send-report
fi
