drop database if exists dominoes_tst;
drop user if exists dominoestst;
create user dominoestst with password 'whistle';
create database dominoes_tst;
grant all privileges on database dominoes_tst to dominoestst;

