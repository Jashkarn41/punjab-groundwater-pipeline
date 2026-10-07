/*CREATE DATABASE IF NOT EXISTS falde;
USE falde;

CREATE TABLE pozzi (
    ow_id VARCHAR(20) NOT NULL PRIMARY KEY,
    location VARCHAR(100) NOT NULL,
    lat DOUBLE NOT NULL,
    longi DOUBLE NOT NULL
);

CREATE TABLE misure (
    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    ow_id VARCHAR(20) NOT NULL,
    numero_data DATE NOT NULL,
    wl_mbgl DECIMAL(6, 2) NOT NULL,
    CONSTRAINT collegamento_pozzi FOREIGN KEY (ow_id) REFERENCES pozzi (ow_id)
);
*/