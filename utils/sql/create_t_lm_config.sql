CREATE TABLE IF NOT EXISTS `t_lm_config` (
  `config_id` VARCHAR(20) NOT NULL COMMENT '配置ID',
  `model_name` VARCHAR(200) COMMENT '模型名称',
  `config_type` SMALLINT UNSIGNED COMMENT '配置用途(数据字典：被测模型、裁判模型等)',
  `model_type` SMALLINT UNSIGNED COMMENT '模型类型(数据字典：远程模型、本地模型等)',
  `url_info` VARCHAR(200) COMMENT 'URL信息',
  `key_info` VARCHAR(200) COMMENT 'APIKEY信息',
  `model_file` BLOB COMMENT '模型文件',
  `created_time` DATETIME COMMENT '创建时间',
  `created_by` VARCHAR(20) COMMENT '创建人',
  `updated_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `updated_by` VARCHAR(20) COMMENT '更新人',
  `del_flag` TINYINT UNSIGNED DEFAULT 0 COMMENT '删除标志位(0未删除1删除)',
  PRIMARY KEY (`config_id`),
  UNIQUE KEY (`config_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='大模型配置';