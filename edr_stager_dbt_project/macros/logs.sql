{% macro edr_stager_log(msg, info=True) %}
    {%- if execute %}
        {% do log('edr_stager: ' ~ msg, info=info) %}
    {%- endif %}
{% endmacro %}