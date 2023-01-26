{% macro get_elementary_dbt_pkg_version() %}
  {% set database, schema = target_database(), target.schema %}
  {% set invocations_relation = adapter.get_relation(database, schema, 'dbt_invocations') %}
  {% if not invocations_relation %}
    {% do elementary_internal.edr_stager_log('') %}
    {% do return(none) %}
  {% endif %}

  {% set get_pkg_version_query %}
    select elementary_version from {{ invocations_relation }} order by generated_at desc limit 1
  {% endset %}
  {% set result = dbt.run_query(get_pkg_version_query)[0][0] %}
  {% do elementary_internal.edr_stager_log(result or '') %}
{% endmacro %}

{% macro target_database() -%}
    {{ return(adapter.dispatch('target_database')()) }}
{%- endmacro %}

-- Postgres and Redshift
{% macro default__target_database() %}
    {% set database = target.dbname %}
    {{ return(database) }}
{% endmacro %}

{% macro snowflake__target_database() %}
    {% set database = target.database %}
    {{ return(database) }}
{% endmacro %}

{% macro bigquery__target_database() %}
    {% set database = target.project %}
    {{ return(database) }}
{% endmacro %}
