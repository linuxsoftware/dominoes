drop database if exists dominoes_tests;
drop user if exists dominoestests;
create user dominoestests with password 'olympics';
create database dominoes_tests;
grant all privileges on database dominoes_tests to dominoestests;

