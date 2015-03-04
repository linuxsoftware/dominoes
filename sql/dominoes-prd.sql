drop database if exists dominoes_prd;
drop user if exists dominoesprd;
create user dominoesprd with password 'sportscentre';
create database dominoes_prd;
grant all privileges on database dominoes_prd to dominoesprd;

