FROM python:3.8

COPY edr_stager_dbt_project /edr_stager_dbt_project
COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
