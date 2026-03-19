use ak;
CREATE TABLE Users (
    user_id INT PRIMARY KEY IDENTITY,
    username VARCHAR(50) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('teacher','student','parent'))
);

CREATE TABLE Sessions (
    session_id INT PRIMARY KEY IDENTITY,
    user_id INT NOT NULL,
    login_time DATETIME DEFAULT GETDATE(),
    logout_time DATETIME NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
