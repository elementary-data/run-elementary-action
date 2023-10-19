# Elementary GitHub Action

This action allows you to run `edr` as a GitHub Action.  
In order to use this action, you will need to create a workflow within your repository.  
To create a new workflow, simply create `.github/workflows/elementary.yml` within your repository.

If you have not yet installed Elementary's dbt package, please refer
to [this guide](https://docs.elementary-data.com/quickstart#how-to-install-elementary-dbt-package).

## Setup

`edr` requires a dbt connection profile called `elementary` that points to your Elementary schema in the warehouse.
More information on that can be found [here](https://docs.elementary-data.com/quickstart-cli).
Accordingly, we'll need to provide the action with that profile.

In addition, we recommend that you integrate `edr` with your dbt project.
This will make sure that the used data is kept up-to-date by running Elementary's models ahead of time.
Accordingly, we'll need to `checkout` the dbt project before running the action, and provide its connection profile.

If you already have a `profiles.yml` in your repository,
checkout the repository and pass the environment variables that are used within it to the action.
`edr` will automatically pick up on the `profiles.yml` file.

```yaml
- name: Checkout dbt project
  uses: actions/checkout@v3

- name: Run Elementary
  uses: elementary-data/run-elementary-action@v1.11
  env:
    USER: ${{ secrets.USER }} # Used in profiles.yml.
    PASSWORD: ${{ secrets.PASSWORD }}
  with:
    edr-command: ...
```

If you do not have a `profiles.yml` in your repository, you can pass the credentials directly to the action.
In order to generate the `profiles.yml` that is needed by `edr` to operate, run the following command within your dbt
project:

```shell
dbt run-operation --args '{"method": "github-actions"}' elementary.generate_elementary_cli_profile
```

Afterwards, fill in the missing fields and copy the output to a secret in your repository.
Once you've done that, you can pass the secret to the action.

```yaml
- name: Checkout dbt project
  uses: actions/checkout@v3

- name: Run Elementary
  uses: elementary-data/run-elementary-action@v1.11
  with:
    profiles-yml: ${{ secrets.ELEMENTARY_PROFILES_YML }}
    edr-command: ...
```

## Usage

Below is a basic example of an Elementary workflow file.  
For more information on how to
use [GitHub workflows](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions).

```yaml
name: Run Elementary
on:
  # Run the action when a push to the main branch of the repository is made.
  push:
    branches: [ "main", "master" ]

  # Run the action when a pull request to the main branch is opened.
  pull_request:
    branches: [ "main", "master" ]

  # Run the action in a scheduled manner every hour.
  schedule:
    - cron: '0 * * * *'

  # Allows you to run this workflow manually from the Actions tab.
  workflow_dispatch:

jobs:
  elementary:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout dbt project
        uses: actions/checkout@v3

      - name: Run Elementary
        uses: elementary-data/run-elementary-action@v1.11
        with:
          warehouse-type: bigquery # Type of warehouse to use (bigquery, snowflake, redshift, etc.)
          adapter-version: 1.5.0 # The dbt-adapter version that should be used (If not provided the latest version will be used). 
          profiles-yml: ${{ secrets.ELEMENTARY_PROFILES_YML }} # Content of ~/.dbt/profiles.yml, should have an `elementary` profile.
          edr-command:
            edr monitor
              --slack-token "${{ secrets.SLACK_TOKEN }}"
              --slack-channel-name "${{ secrets.SLACK_CHANNEL_NAME }}"
            &&
            edr report
              --file-path "report.html"
            &&
            edr send-report
              --slack-token "${{ secrets.SLACK_TOKEN }}"
              --slack-channel-name "${{ secrets.SLACK_CHANNEL_NAME }}"
              --aws-access-key-id "${{ secrets.AWS_ACCESS_KEY_ID }}"
              --aws-secret-access-key "${{ secrets.AWS_SECRET_ACCESS_KEY }}"
              --s3-bucket-name "${{ secrets.S3_BUCKET_NAME }}"
              --google-service-account-path "/tmp/gcs_keyfile.json"
              --gcs-bucket-name "${{ secrets.GCS_BUCKET_NAME }}"
              --update-bucket-website "true"

          bigquery-keyfile: ${{ secrets.BIGQUERY_KEYFILE }} # If using BigQuery, the content of its keyfile.
          gcs-keyfile: ${{ secrets.GCS_KEYFILE }} # If using GCS, the content of its keyfile.

      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: report.html
          path: report.html

      - name: Upload log
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: edr.log
          path: edr.log
```

## Configuration

### Elementary Profile

Note that the `profiles-yml` argument needs to be the **content** of `profiles.yml` rather than a path to it.  
You can create a secret and then pass it.

```yml
profiles-yml: ${{ secrets.PROFILES_YML }}
```

Please make sure to quote any field that may contain special characters (For instance `'#$Password\&^'`).

<img width="1097" alt="image" src="https://user-images.githubusercontent.com/30181361/185250359-918a10ab-b323-4ce3-b598-307ecedadeb9.png">

### BigQuery Keyfile Authentication

If you're using BigQuery with a key file,
supply the `bigquery-keyfile` argument to the action and make sure your `keyfile` in the `profiles-yml`
is `/tmp/bigquery_keyfile.json`.

### Google Cloud Storage Keyfile

If you want to upload your report to a Google Cloud Storage bucket using `send-report`,
supply the `gcs-keyfile` argument to the action with the **content** of your Google service account keyfile.
Afterwards, use `edr monitor send-report --google-service-account-path /tmp/gcs_keyfile.json` to upload the report.

## Having trouble?

Please contact us
on [Slack](https://join.slack.com/t/elementary-community/shared_invite/zt-uehfrq2f-zXeVTtXrjYRbdE_V6xq4Rg), we're here
to help!
