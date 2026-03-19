create database ak;
Use ak;


CREATE TABLE student_reg_crt (
    id INT PRIMARY KEY IDENTITY(1,1),
    name1 NVARCHAR(100),
    regno1 NVARCHAR(50),
    dep1 NVARCHAR(100),
    year1 NVARCHAR(10),
    pic VARBINARY(MAX),
    blood1 NVARCHAR(10),
    phone1 NVARCHAR(20),
    email1 NVARCHAR(100),
    city1 NVARCHAR(100)
);
select*from student_reg_crt;
-- to make the reg no unique so that we can make it as foreign key in attendance table

ALTER TABLE student_reg_crt
ADD CONSTRAINT uq_regno1 UNIQUE(regno1);
drop table student_reg_crt


