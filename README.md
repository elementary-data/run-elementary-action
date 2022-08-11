# Elementary GitHub Action

This action allows you to run `edr` as a GitHub Action.  
In order to use this action, you will need to create a workflow within your repository.  
To create a new workflow, simply create `.github/workflows/elementary.yml` within your repository.

If you have not yet installed Elementary's dbt package, please refer
to [this guide](https://docs.elementary-data.com/quickstart#how-to-install-elementary-dbt-package).

In order to generate the `profiles.yml` that is needed by `edr` to operate, run the following command within your Dbt
project:

```shell
dbt run-operation --args '{"method": "github-actions"}' elementary.generate_elementary_cli_profile
```

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
      - name: Run Elementary
        uses: elementary-data/run-elementary-action@main
        with:
          warehouse-type: ${{ secrets.WAREHOUSE_TYPE }} # Type of warehouse to use (bigquery, snowflake, redshift, etc.)
          profiles-yml: ${{ secrets.PROFILES_YML }} # Content of ~/.dbt/profiles.yml, should have an `elementary` profile.
          edr-command: |
            edr monitor --slack-token ${{ secrets.SLACK_TOKEN }} --slack-channel-name ${{ secrets.SLACK_CHANNEL_NAME }}
            edr monitor send-report --slack-token ${{ secrets.SLACK_TOKEN }} --slack-channel-name ${{ secrets.SLACK_CHANNEL_NAME }}

          bigquery-keyfile: ${{ secrets.BIGQUERY_KEYFILE }} # If using BigQuery, the content of its keyfile.
```

## BigQuery Keyfile Authentication

If you're using BigQuery with a key file,
supply the `bigquery-keyfile` argument to the action and make sure your `keyfile` in the `profiles-yml`
is `/tmp/bigquery_keyfile.json`.

Having trouble? Please contact us
on [Slack](https://join.slack.com/t/elementary-community/shared_invite/zt-uehfrq2f-zXeVTtXrjYRbdE_V6xq4Rg), we're here
to help!
