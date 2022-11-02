FROM python:3.8

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY edr_stager_dbt_project edr_stager_dbt_project
COPY entrypoint.sh entrypoint.sh

CMD [ "python", "entrypoint.py" ]
