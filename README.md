# doto 鱼塘分队群用 qbot

框架采用 [mirai](https://github.com/mamoe/mirai) 以及 [Ariadne](https://github.com/GraiaProject/Ariadne)

## Features

```text
内置 模块:
- /help: 帮助指令
- /task: 任务指令
- /mods: 命令查询指令
- /on: 启用命令指令
- /off: 关闭命令指令
- /log: 日志查询指令

bili 模块:
- /dance: B站舞蹈区排行
- /recommend: td金牌推荐舞见视频
- /live: B站直播间开播订阅
- /rmlive: 取消订阅直播间
- /up: 订阅UP主投稿
- /rmup: 取消订阅UP主投稿

dota 模块:
- /dota: 展示最近24小时(上限10场)游戏数据
- /winrate: 最近胜率图展示
- /stat: 展示最近指定场数(默认20场)游戏平均数据
- /setdota: 设置用户对应的dota id
- /comp: 玩家间最近平均数据对比
- /wrcp: 玩家间最近胜率数据对比
- /star: 展示最近指定场数(默认20场)游戏五星图数据
- /stcp: 玩家间最近五星图对比
- /hero: 展示玩家英雄平均数据
- /story: dota战报展示
- /dotaupdate
- /rmdotaupdate

repeat 模块:
- 复读: bot拟人化, 实现人类的本质.

roll 模块:
- /roll: 按照所给参数roll点

user 模块:
- /setname: 设置昵称
- /name: 显示昵称
- /jrrp: 查询今日人品
```

## Change Logs

- 2022/12/04 v0.2.0
  整体迁移到 Graia/Ariadne

- 2021/12/11 v0.1.1
  新功能引入和多处改动，引入 poetry 管理依赖

- 2020/10/11 v0.1.0
  整体迁移到 Graia/Application

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
