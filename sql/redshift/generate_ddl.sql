SELECT
    'CREATE TABLE ' || table_schema || '.' || table_name || ' (' || listagg(column_name || ' ' || data_type, ', ') WITHIN GROUP (ORDER BY ordinal_position) || ');' AS ddl
FROM
    information_schema.columns
WHERE
    table_schema NOT IN ('pg_catalog', 'information_schema')
GROUP BY
    table_schema, table_name;
