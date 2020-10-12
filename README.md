# doto 鱼塘分队群用 qbot

框架采用 [mirai](https://github.com/mamoe/mirai) 以及 [python-mirai-v4(graia-application)](https://github.com/GraiaProject/Application)

### Features
```
/name: 显示昵称
/setname: 设置昵称
/jrrp: 查询今日人品
/roll: 按照所给参数roll点

/setdota: 设置用户对应的dota id
/dota: 展示最近24小时(上限10场)游戏数据
/comp: 玩家间最近平均数据对比
/winrate: 最近胜率图展示
/wrcp: 玩家间最近胜率数据对比
/star: 展示最近指定场数(默认20场)游戏五星图数据
/stat: 展示最近指定场数(默认20场)游戏平均数据
/stcp: 玩家间最近五星图对比
/dotanews /rmdotanews: 订阅/取消订阅DOTA2更新

/dance: B站舞蹈区排行
/recommend: td金牌推荐舞见视频
/live /rmlive: 订阅/取消订阅B站直播间开播信息
/up /rmup: 订阅/取消订阅UP主投稿

/task: 显示订阅任务列表
/help: 帮助指令
/log: Bot日志展示
```

### Change Logs
- 2020/10/11 v0.1.0
  整体迁移到 python-mirai-v4

- 2020/09/12 v0.0.5
  添加指令注释机制，订阅机制，缓存机制，底层命令处理优化为消息队列，以及dota更新订阅功能

- 2020/09/06 v0.0.4
  添加 dota 五星图等一系列数据对比指令，对项目结构以及部署进行优化

- 2020/08/13 v0.0.3
  添加B站直播监控，B站舞蹈推荐，今日人品，账户绑定角色等功能 同时优化指令处理逻辑

- 2020/08/10 v0.0.2
  各功能逻辑优化 添加 dota 胜率，日志功能

- 2020/08/09 v0.0.1
  基础版本 并支持 Github Actions 自动部署
