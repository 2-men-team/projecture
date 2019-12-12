CREATE DATABASE IF NOT EXISTS Projecture;

USE Projecture;

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(25),
    email VARCHAR(25),
    password_hash VARCHAR(100),
    time_stamp TIMESTAMP DEFAULT current_timestamp()
);

CREATE TABLE projects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_name VARCHAR(100),
    posted_by INT,
    link VARCHAR(150),
    complexity INT,
    brief_description VARCHAR(300),
    description TEXT,
    post_time_stamp TIMESTAMP DEFAULT current_timestamp(),
    FOREIGN KEY (posted_by) REFERENCES users(id) ON DELETE NO ACTION
);

CREATE TABLE user_projects (
    project_id INT,
    user_id INT,
    PRIMARY KEY (project_id, user_id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE ,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE NO ACTION
);

CREATE TABLE tags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(25)
);

CREATE TABLE project_tags (
    project_id INT,
    tag_id INT,
    PRIMARY KEY (project_id, tag_id),
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);