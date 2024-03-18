-- --------------------------------------------------------
-- 主机:                           127.0.0.1
-- 服务器版本:                        8.2.0 - MySQL Community Server - GPL
-- 服务器操作系统:                      Win64
-- HeidiSQL 版本:                  12.6.0.6765
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- 导出 ota 的数据库结构
CREATE DATABASE IF NOT EXISTS `ota`;
USE `ota`;

-- 导出  表 ota.ota 结构
DROP TABLE IF EXISTS `ota`;
CREATE TABLE IF NOT EXISTS `ota` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `version` varchar(100) NOT NULL,
  `branch` varchar(100) NOT NULL,
  `content` json NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;

-- 正在导出表  ota.ota 的数据：~2 rows (大约)
DELETE FROM `ota`;
INSERT INTO `ota` (`id`, `name`, `version`, `branch`, `content`) VALUES
	(3, 'test', '0.0.1', 'major', '{"local": "./test", "branch": "major", "remote": "http://localhost:3000/", "sha256": "c733d0d6fc33e8a34533d8358ee706c2b6c67be5beeaad6fab3c98dfb66537a7", "package": "test", "restore": "", "version": "0.0.1", "AfterUpdate": "", "description": "test package", "BeforeUpdate": "", "dependencies": {"test": "0.0.1"}}'),
	(4, 'test', '0.0.2', 'major', '{"local": "./test", "branch": "major", "remote": "http://localhost:3000/", "sha256": "c733d0d6fc33e8a34533d8358ee706c2b6c67be5beeaad6fab3c98dfb66537a7", "package": "test", "restore": "", "version": "0.0.2", "AfterUpdate": "", "description": "test package", "BeforeUpdate": "", "dependencies": {"test": "0.0.1"}}');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
