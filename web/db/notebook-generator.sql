DROP DATABASE IF EXISTS `notebook-generator`;
CREATE DATABASE `notebook-generator` DEFAULT CHARACTER SET utf8;
USE `notebook-generator`;

CREATE TABLE user (
	`id` INT AUTO_INCREMENT PRIMARY KEY,
	`username` VARCHAR(30) UNIQUE NOT NULL
);

INSERT INTO user (username) VALUES
	('maayanlab');

CREATE TABLE notebook (
	`id` INT AUTO_INCREMENT PRIMARY KEY,
	`user_fk` INT NOT NULL,
	`name` VARCHAR(30) DEFAULT '',
	FOREIGN KEY (user_fk) REFERENCES user(id)
);

INSERT INTO notebook (user_fk, name) VALUES
	(1, 'Notebook 1'),
	(1, 'Notebook 2');
