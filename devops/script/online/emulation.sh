#!/bin/bash
#####################################################################################
#脚本提供三个功能
#仿真发布: Usage   sh $0 emulation tag commit project_name
#取消    : Usage   sh $0 cancel  cancel_flag project_name
#正式发布: Usage   sh $0 product project_name
#申请发布: Usage   sh $0 apply   project_name
#####################################################################################

BACK_UP='/data/backup/'
WORK_DIR='/data/gitclone/'

mkdir -p $WORK_DIR
mkdir -p $BACK_UP

function emulation(){
    if [ $# != 3 ];then
        echo "传入参数错误, sh $0 emulation tag,commit,project_name"
        exit 2
    fi
    cd $WORK_DIR$3
    git tag -a $1  $2 -m  $1 >/dev/null 2>&1
    git push origin $1  > /dev/null 2>&1
    if [ $? -ne 0 ];then
        echo "ERROR: 标示版本失败!"
        exit 2
    fi
    
    #通过ssh执行sa上面的脚本 备份sa代码
    /usr/local/sbin/sa_online.sh sa_backup $2 $3

    #rsync 推送代码到灰度
    /usr/bin/rsync -avz $WORK_DIR$3/ /data/wwwroot/$3/
    #/usr/bin/rsync -avz  -e ssh  --exclude=.git --exclude=.svn --exclude=runtime  --include=assets/js --include=assets/css --include=assets/images --include=assets/wechat  --exclude=assets/*/  /data/wwwroot/$3  root@$HOST:/data/wwwroot/$3/    #将项目目录的内容rsync到远程主机目录下
    if [ $? -ne 0 ];then
        echo "ERROR: 仿真环境发布失败!"
        exit 2
    fi

    echo "OK: 仿真环境发布成功!"
}


function cancel(){
    if [ $# != 3 ];then
        echo "Usage sh $0 cancel tag project_name"
        exit
    fi
    if [ $1 -eq 1 ];then
        echo "OK: 取消仿真发布成功"
    elif [ $1 -eq 2 ];then
        cd  $WORK_DIR$3 
        git push origin --delete tag $2
        # ssh root@sa -e "sh script_name status project_name"   sa服务器将代码恢复到上一个版本
        if [ $? -ne 0 ];then
            echo "ERROR: 取消版本失败!"
            exit 2
        fi
        /usr/local/sbin/sa_online.sh sa_cancel $1 $3
        echo "OK: 取消正式发布成功"
    else
        echo "ERROR: 未知发布状态，取消发布失败"
    fi

}

function product(){
    #ssh root@sa -e "sh script_name project_name"    远程调用sa上面的上线脚本   
    #/usr/local/sbin/code.sh $1
    echo "OK: 取消正式发布成功"
}


function apply(){
    if  [ $# != 1 ];then
        echo -e  "\033[31musage:\n sh apply.sh project-name \033[0m"
        echo "ERROR: 调用脚本错误"
        exit  2
    fi
    cd /data/gitclone
    if [ ! -d $1 ]; then
        git clone  git@127.0.0.1:$1 &>/dev/null
    fi
     
    cd $1
    git pull > /dev/null 2>&1
    if [ $? -ne 0 ];then
        echo "ERROR: 更新项目失败"
        exit 1
    fi
    commit=`git log  --oneline -1 --pretty=format:"%h"`
    echo "OK: $commit"
}

case $1 in
    cancel)
        cancel $2 $3 $4;          #$2=cancel_flag  $3=tag  $4=project_name
        ;;
    emulation)
        emulation $2 $3 $4;       #$2=tag $3=commit  $4=project_name
        ;;
    product)
        product $2;
        ;;
    apply)
        apply $2;                 #$2=project_name
        ;;
    *)
        echo "Usage: sh $0 cancel cancel_flag tag project_name
       sh $0 emulation tag commit project_name  
       sh $0 product project_name
       sh $0 apply project_name
"
esac
