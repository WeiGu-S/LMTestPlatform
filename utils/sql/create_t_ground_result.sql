CREATE TABLE IF NOT EXISTS `t_ground_result` (
  `round_id` VARCHAR(20) NOT NULL COMMENT '轮次ID',
  `task_id` VARCHAR(20) NOT NULL COMMENT '任务ID',
  `data_id` VARCHAR(20) NOT NULL COMMENT '数据ID',
  `collection_id` VARCHAR(20) NOT NULL COMMENT '数据集ID',
  `lm_answer` VARCHAR(500) COMMENT '大模型答案',
  `data_result` FLOAT COMMENT '评分',
  `created_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `created_by` VARCHAR(20) COMMENT '创建人',
  `updated_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `updated_by` VARCHAR(20) COMMENT '更新人',
  `del_flag` TINYINT UNSIGNED DEFAULT 0 COMMENT '删除标志位(0未删除1删除)',
  PRIMARY KEY (`round_id`, `task_id`, `data_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='测试数据结果表';