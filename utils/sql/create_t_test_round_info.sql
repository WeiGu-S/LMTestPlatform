CREATE TABLE IF NOT EXISTS `t_test_round_info` (
  `round_id` VARCHAR(20) NOT NULL COMMENT '轮次ID',
  `task_id` VARCHAR(20) NOT NULL COMMENT '任务ID',
  `task_status` ENUM('待测评','测评中','已测评') COMMENT '任务状态',
  `task_result` FLOAT COMMENT '任务得分',
  `created_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `created_by` VARCHAR(20) COMMENT '创建人',
  `updated_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `updated_by` VARCHAR(20) COMMENT '更新人',
  `del_flag` TINYINT UNSIGNED DEFAULT 0 COMMENT '删除标志位(0未删除1删除)',
  PRIMARY KEY (`round_id`),
  KEY `idx_task_id` (`task_id`),
  FOREIGN KEY (`task_id`) REFERENCES t_test_task_info(`task_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='测试轮次表';