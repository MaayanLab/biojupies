CREATE TABLE IF NOT EXISTS `dataset_{version}` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dataset_accession` varchar(35) NOT NULL DEFAULT '',
  `dataset_title` text NOT NULL,
  `summary` text NOT NULL,
  `date` date NOT NULL,
  `dataset_type_fk` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accession` (`dataset_accession`),
  KEY `dataset_type_fk` (`dataset_type_fk`),
  CONSTRAINT `dataset_ibfk_1_{version}` FOREIGN KEY (`dataset_type_fk`) REFERENCES `dataset_type` (`id`)
);

CREATE TABLE IF NOT EXISTS `platform_{version}` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `platform_accession` varchar(15) NOT NULL,
  `organism` varchar(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `platform_accession` (`platform_accession`)
);

CREATE TABLE IF NOT EXISTS `sample_{version}` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sample_accession` varchar(15) NOT NULL,
  `sample_title` varchar(255) NOT NULL,
  `dataset_fk` int(11) NOT NULL,
  `platform_fk` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accession` (`sample_accession`,`platform_fk`,`dataset_fk`),
  KEY `dataset_fk` (`dataset_fk`),
  KEY `platform_fk` (`platform_fk`),
  CONSTRAINT `sample_{version}_ibfk_1` FOREIGN KEY (`dataset_fk`) REFERENCES `dataset_{version}` (`id`),
  CONSTRAINT `sample_{version}_ibfk_2` FOREIGN KEY (`platform_fk`) REFERENCES `platform_{version}` (`id`)
);

CREATE TABLE IF NOT EXISTS `sample_metadata_{version}` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `variable` text,
  `value` text,
  `sample_fk` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `sample_fk` (`sample_fk`),
  CONSTRAINT `sample_metadata_{version}_ibfk_1` FOREIGN KEY (`sample_fk`) REFERENCES `sample_{version}` (`id`)
);