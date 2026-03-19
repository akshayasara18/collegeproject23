use ak;

CREATE TABLE attendance (
    sno INT IDENTITY(1,1) PRIMARY KEY,            
    regno1 NVARCHAR(50) NOT NULL,                 -- Register number (FK)
    name1 NVARCHAR(100) NOT NULL,                 
    date DATE NOT NULL,                           -- Attendance date
    status NVARCHAR(10) CHECK (status IN ('Present', 'Absent', 'Late')),
    late_time TIME,
    marked_at DATETIME DEFAULT GETDATE(), 
            -- Time attendance was marked
    FOREIGN KEY (regno1) REFERENCES student_reg_crt(regno1),
    TeacherName NVARCHAR(100)

    CONSTRAINT uq_attendance UNIQUE (regno1, date,TeacherName) -- Avoid duplicate entries for same student/day
);

select * from attendance
DROP TABLE IF EXISTS attendance;
drop table attendance

alter table attendance add late_time TIME;

ALTER TABLE attendance
ADD late_time TIME NULL;
WITH WorkDays AS (
    SELECT COUNT(DISTINCT date) AS TotalWorking
    FROM attendance
    WHERE MONTH(date) = 9   -- 👈 Month (September)
      AND YEAR(date) = 2025 -- 👈 Year
)
SELECT 
    s.name1 AS Name,
    s.regno1 AS RegNo,
    w.TotalWorking,
    SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END) AS AbsentCount,
    (w.TotalWorking - SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END)) AS PresentCount
FROM student_reg_crt s
CROSS JOIN WorkDays w
LEFT JOIN attendance a 
       ON s.regno1 = a.regno1
      AND MONTH(a.date) = 9
      AND YEAR(a.date) = 2025
GROUP BY s.name1, s.regno1, w.TotalWorking
ORDER BY s.name1;



SELECT 
    s.name1 AS Name,
    s.regno1 AS regno
FROM student_reg_crt s
JOIN attendance a 
    ON s.regno1 = a.regno1
WHERE CONVERT(date, a.date) = ?  -- replace with your desired date
  AND a.status = 'Absent'
ORDER BY s.name1;

SELECT TOP 3 regno1, name1, COUNT(*) AS absent_days
FROM attendance
WHERE status = 'Absent'
GROUP BY regno1, name1
ORDER BY absent_days DESC;


