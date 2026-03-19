create database ak;
Use ak;


CREATE TABLE student_reg (
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