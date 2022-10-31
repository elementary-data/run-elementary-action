#!/usr/bin/env bash

WAREHOUSE_TYPE=$1
PROFILES_YML=$2
EDR_COMMAND=$3
BIGQUERY_KEYFILE=$4
GCS_KEYFILE=$5

pip install "dbt-$WAREHOUSE_TYPE"

echo "Initializing environment."
mkdir -p ~/.dbt
echo "$PROFILES_YML" > ~/.dbt/profiles.yml
echo "$BIGQUERY_KEYFILE" > /tmp/bigquery_keyfile.json
echo "$GCS_KEYFILE" > /tmp/gcs_keyfile.json

echo "Getting Elementary dbt package version."
DBT_PKG_VER=$(dbt -q run-operation get_elementary_dbt_pkg_version --project-dir /edr_stager_dbt_project)
echo "Elementary's dbt package version - $DBT_PKG_VER"

echo "Installing Elementary with '$WAREHOUSE_TYPE' adapter."
if [ -z "$DBT_PKG_VER" ] then
  echo "Installing latest edr version."
  pip install "elementary-data[$WAREHOUSE_TYPE]"
else
  echo "Installing latest compatible edr version."
  pip install "elementary-data[$WAREHOUSE_TYPE]~=$DBT_PKG_VER"
fi

echo "Running the edr command."
bash -c "$EDR_COMMAND"
