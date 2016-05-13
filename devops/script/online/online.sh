#!/bin/bash
#####################################################################################
#脚本提供四个功能
#申请发布: Usage   sh $0 apply   project_name
#仿真发布: Usage   sh $0 emulation tag commit project_name
#取消    : Usage   sh $0 cancel  cancel_flag project_name
#正式发布: Usage   sh $0 product project_name
#####################################################################################

CLONE_DIR='/data/gitclone/'
BACK_UP='/data/backup/'
WORK_DIR='/data/wwwroot/'

mkdir -p $CLONE_DIR
mkdir -p $BACK_UP
mkdir -p $WORK_DIR

#申请发布
function apply(){
    if  [ $# != 1 ];then
        echo -e  "\033[31musage:\n sh $0  apply project-name \033[0m"
        echo "ERROR: 调用脚本错误"
        exit  2
    fi
    #如果项目不存在，则clone下来
    cd $CLONE_DIR
    if [ ! -d $1 ]; then
        git clone  git@127.0.0.1:$1
    fi
     
    #拉取最新的代码，并记录commit
    cd $1
    git pull
    if [ $? -ne 0 ];then
        echo "ERROR: 更新项目失败"
        exit 1
    fi
    chown -R www:www $CLONE_DIR$1
    commit=`git log  --oneline -1 --pretty=format:"%h"`
    echo "OK: $commit"
}

#灰度发布
function emulation(){
    if [ $# != 3 ];then
        echo "传入参数错误, sh $0 emulation tag,commit,project_name"
        exit 2
    fi

    #拉取最新的git代码
    cd   $CLONE_DIR$3  
    git tag -a $1  $2 -m  $1
    if [ $? -ne 0 ];then
        echo "ERROR: 标示本地版本失败!"
        exit 2
    fi
    git push origin $1
    if [ $? -ne 0 ];then
        echo "ERROR: 标示的版本失败!"
        exit 2
    fi
    
    #备份原来$WORK_DIR的数据到$BACK_UP对应的项目目录下
    mkdir -p $WORK_DIR$3
    mkdir -p $BACK_UP$3
    tar zcf $BACK_UP$3/$2.tar.gz -C $WORK_DIR $3
    if [ $? -ne 0 ];then
        echo "ERROR: 备份代码失败!"
        exit 2
    fi

    #将$CLONE_DIR里面的代码rsync到$WORK_DIR下面
    /usr/bin/rsync -avz    --exclude=.git  --include=assets/js --include=assets/css --include=assets/images --include=assets/wechat  --exclude=assets/*/  $CLONE_DIR$3/ $WORK_DIR$3 
    if [ $? -ne 0 ];then
        echo "ERROR: 仿真环境同步失败!"
        exit 2
    fi


    #将$WORK_DIR下面的项目通过ansible批量推送到目标服务器
    ansible  test1:test2  -a  "mkdir -p /data/wwwroot/$3"
    ansible test1:test2  -m synchronize -a "src=/data/wwwroot/$3/ dest=/data/wwwroot/$3/ compress=yes"
    echo "OK: 仿真环境发布成功!"

}

#取消发布
function cancel(){
    if [ $# -lt 2 ];then
        echo "Usage sh $0 cancel status project_name [tag]"
        exit
    fi
    if [ $1 -eq 1 ];then
        #如果是没有经过灰度，点击取消，则什么都不需要操作
        echo "OK: 取消仿真发布成功"
        exit 2
    elif [ $1 -eq 2 ];then
        #如果是进行了灰度，点击取消，需要删除新打的tag,并将仿真环境的代码回滚(待定)
        cd  $CLONE_DIR$2 
        git tag -d $3
        git push origin --delete tag $3
        if [ $? -ne 0 ];then
            echo "ERROR: 取消版本失败!"
            exit 2
        fi
        #/usr/local/sbin/sa_online.sh sa_cancel $1 $2
        echo "OK: 取消正式发布成功"
    else
        echo "ERROR: 未知发布状态，取消发布失败"
    fi

}

#正式发布
function product(){
    if  [ $# != 1 ];then
        echo -e  "\033[31musage:\n sh $0  prouct  project-name \033[0m"
        exit  2
    fi
    #将$WORK_DIR下面的项目通过ansible批量推送到目标服务器
    ansible  web  -a  "mkdir -p /data/wwwroot/$1"
    ansible web  -m synchronize -a "src=/data/wwwroot/$1/ dest=/data/wwwroot/$1/ compress=yes"
    echo "OK: 正式发布成功"
}



case $1 in
    cancel)
        cancel $2 $4 $3;         #$2=cancel_flag  $3=tag  $4=project_name
        ;;
    emulation)
        emulation $2 $3 $4;       #$2=tag $3=commit  $4=project_name
        ;;
    product)
        product $2;
        ;;
    apply)
        apply  $2;               #$2=project_name
        ;;
    *)
        echo "Usage: sh $0 cancel cancel_flag project_name
       sh $0 emulation tag commit project_name  
       sh $0 product project_name
       sh $0 apply project_name
"
esac
