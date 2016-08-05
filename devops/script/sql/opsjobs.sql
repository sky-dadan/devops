-- MySQL dump 10.13  Distrib 5.1.73, for redhat-linux-gnu (x86_64)
--
-- Host: localhost    Database: devops
-- ------------------------------------------------------
-- Server version	5.1.73

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ops_jobs`
--

DROP TABLE IF EXISTS `ops_jobs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ops_jobs` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `apply_date` datetime NOT NULL COMMENT 'åˆ›å»ºæ—¶é—´',
  `apply_type` tinyint(3) unsigned NOT NULL COMMENT 'å·¥å•ç”³è¯·ç±»åž‹',
  `apply_desc` text NOT NULL COMMENT 'å·¥å•ç”³è¯·æè¿°',
  `deal_persion` varchar(20) DEFAULT NULL COMMENT 'å·¥å•å¤„ç†äºº',
  `status` tinyint(3) NOT NULL COMMENT 'å·¥å•å¤„ç†è¿‡ç¨‹çš„çŠ¶æ€',
  `deal_desc` text COMMENT 'å¤„ç†æè¿°',
  `deal_time` datetime DEFAULT NULL COMMENT 'å¤„ç†å®Œæˆæ—¶é—´',
  `apply_persion` varchar(20) NOT NULL COMMENT 'å·¥å•ç”³è¯·äºº',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=86 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

