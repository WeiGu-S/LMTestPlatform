# LMTestPlatform

基于PySide6的大模型测试工具平台

## 项目描述

这是一个用于大模型测试的桌面应用程序，提供数据收集、管理和分析功能。主要用于评估和比较不同大语言模型的性能表现。

## 功能特性

- 数据收集管理（已实现）
- 测试结果分析（待实现）
- 数据导入导出
- 多窗口交互界面

## 安装指南

1. 确保已安装Python 3.8+ 
2. 安装依赖：
```bash
pip install -r requirements.txt
```
3. 配置数据库连接信息（config/database.ini）
``` 数据库启动后，会自动创建数据库并根据 utils/sql 目录下的 sql 文件建表
    如有新增表，可在 utils/sql 目录下新增 sql 文件，文件名格式为：create_xxx.sql，并在 utils/databases.py 中添加对应的建表文件名
```
## 使用说明

1. 运行主程序
```bash
python app.py
```
2. 通过GUI界面进行各项操作

3. 开发模式
```bash
python utils/debug_runner.py
``` 
utils/debug_runner.py可实时监控文件变化，方便开发调试
```