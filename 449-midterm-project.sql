CREATE TABLE IF NOT EXISTS `accounts` (
`id` int NOT NULL AUTO_INCREMENT,
`username` varchar(50) NOT NULL,
`password` varchar(255) NOT NULL,
`email` varchar(100) NOT NULL, PRIMARY KEY (`id`)
) ENGINE=InnODB AUTO_INCREMENT=1;