#!/bin/bash
BACK_UP='/data/backup/'
WORK_DIR='/data/gitclone/'
GITSERVER='git@localhost'
HOST='192.168.1.243'

mkdir -p $WORK_DIR
mkdir -p $BACK_UP

function emulation(){
cd  $WORK_DIR
if [ $# != 3 ];then
    echo "传入参数错误, sh $0 tag,tag_name,project_name"
    exit 2
fi

if [  ! -d $WORK_DIR$3 ];then
    git clone $gitserver:/$3.git >/dev/null 2>&1
    if [ $? -ne 0 ];then
        echo "git clone error!"; 
        exit 2
    fi
else 
    cd $WORK_DIR$3
fi

#备份代码
tar czf $BACK_UP$3.tar.gz  $BACK_UP$3

git pull >/dev/null 2>&1
if [ $? -ne 0 ];then
    echo "git pull error!"
    exit 2
fi

git tag -a $1 -m $2 >/dev/null 2>&1
git push origin $1  > /dev/null 2>&1
if [ $? -ne 0 ];then
    echo "git push tag error!"
    exit 2
fi

#rsync 推送代码
#    /usr/bin/rsync -avz  -e ssh  --exclude=.git --exclude=.svn --exclude=runtime  --include=assets/js --include=assets/css --include=assets/images --include=assets/wechat  --exclude=assets/*/  $WORK_DIR$3  root@$HOST:/data/wwwroot/$3/    #将项目目录的内容rsync到远程主机目录下

echo "finish"
}


function cancel(){
    if [ $# != 1 ];then
        echo "Usage sh $0 cancel project name"
        exit
    fi
    rm -rf $WORK_DIR$1
    tar zxf $BACK_UP$1.tar.gz -C $WORK_DIR
    if [ $? -ne 0 ]; then
        echo "tar $1.tar.gz error!"
        exit 2
    else
        echo "cancel finish"
    fi
}

#emulation  $1 $2 $3
#cancel $1


case $1 in
    cancel)
        cancel $2;
        ;;
    emulation)
        emulation $2 $3 $4
        ;;
    *)
        echo "Usage: sh $0 cancel project_name
       sh $0 emulation tag tag_infomation project_name
"
esac
