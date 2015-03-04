drop database if exists dominoes_dev;
drop user if exists dominoesdev;
create user dominoesdev with password 'clipboard';
create database dominoes_dev;
grant all privileges on database dominoes_dev to dominoesdev;

