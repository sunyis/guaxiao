# CheckTMDB
每日自动更新TMDB，themoviedb 国内可正常连接IP，解决DNS污染，供tinyMediaManager(TMM削刮器)、kodi削刮等正常削刮影片信息。
## 一、前景
自从我早两年使用了黑群NAS以后，下了好多的电影电视剧，发现电视端无法生成正常的海报墙。查找资料得知应该是 themoviedb.org、tmdb.org 数据库网站无法正常解析访问照成的，故依葫芦画瓢写了一个python脚本，每日定时通过[dnschecker](https://dnschecker.org/)查询出最佳IP，并自动同步到路由器外挂hosts，可正常削刮。

**本项目无需安装任何程序**

通过修改本地、路由器 hosts 文件，即可正常削刮影片信息。

## 文件地址
- tmdb hosts文件：`https://github.com/cnwikee/CheckTMDB/blob/main/Tmdb_host` ，[链接](https://github.com/cnwikee/CheckTMDB/blob/main/Tmdb_host)
- 合并 tmdb 和 Github 的hosts文件：`https://github.com/cnwikee/CheckTMDB/blob/main/Tmdb_Github_host` ，[链接](https://github.com/cnwikee/CheckTMDB/blob/main/Tmdb_Github_host)

## 二、使用方法

### 2.1 手动方式

#### 2.1.1 复制下面的内容

```bash
# Tmdb Hosts Start
3.167.212.33	themoviedb.org
3.167.212.111	www.themoviedb.org
18.154.132.87	auth.themoviedb.org
3.167.212.64	api.themoviedb.org
13.225.142.100	tmdb.org
3.167.192.104	api.tmdb.org
143.244.49.179	image.tmdb.org
18.154.130.110	thetvdb.com
3.167.194.87	api.thetvdb.com

# Update time: 2024-12-13T06:22:34+08:00
# Update url: https://github.com/cnwikee/CheckTMDB/blob/main/Tmdb_host
# Star me: https://github.com/cnwikee/CheckTMDB
# Tmdb Hosts End

```

该内容会自动定时更新， 数据更新时间：2024-12-13T06:22:34+08:00

#### 2.1.2 修改 hosts 文件

hosts 文件在每个系统的位置不一，详情如下：
- Windows 系统：`C:\Windows\System32\drivers\etc\hosts`
- Linux 系统：`/etc/hosts`
- Mac（苹果电脑）系统：`/etc/hosts`
- Android（安卓）系统：`/system/etc/hosts`
- iPhone（iOS）系统：`/etc/hosts`

修改方法，把第一步的内容复制到文本末尾：

1. Windows 使用记事本。
2. Linux、Mac 使用 Root 权限：`sudo vi /etc/hosts`。
3. iPhone、iPad 须越狱、Android 必须要 root。

#### 2.1.3 激活生效
大部分情况下是直接生效，如未生效可尝试下面的办法，刷新 DNS：

1. Windows：在 CMD 窗口输入：`ipconfig /flushdns`

2. Linux 命令：`sudo nscd restart`，如报错则须安装：`sudo apt install nscd` 或 `sudo /etc/init.d/nscd restart`

3. Mac 命令：`sudo killall -HUP mDNSResponder`

**Tips：** 上述方法无效可以尝试重启机器。

## 其他
- [x] 自学薄弱编程基础，大部分代码基于AI辅助生成，此项目过程中，主要人为解决的是：通过 [dnschecker](https://dnschecker.org/) 提交时，通过计算出正确的udp参数，获取正确的csrftoken，携带正确的referer提交！
- [x] README.md 及 部分代码 参考[GitHub520](https://github.com/521xueweihan/GitHub520)
- [x] * 本项目仅在本机测试通过，如有问题欢迎提 [issues](https://github.com/cnwikee/CheckTMDB/issues/new)
