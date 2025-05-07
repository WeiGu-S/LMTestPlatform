CREATE TABLE IF NOT EXISTS `t_test_attachment_snapshot` (
  `task_id` VARCHAR(20) NOT NULL COMMENT '任务ID',
  `data_id` VARCHAR(20) NOT NULL COMMENT '附件ID',
  `collection_id` VARCHAR(20) NOT NULL COMMENT '数据ID/数据集ID',
  `question_file` BLOB COMMENT '问题附件',
  `created_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `created_by` VARCHAR(20) COMMENT '创建人',
  `updated_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `updated_by` VARCHAR(20) COMMENT '更新人',
  `del_flag` TINYINT UNSIGNED DEFAULT 0 COMMENT '删除标志位(0未删除1删除)',
  PRIMARY KEY (`task_id`, `data_id`, `collection_id`) 
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据附件快照';