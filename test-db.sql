CREATE DATABASE IF NOT EXISTS `dffml_source` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `dffml_source`;

DROP TABLE IF EXISTS `repo_data`;

SET character_set_client = utf8mb4 ;

CREATE TABLE `repo_data` (
  `src_url` varchar(100) NOT NULL,
  `feature_PetalLength` float DEFAULT NULL,
  `feature_PetalWidth` float DEFAULT NULL,
  `feature_SepalLength` float DEFAULT NULL,
  `feature_SepalWidth` float DEFAULT NULL,
  `prediction_confidence` float DEFAULT NULL,
  `prediction_value` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`src_url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8;


LOCK TABLES `repo_data` WRITE;

INSERT INTO `repo_data` VALUES ('\'0\'',3.9,1.2,5.8,2.7,0.42,'\'feedface\''),('\'1\'',3.9,1.2,5.8,2.7,0,'\'\'');

UNLOCK TABLES;

