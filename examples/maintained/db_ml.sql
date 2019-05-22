DROP TABLE IF EXISTS `ml_data`;
CREATE TABLE IF NOT EXISTS `ml_data` (
  `src_url` VARCHAR(1000) PRIMARY KEY NOT NULL,
  `json` text
);
