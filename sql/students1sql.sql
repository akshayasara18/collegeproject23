use ak;

CREATE TABLE students1 (
    register_no VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100)
);
INSERT INTO students1 (register_no, name) VALUES
('2023B01', 'Aarthy P'),
('2023B02', 'Akshaya A'),
('2023B03', 'Akshaya sara S'),
('2023B04', 'Delbeena S'),
('2023B05', 'Farisa S'),
('2023B06', 'Guru selvi S');
select*from students1
drop table students1