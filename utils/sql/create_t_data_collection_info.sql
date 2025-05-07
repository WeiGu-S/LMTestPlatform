CREATE TABLE IF NOT EXISTS `t_data_collection_info` (
  `data_id` VARCHAR(20) NOT NULL COMMENT '数据ID',
  `collection_id` VARCHAR(20) NOT NULL COMMENT '数据集ID',
  `data_type` SMALLINT UNSIGNED COMMENT '数据分类: 数据字典：文本、图片、音频、视频等',
  `context` TEXT COMMENT '上下文',
  `question` VARCHAR(500) COMMENT '问题',
  `answer` VARCHAR(500) COMMENT '答案',
  `question_type` SMALLINT UNSIGNED COMMENT '题型: 数据字典：选择题、判断题、问答题等',
  `question_label` SMALLINT UNSIGNED COMMENT '问题标签: 数据字典：数学、文字理解、Rag召回等',
  `created_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `created_by` VARCHAR(20) COMMENT '创建人',
  `updated_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `updated_by` VARCHAR(20) COMMENT '更新人',
  `del_flag` TINYINT UNSIGNED DEFAULT 0 COMMENT '删除标志位: 0未删除 1删除',
  PRIMARY KEY (`data_id`),
  CONSTRAINT `fk_collection_info` FOREIGN KEY (`collection_id`) 
    REFERENCES `t_data_collections` (`collection_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据信息表';