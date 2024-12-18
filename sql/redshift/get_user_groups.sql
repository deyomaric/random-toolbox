SELECT
    g.groname AS group_name,
    u.usename AS user_name
FROM
    pg_group g
JOIN
    pg_user u
ON
    u.usesysid = ANY(g.grolist)
ORDER BY
    group_name,
    user_name;
