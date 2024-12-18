SELECT
    DISTINCT Grantee AS group_name
FROM
    information_schema.user_privileges
WHERE
    Grantee LIKE '%@%'
ORDER BY
    group_name;
