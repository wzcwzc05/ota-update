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
CREATE DATABASE IF NOT EXISTS `ota` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `ota`;

-- 导出  表 ota.otafiles 结构
CREATE TABLE IF NOT EXISTS `otafiles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `version` varchar(50) NOT NULL DEFAULT '0',
  `branch` varchar(50) NOT NULL DEFAULT '0',
  `content` json NOT NULL,
  `package` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `tag` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  ota.otafiles 的数据：~2 rows (大约)
DELETE FROM `otafiles`;
INSERT INTO `otafiles` (`id`, `version`, `branch`, `content`, `package`, `tag`) VALUES
	(1, '1.0.0', 'x86-major', '{}', 'test', 1),
	(2, '1.0.1', 'x86-major', '{}', 'test', 0);

-- 导出  表 ota.package 结构
CREATE TABLE IF NOT EXISTS `package` (
  `id` int NOT NULL AUTO_INCREMENT,
  `package` varchar(50) NOT NULL,
  `branch` varchar(50) NOT NULL,
  `version` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  ota.package 的数据：~0 rows (大约)
DELETE FROM `package`;
INSERT INTO `package` (`id`, `package`, `branch`, `version`) VALUES
	(1, 'test', 'release', '1.0.1');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
