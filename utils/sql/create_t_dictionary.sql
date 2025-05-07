CREATE TABLE IF NOT EXISTS `t_dictionary` (
  `dic_id` VARCHAR(20) NOT NULL COMMENT '字典ID',
  `key` VARCHAR(50) NOT NULL COMMENT '字典键',
  `name` VARCHAR(50) NOT NULL COMMENT '字典值名称',
  `description` VARCHAR(500) COMMENT '描述信息',
  `parent_id` VARCHAR(20) COMMENT '父级字典ID',
  `sort_order` INT UNSIGNED DEFAULT 0 COMMENT '排序序号',
  `created_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `del_flag` TINYINT UNSIGNED DEFAULT 0 COMMENT '删除标志位(0未删除1删除)',
  PRIMARY KEY (`dic_id`),
  KEY `idx_key` (`key`),
  KEY `idx_parent` (`parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据字典表';