#!/bin/bash

###################################################
#功能： 执行脚本时传入 项目名和同步主机IP，会拉取 #
#最新的git版本 并rysnc到指定的主机                #
#操作方法：./online 项目名 同步目标主机ip         #
#作者：liuziping                                  #
#时间：2015-06-03                                 #
#备注: 执行需要root用户                           #
##################################################

if [ $# != 2 ];then    #执行输入不正确会提示
   echo "执行方法 ./online.sh  project_name host"
   exit
fi

cd /data/gitclone_dev   
if  [ ! -d $1 ];then    #判断gitclone中项目是否存在，不存在就gitclone一份，如果存在了，就直接git pull
    git clone -b dev http://192.168.1.251:8000/git/$1 &>/dev/null
    cd /data/gitclone_dev/$1
    git pull &>/dev/null
    commit=$(git log  --oneline -1 --pretty=format:"%h")
    info=$(git log --oneline -1 --pretty=format:"%s")
    echo $commit,$info
#    chown www:www -R /data/gitclone_dev/$1
#    /usr/bin/rsync -avz --timeout=20  -e ssh  --exclude=.git --exclude=.svn   /data/gitclone_dev/$1 root@$2:/data/wwwroot/    #将新项目整个目录rsync到远程主机目录
else
    cd /data/gitclone_dev/$1  
    git pull &>/dev/null
#    chown www:www -R /data/gitclone_dev/$1 
    commit=$(git log  --oneline -1 --pretty=format:"%h")
    info=$(git log --oneline -1 --pretty=format:"%s")
    echo $commit,$info
#    /usr/bin/rsync -avz  -e ssh  --exclude=.git --exclude=.svn --exclude=runtime  --include=assets/js --include=assets/css --include=assets/images --include=assets/wechat  --exclude=assets/*/  /data/gitclone_dev/$1/ root@$2:/data/wwwroot/$1/    #将项目目录的内容rsync到远程主机目录下

fi    