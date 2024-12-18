DELIMITER //

CREATE PROCEDURE generate_ddls()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE tbl_name VARCHAR(255);
    DECLARE cur CURSOR FOR SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE() AND table_type = 'BASE TABLE';
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    -- Temporary table to store DDL statements
    CREATE TEMPORARY TABLE IF NOT EXISTS ddl_statements (ddl TEXT);

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO tbl_name;
        IF done THEN
            LEAVE read_loop;
        END IF;

        SET @ddl_statement = NULL;
        SET @query = CONCAT('SHOW CREATE TABLE ', tbl_name);
        PREPARE stmt FROM @query;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;

        -- Extract the DDL statement from the result
        FETCH cur INTO tbl_name;
        FETCH cur INTO @ddl_statement;

        -- Insert the DDL statement into the temporary table
        INSERT INTO ddl_statements (ddl) VALUES (@ddl_statement);
    END LOOP;

    CLOSE cur;

    -- Select all DDL statements
    SELECT * FROM ddl_statements;

    -- Clean up
    DROP TEMPORARY TABLE IF EXISTS ddl_statements;
END //

DELIMITER ;
