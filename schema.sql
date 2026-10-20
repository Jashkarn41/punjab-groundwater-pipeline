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

select count(*) from pozzi;
describe falde.misure; -- controllo l'errore in quanto il count mi risulta 0

alter table falde.misure modify wl_mbgl decimal(6,2) not null;
select count(*) from falde.misure;

select year(numero_data) as year ,count(*) as misure, avg(wl_mbgl) as average
from falde.misure 
group by year(numero_data)
order by year(numero_data);

set sql_safe_updates = 0;
delete from falde.misure;
delete from falde.pozzi;
set sql_safe_updates = 1; -- Seguo il consiglio di un amico Data Engineer e sistemo il problema dell'idempotenza del mio database

select count(*) from falde.misure;

select count(*) from falde.misure;
select count(*) from falde.pozzi; 

-- Ho eseguito piu volte il select count(*) e noto di aver sistemato il problema dell'idempotenza

-- Sistemo il data dopo il consiglio di un professional Data Engineer

create table scarti(
	id bigint not null auto_increment primary key,
    ow_id varchar(20) not null,
    numero_data date not null,
    wl_mbgl decimal(6,2) null,
    reason varchar(40) not null,
    start_year year not null,
    end_year year not null,
    loaded datetime default current_timestamp not null
);

*/
