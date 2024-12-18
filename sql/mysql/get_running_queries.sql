SELECT
    ID AS process_id,
    USER AS user_name,
    HOST AS host_name,
    DB AS database_name,
    COMMAND AS command_type,
    TIME AS duration_seconds,
    STATE AS query_state,
    INFO AS query_text
FROM
    information_schema.processlist
WHERE
    COMMAND != 'Sleep'
ORDER BY
    TIME DESC
LIMIT 10; -- Adjust the limit as needed
