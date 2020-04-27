CREATE DATABASE IF NOT EXISTS medical_data;

USE medical_data;

DROP TABLE IF EXISTS patients;
CREATE TABLE patients (
  id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
  ssn INT NOT NULL,
  name VARCHAR(50) NOT NULL,
  birth_date DATE,
  contact_info VARCHAR(100),
  diagnosis VARCHAR(50) NOT NULL,
  severity INT,
  drugName VARCHAR(50) NOT NULL,
  dosage INT
);


DROP PROCEDURE IF EXISTS InsertPatients;

DELIMITER $$
CREATE PROCEDURE InsertPatients()
    BEGIN
        DECLARE i INT;
        DECLARE Length INT;
        DECLARE ssn INT;
        DECLARE name VARCHAR(50);
        DECLARE bday DATE;
        DECLARE contact VARCHAR(100);
        DECLARE diagnosis VARCHAR(50);
        DECLARE severity INT;
        DECLARE drugName VARCHAR(50);
        DECLARE dosage INT;
        SET i = 0;

        START TRANSACTION;
        WHILE i < 1000 DO
            -- Generate Number
            SET ssn = ROUND(RAND() * 100000000, 0);

            -- Generate Varchar
            SET name ='';
            SET Length = RAND() * 50;
            WHILE Length <> 0 DO
              SET name = CONCAT(name, substring('ABCDEFGHIJKLMNOPQRSTUVWXYZ ', rand()*26+1, 1));
              SET Length = Length - 1;
            END WHILE;

            -- Generate Date
            SET bday = CURRENT_TIMESTAMP - INTERVAL FLOOR(RAND() * 20000) DAY;

            -- Generate Varchar
            SET contact ='';
            SET Length = RAND() * 50;
            WHILE Length <> 0 DO
              SET contact = CONCAT(contact, substring('ABCDEFGHIJKLMNOPQRSTUVWXYZ ', rand()*26+1, 1));
              SET Length = Length - 1;
            END WHILE;

            -- Generate Varchar
            SET diagnosis ='';
            SET Length = RAND() * 50;
            WHILE Length <> 0 DO
              SET diagnosis = CONCAT(diagnosis, substring('ABCDEFGHIJKLMNOPQRSTUVWXYZ ', rand()*26+1, 1));
              SET Length = Length - 1;
            END WHILE;

            -- Generate Number
            SET severity = ROUND(RAND() * 10, 0);

            -- Generate Varchar
            SET drugName ='';
            SET Length = RAND() * 50;
            WHILE Length <> 0 DO
              SET drugName = CONCAT(drugName, substring('ABCDEFGHIJKLMNOPQRSTUVWXYZ ', rand()*26+1, 1));
              SET Length = Length - 1;
            END WHILE;

            -- Generate Number
            SET dosage = ROUND(RAND() * 100, 0);

            INSERT INTO patients(ssn,name,birth_date,contact_info,diagnosis,severity,drugName,dosage) VALUES (ssn,name,bday,contact,diagnosis,severity,drugName,dosage);
            SET i = i + 1;
        END WHILE;
        COMMIT;
    END$$
DELIMITER ;

CALL InsertPatients();

INSERT INTO patients(ssn,name,birth_date,contact_info,diagnosis,severity,drugName,dosage) VALUES (123456789,'Our Guy',CURDATE(),'email@email.com','a bad case of monday mornings',3,'coffee',20);
INSERT INTO patients(ssn,name,birth_date,contact_info,diagnosis,severity,drugName,dosage) VALUES (123456789,'Our Guy',CURDATE(),'email@email.com','coronavirus',8,'tylenol',10);
INSERT INTO patients(ssn,name,birth_date,contact_info,diagnosis,severity,drugName,dosage) VALUES (123456789,'Our Guy',CURDATE(),'email@email.com','Bowdens Malady',5,'pescaline D',6);
