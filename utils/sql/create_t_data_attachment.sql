CREATE TABLE IF NOT EXISTS `t_data_attachment` (
  `attachment_id` VARCHAR(20) NOT NULL COMMENT '附件ID',
  `data_id` VARCHAR(20) NOT NULL COMMENT '数据ID',
  `collection_id` VARCHAR(20) NOT NULL COMMENT '数据集ID',
  `question_file` BLOB COMMENT '问题附件',
  `created_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `created_by` VARCHAR(20) COMMENT '创建人',
  `updated_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `updated_by` VARCHAR(20) NOT NULL COMMENT '更新人',
  `del_flag` TINYINT UNSIGNED DEFAULT 0 COMMENT '删除标志位: 0未删除 1删除',
  PRIMARY KEY (`attachment_id`),
  CONSTRAINT `fk_attachment_data` FOREIGN KEY (`data_id`) 
    REFERENCES `t_data_collection_info` (`data_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_attachment_collection` FOREIGN KEY (`collection_id`) 
    REFERENCES `t_data_collections` (`collection_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据附件表';