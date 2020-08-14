# doto鱼塘分队群用qbot

框架采用mirai以及python-mirai

### Features
- 指令列表/help
- 账户绑定系统 /name /setname 今日人品查询/jrrp
- dota 24小时战绩查看 /dota /setdota 胜率变化曲线 /winrate 最近20场平均数据/stat 战绩比较/comp
- 复读机,支持多类型消息
- 跑团roll点 /roll
- Actions自动部署 包括dev分支测试和master分支部署
- 调试日志功能 /log
- bilibili直播监控 /live /rmlive 舞蹈推荐/dance /recommend

### Todo
- 每日风水(ddl)
- 新功能？

### Change Logs
- 2020/08/13 v0.0.3
  添加B站直播监控，B站舞蹈推荐，今日人品，账户绑定角色等功能 同时优化指令处理逻辑

- 2020/08/10 v0.0.2 
  各功能逻辑优化 添加dota胜率，日志功能

- 2020/08/09 v0.0.1 
  基础版本 并支持Github Actions自动部署