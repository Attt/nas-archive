 # Installation
 
 to determine which `PUID` and `PGID` to use, execute `id {username}` in shell

 ## nas-tools
 ```bash
 sudo docker run -d \
	--name=nastools \
	-e PUID=1000 \
	-e PGID=1000 \
	-e UMASK=022 \
	-e TZ=Asia/Shanghai \
	-e NASTOOL_AUTO_UPDATE=true \
	-e http_proxy=http://192.168.0.101:7890 \
	-e all_proxy=http://192.168.0.101:7890 \
	-p 3000:3000 \
	-v /home/attt/docker/nastools/config:/config \
	-v /mnt/sdc/nas/media:/media \
	--restart unless-stopped jxxghp/nas-tools:latest
 ```

 ## flaresolverr
 ```bash
 sudo docker run -d \
	--name=flaresolverr \
	-p 8191:8191 \
	-e LOG_LEVEL=info \
	-e http_proxy=http://192.168.0.101:7890 \
	-e all_proxy=http://192.168.0.101:7890 \
	--restart unless-stopped flaresolverr/flaresolverr:latest
 ```


 ## jellyfin-nyanmisaka
 ```bash
 sudo docker run -d \
	--name=jellyfin-nyanmisaka \
	-p 8096:8096 \
	-v /home/attt/docker/jellyfin-nyanmisaka/config:/config \
	-v /mnt/sdc/nas/media/jellyfin:/media \
	-e PUID=1000 \
	-e PGID=1000 \
	-e UMASK=022 \
	-e http_proxy=http://192.168.0.101:7890 \
	-e all_proxy=http://192.168.0.101:7890 \
	--restart unless-stopped nyanmisaka/jellyfin:latest
 ```

 ## jackeet
 ```bash
 sudo docker run -d \
	--name=jackett \
	-e PUID=1000 \
	-e PGID=1000 \
	-e TZ=Asia/Shanghai \
	-p 9117:9117 \
	-v /home/attt/docker/jackett/config:/config \
	--restart unless-stopped linuxserver/jackett:latest
 ```

 ## chinesesubfinder
 ```bash
 sudo docker run -d \
	-v /home/attt/docker/chinesesubfinder/config:/config   `# 冒号左边请修改为你想在主机上保存配置、日志等文件的路径`   \
	-v /mnt/sdc/nas/media:/media     `# 请修改为需要下载字幕的媒体目录，冒号右边可以改成你方便记忆的目录，多个媒体目录需要添\加多个-v映射`    \
	-v /mnt/sdc/nas/browser:/root/.cache/rod/browser `# 容器重启后无需再次下载 chrome，除非 go-rod 更新`    \
	-e PUID=1000    \
	-e PGID=1000    \
	-e PERMS=true       `# 是否重设/media权限`    \
	-e TZ=Asia/Shanghai `# 时区`    \
	-e UMASK=022        `# 权限掩码`    \
	-p 19035:19035 `# 从0.20.0版本开始，通过webui来设置`    \
	-p 19037:19037 `# webui 的视频列表读取图片用，务必设置不要暴露到外网`    \
	--name chinesesubfinder    \
	--hostname chinesesubfinder    \
	--log-driver "json-file"    \
	--log-opt "max-size=100m" `# 限制docker控制台日志大小，可自行调整`     allanpk716/chinesesubfinder
 ```

# Configuration
## nas-tools

```text
user: admin
pass: password
```

目录关系：

`本地的媒体目录是：/media，在nas-tool里面下载器的目录是 /media/downloads，jellyfin的目录是 /media/jellyfin`

- 代理
基础设置-代理服务器

- TMDB的key
基础设置-媒体-TMDB API key

- 勾选生成NFO
基础设置-媒体-生成NFO

- 下载软件监控开启
基础设置-服务-下载软件监控

- 扫描非nas-tools的内容
基础设置-服务-只管理nas-tool去掉

- TMDB缓存过期
基础设置-实验室-TMDB缓存过期策略

- 媒体库
设置jellyfin的目录

- 目录同步
开了下载监控，这个可以不开

- 消息 optional

- 索引器
配置一下jackeet

- 下载器
配置一下qbittorrent

- 媒体服务器
配置一下jellyfin

- 字幕
配置一下chinesesubfinder

## jellyfin
```text
user：root
pass：无
```
## chinesesubfinder
```text
user：attt
pass：123456
```
 

 
