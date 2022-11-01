#!/usr/bin/env bash

ADAPTER=$1
PROFILES_YML=$2
EDR_COMMAND=$3
BIGQUERY_KEYFILE=$4
GCS_KEYFILE=$5
TARGET=$6

pip install "dbt-$ADAPTER"

echo "Initializing environment."
mkdir -p ~/.dbt
echo "$PROFILES_YML" > ~/.dbt/profiles.yml
echo "$BIGQUERY_KEYFILE" > /tmp/bigquery_keyfile.json
echo "$GCS_KEYFILE" > /tmp/gcs_keyfile.json

echo "Getting Elementary dbt package version."
if [ -z "$TARGET" ]
then
  DBT_PKG_VER=$(dbt -q run-operation get_elementary_dbt_pkg_version --project-dir /edr_stager_dbt_project)
else
  DBT_PKG_VER=$(dbt -q run-operation -t $TARGET get_elementary_dbt_pkg_version --project-dir /edr_stager_dbt_project)
fi
echo "Elementary's dbt package version - $DBT_PKG_VER"

echo "Installing Elementary with '$ADAPTER' adapter."
if [ -z "$DBT_PKG_VER" ]
then
  echo "Installing latest edr version."
  pip install "elementary-data[$ADAPTER]"
else
  echo "Installing latest compatible edr version."
  pip install "elementary-data[$ADAPTER]~=$DBT_PKG_VER"
fi

echo "Running the edr command."
bash -c "$EDR_COMMAND"
