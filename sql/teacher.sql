CREATE TABLE Teacher (
    TeacherID NVARCHAR(50) PRIMARY KEY,  -- Teacher ID unique
    TeacherName NVARCHAR(100) NOT NULL,
	Gender NVARCHAR(10) NOT NULL,
    Department NVARCHAR(100) NOT NULL,
    Email NVARCHAR(100) NOT NULL,
    Phone NVARCHAR(20) NOT NULL,
	Designation NVARCHAR(50) NOT NULL,
	Address NVARCHAR(100) NOT NULL

);

select * from Teacher

