DROP DATABASE IF EXISTS notebook_generator;
CREATE DATABASE notebook_generator;
USE notebook_generator;

CREATE TABLE series (
	`id` INT AUTO_INCREMENT PRIMARY KEY,
	`gse` VARCHAR(35) UNIQUE,
	`title` TEXT,
	`summary` TEXT,
	`date` DATETIME
);

CREATE TABLE platform (
	`id` INT AUTO_INCREMENT PRIMARY KEY,
	`gpl` VARCHAR(15) UNIQUE,
	`organism` VARCHAR(15)
);

CREATE TABLE sample (
	`id` INT AUTO_INCREMENT PRIMARY KEY,
	`gsm` VARCHAR(15),
	`sample_title` VARCHAR(255),
	`series_fk` INT,
	`platform_fk` INT,
	FOREIGN KEY (series_fk) REFERENCES series(id),
	FOREIGN KEY (platform_fk) REFERENCES platform(id)
);

CREATE TABLE sample_metadata (
	`id` INT AUTO_INCREMENT PRIMARY KEY,
	`variable` TEXT,
	`value` TEXT,
	`sample_fk` INT,
	FOREIGN KEY (sample_fk) REFERENCES sample(id)
);

CREATE TABLE section (
	`id` INT AUTO_INCREMENT PRIMARY KEY,
	`section_name` VARCHAR(255),
	`section_description` TEXT
);

CREATE TABLE tool (
	`id` INT AUTO_INCREMENT PRIMARY KEY,
	`tool_string` VARCHAR(255) UNIQUE,
	`tool_name` VARCHAR(255),
	`tool_description` TEXT,
	`introduction` TEXT,
	`methods` TEXT,
	`reference` TEXT,
	`reference_link` TEXT,
	`default_selected` BOOL,
	`requires_signature` BOOL,
	`input` VARCHAR(20),
	`section_fk` INT,
	FOREIGN KEY (section_fk) REFERENCES section(id)
);

CREATE TABLE parameter (
	`id` INT AUTO_INCREMENT PRIMARY KEY,
	`parameter_name` VARCHAR(255),
	`parameter_description` TEXT,
	`parameter_string` VARCHAR(255),
	`tool_fk` INT,
	FOREIGN KEY (tool_fk) REFERENCES tool(id)
);

CREATE TABLE parameter_value (
	`id` INT AUTO_INCREMENT PRIMARY KEY,
	`parameter_fk` INT,
	`value` VARCHAR(255),
	`type` ENUM('str', 'int', 'float'),
	`default` BOOL,
	FOREIGN KEY (parameter_fk) REFERENCES parameter(id)
);

CREATE TABLE core_scripts (
	`id` INT AUTO_INCREMENT PRIMARY KEY,
	`option_string` VARCHAR(255),
	`option_name` VARCHAR(255),
	`option_description` TEXT,
	`introduction` TEXT,
	`methods` TEXT,
	`reference` TEXT,
	`reference_link` TEXT
);

CREATE TABLE error_log (
	`id` INT AUTO_INCREMENT PRIMARY KEY,
	`gse` VARCHAR(20),
	`version` VARCHAR(10),
	`notebook_configuration` TEXT,
	`error_type` VARCHAR(20),
	`error` TEXT,
	`date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE notebooks (
	`id` INT AUTO_INCREMENT PRIMARY KEY,
	`notebook_uid` VARCHAR(30),
	`notebook_url` TEXT,
	`notebook_configuration` TEXT,
	`gse` VARCHAR(20),
	`version` VARCHAR(10)
);

CREATE TABLE user_dataset (
	`id` INT AUTO_INCREMENT PRIMARY KEY,
	`dataset_uid` VARCHAR(30),
	`dataset_type` VARCHAR(30),
	`status` VARCHAR(30),
	`date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_sample (
	`id` INT AUTO_INCREMENT PRIMARY KEY,
	`sample_name` VARCHAR(255),
	`user_dataset_fk` INT,
	FOREIGN KEY (user_dataset_fk) REFERENCES user_dataset(id)
);

CREATE TABLE user_sample_metadata (
	`id` INT AUTO_INCREMENT PRIMARY KEY,
	`variable` TEXT,
	`value` TEXT,
	`user_sample_fk` INT,
	FOREIGN KEY (user_sample_fk) REFERENCES user_sample(id)
);

CREATE TABLE ontology (
	`id` INT AUTO_INCREMENT PRIMARY KEY,
	`ontology_name` VARCHAR(50),
	`ontology_string` VARCHAR(50),
	`homepage_url` VARCHAR(100),
	`search_base_url` VARCHAR(100),
	`ontology_description` TEXT
);

CREATE TABLE ontology_term (
	`id` INT AUTO_INCREMENT PRIMARY KEY,
	`term_id` VARCHAR(30),
	`term_name` VARCHAR(250),
	`term_description` TEXT,
	`ontology_fk` INT,
	FOREIGN KEY (ontology_fk) REFERENCES ontology(id)
);

CREATE TABLE notebook_ontology_term (
	`id` INT AUTO_INCREMENT PRIMARY KEY,
	`notebook_fk` INT,
	`ontology_term_fk` INT,
	FOREIGN KEY (notebook_fk) REFERENCES notebook(id),
	FOREIGN KEY (ontology_term_fk) REFERENCES ontology_term(id)
);

CREATE TABLE fastq_upload (
	`id` INT AUTO_INCREMENT PRIMARY KEY,
	`upload_uid` VARCHAR(30) UNIQUE,
	`date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE fastq_file (
	`id` INT AUTO_INCREMENT PRIMARY KEY,
	`fastq_upload_fk` INT,
	`filename` TEXT,
	FOREIGN KEY (fastq_upload_fk) REFERENCES fastq_upload(id)
);

CREATE TABLE alignment (
	`id` INT AUTO_INCREMENT PRIMARY KEY,
	`alignment_uid` VARCHAR(30) UNIQUE
);