-- MySQL dump 10.13  Distrib 5.1.73, for redhat-linux-gnu (x86_64)
--
-- Host: localhost    Database: dev
-- ------------------------------------------------------
-- Server version	5.1.73

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES latin1 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

CREATE DATABASE IF NOT EXISTS `devops`;
USE `devops`;
SET NAMES utf8;

--
-- Table structure for table `cabinet`
--

DROP TABLE IF EXISTS `cabinet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cabinet` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL COMMENT '机柜名',
  `idc_id` int(10) NOT NULL COMMENT '对应的机房ID',
  `u_num` int(10) DEFAULT NULL COMMENT 'U位数量',
  `power` varchar(32) DEFAULT NULL COMMENT '机柜电源功率',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host`
--

DROP TABLE IF EXISTS `host`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `hostname` varchar(32) NOT NULL COMMENT '主机名',
  `sn` varchar(32) DEFAULT NULL COMMENT '序列号',
  `host_no` varchar(10) DEFAULT NULL COMMENT '主机编号，eg:H-0001',
  `inner_ip` varchar(32) DEFAULT NULL COMMENT '内网IP',
  `mac_address` varchar(32) DEFAULT NULL COMMENT '内网mac地址',
  `wan_ip` varchar(32) DEFAULT NULL COMMENT '外网IP',
  `remote_ip` varchar(32) DEFAULT NULL COMMENT '远程控制卡ip',
  `os_info` varchar(32) DEFAULT NULL COMMENT '系统信息,eg：centos6.5',
  `cpu_num` int(10) DEFAULT NULL COMMENT 'cpu核数',
  `disk_num` varchar(20) DEFAULT NULL COMMENT '磁盘大小',
  `mem_num` varchar(10) DEFAULT NULL COMMENT '内存大小',
  `host_type` varchar(32) DEFAULT NULL COMMENT '服务器类型，eg：dellR30',
  `manufacturer_id` int(10) DEFAULT NULL COMMENT '生产商id',
  `supplier_id` int(10) DEFAULT NULL COMMENT '供应商id',
  `store_date` date DEFAULT NULL COMMENT '入库时间',
  `expire` date DEFAULT NULL COMMENT '质保时间',
  `idc_id` int(10) DEFAULT NULL COMMENT '机房ID',
  `cabinet_id` int(10) DEFAULT NULL COMMENT '机柜ID',
  `service_id` int(10) DEFAULT NULL COMMENT '所属服务ID',
  `status` int(10) DEFAULT NULL COMMENT '0在线，1不在线',
  `vm_status` int(10) DEFAULT NULL COMMENT '0虚拟机，1不是虚拟机',
  `remark` varchar(50) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`id`),
  UNIQUE KEY `hostname` (`hostname`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idc`
--

DROP TABLE IF EXISTS `idc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idc` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `idc_name` varchar(32) NOT NULL COMMENT '机房名简称',
  `name` varchar(32) NOT NULL COMMENT '机房全称',
  `address` varchar(64) DEFAULT NULL COMMENT '机房地址',
  `email` varchar(32) DEFAULT NULL COMMENT '机房邮件',
  `interface_user` varchar(32) DEFAULT NULL COMMENT '机房接口人',
  `user_phone` varchar(32) DEFAULT NULL COMMENT '接口人电话',
  `pact_cabinet_num` int(10) DEFAULT NULL COMMENT '合约机柜数',
  `rel_cabinet_num` int(10) DEFAULT NULL COMMENT '实际分配机柜数',
  `remark` varchar(64) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idc_name` (`idc_name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `manufacturer`
--

DROP TABLE IF EXISTS `manufacturer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `manufacturer` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL COMMENT '生产厂商',
  `supplier_name` varchar(32) NOT NULL COMMENT '供应商',
  `interface_user` varchar(32) DEFAULT NULL COMMENT '供应商接口人',
  `email` varchar(32) DEFAULT NULL COMMENT '接口人邮箱',
  `user_phone` varchar(32) DEFAULT NULL COMMENT '接口人电话',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `service`
--

DROP TABLE IF EXISTS `service`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `service` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL COMMENT '服务名eg:商城php，前端nginx',
  `dev_interface` varchar(50) DEFAULT NULL COMMENT '开发接口人',
  `sa_interface` varchar(50) DEFAULT NULL COMMENT '运维接口人',
  `remark` varchar(50) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `soft_asset`
--

DROP TABLE IF EXISTS `soft_asset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `soft_asset` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `type` varchar(64) NOT NULL COMMENT '资产类型,eg：dns',
  `manufacturer` varchar(40) DEFAULT NULL COMMENT '服务商',
  `store_date` date DEFAULT NULL COMMENT '采购时间',
  `expire` date DEFAULT NULL COMMENT '有效时间',
  `remark` varchar(128) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `switch`
--

DROP TABLE IF EXISTS `switch`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `switch` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL COMMENT '网络设备名',
  `ip` varchar(32) DEFAULT NULL COMMENT 'ip地址',
  `type` varchar(32) DEFAULT NULL COMMENT '网络设备类型，eg:二层交换机',
  `manufacturer_id` int(10) DEFAULT NULL COMMENT '生产商id',
  `supplier_id` int(10) DEFAULT NULL COMMENT '供应商id',
  `idc_id` int(10) DEFAULT NULL COMMENT '机房ID',
  `cabinet_id` int(10) DEFAULT NULL COMMENT '机柜ID',
  `port_num` int(10) DEFAULT NULL COMMENT '端口数量',
  `status` int(10) DEFAULT NULL COMMENT '0正常，1未使用',
  `store_date` date DEFAULT NULL COMMENT '采购时间',
  `expire` date DEFAULT NULL COMMENT '有效时间',
  `remark` varchar(50) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_group`
--

DROP TABLE IF EXISTS `user_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_group` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL COMMENT '用户组英文名',
  `name_cn` varchar(80) NOT NULL COMMENT '用户组中文名',
  `p_id` varchar(32) NOT NULL COMMENT '权限列表',
  `comment` varchar(50) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `permission`
--

DROP TABLE IF EXISTS `permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `permission` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(40) NOT NULL COMMENT '权限英文名',
  `name_cn` varchar(30) NOT NULL COMMENT '权限中文名',
  `url` varchar(128) NOT NULL COMMENT '权限对应URL',
  `comment` varchar(128) NOT NULL COMMENT '备注',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `project`
--

DROP TABLE IF EXISTS `project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL COMMENT '项目名',
  `path` varchar(80) NOT NULL COMMENT '项目代码仓库路径',
  `principal` int(10) unsigned NOT NULL COMMENT '负责人',
  `tag` varchar(30) DEFAULT '关联标签',
  `create_date` date NOT NULL COMMENT '创建时间',
  `is_lock` tinyint(1) unsigned DEFAULT '0' COMMENT '是否锁定 0-未锁定 1-锁定',
  `comment` varchar(256) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `project_perm`
--

DROP TABLE IF EXISTS `project_perm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project_perm` (
  `id` int(10) unsigned NOT NULL COMMENT '项目id',
  `user_all_perm` varchar(80) DEFAULT '' COMMENT '全部权限的用户列表',
  `group_all_perm` varchar(80) DEFAULT '' COMMENT '全部权限的用户组列表',
  `user_rw_perm` varchar(80) DEFAULT '' COMMENT '读写权限的用户列表',
  `group_rw_perm` varchar(80) DEFAULT '' COMMENT '读写权限的用户组列表',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `project_test`
--

DROP TABLE IF EXISTS `project_test`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project_test` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `project_id` int(10) NOT NULL COMMENT '对应project项目ID',
  `host` varchar(64) NOT NULL COMMENT '测试主机',
  `commit` varchar(64) NOT NULL COMMENT '推送版本号',
  `pusher` varchar(128) NOT NULL COMMENT '推送人',
  `push_date` datetime NOT NULL COMMENT '推送时间',
  `comment` varchar(256) COMMENT '备注',
  PRIMARY KEY (`id`),
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `project_apply`
--

DROP TABLE IF EXISTS `project_apply`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project_apply` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `project_id` int(10) NOT NULL COMMENT '对应project项目ID',
  `info` varchar(64) NOT NULL COMMENT '发布简介',
  `applicant` varchar(64) NOT NULL COMMENT '申请人',
  `version` varchar(64) DEFAULT NULL COMMENT '发布版本',
  `commit` varchar(64) NOT NULL COMMENT '代码最新版本',
  `apply_date` datetime NOT NULL COMMENT '申请时间',
  `status` int(10) DEFAULT 0 COMMENT '发布状态',
  `detail` text COMMENT '发布详情',
  PRIMARY KEY (`id`),
  UNIQUE KEY `project_id` (`project_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `project_deploy`
--

DROP TABLE IF EXISTS `project_deploy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project_deploy` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `project_id` int(10) NOT NULL COMMENT '对应project的项目ID',
  `info` varchar(64) NOT NULL COMMENT '发布简介',
  `version` varchar(64) DEFAULT NULL COMMENT '发布版本',
  `commit` varchar(64) NOT NULL COMMENT '代码最新版本',
  `applicant` varchar(64) NOT NULL COMMENT '操作人',
  `apply_date` datetime NOT NULL COMMENT '操作时间',
  `status` int(10) DEFAULT 0 COMMENT '发布状态',
  `detail` text COMMENT '发布详情',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(40) NOT NULL COMMENT '用户名',
  `password` varchar(64) NOT NULL COMMENT '密码',
  `name` varchar(80) NOT NULL COMMENT '姓名',
  `email` varchar(64) NOT NULL COMMENT '公司邮箱',
  `mobile` varchar(16) DEFAULT NULL COMMENT '手机号',
  `role` tinyint(3) unsigned DEFAULT 1 COMMENT '用户类型 0-管理员 1-普通用户',
  `r_id` varchar(30) DEFAULT NULL COMMENT '所属组列表',
  `is_lock` tinyint(1) unsigned DEFAULT 0 COMMENT '是否锁定 0-未锁定 1-锁定',
  `join_date` datetime DEFAULT NULL COMMENT '注册时间',
  `last_login` datetime DEFAULT NULL COMMENT '最后登录时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

INSERT INTO user (username, password, name, email, role, join_date) VALUES ('admin', 'e10adc3949ba59abbe56e057f20f883e', '管理员', 'yuanxin@yuanxin-inc.com', 0, NOW());
INSERT INTO permission (name, name_cn, url, comment) VALUES ('git', 'Git仓库管理', '/git/list', '');

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-03-08 17:52:32
