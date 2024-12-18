SELECT
    pid,
    user_name,
    db,
    starttime,
    substring(query, 1, 50) AS query_snippet,
    elapsed::interval AS duration
FROM
    stv_recents
WHERE
    state = 'Running' -- Change to 'Finished' if you want recently finished queries
ORDER BY
    elapsed DESC
LIMIT 10; -- Adjust the limit as needed
