/*

CREATE DATABASE IF NOT EXISTS falde;
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

describe misure;

create user 'falde_user'@'localhost' identified by 'root';
grant all privileges on falde.* to 'falde_user'@'localhost';

select count(*) from pozzi;
describe falde.misure; -- controllo l'errore in quanto il count mi risulta 0

alter table falde.misure modify wl_mbgl decimal(6,2) not null;
select count(*) from falde.misure;

select year(numero_data) as year ,count(*) as misure, avg(wl_mbgl) as average
from falde.misure 
group by year(numero_data)
order by year(numero_data);

*/