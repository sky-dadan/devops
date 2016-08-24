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
URGENT='/data/urgent/'

mkdir -p $CLONE_DIR
mkdir -p $BACK_UP
mkdir -p $WORK_DIR
mkdir -p $URGENT

#申请发布
function apply(){
    if  [ $# != 2 ];then
        echo -e  "\033[31musage:\n sh $0  apply project-name apply_type \033[0m"
        echo "ERROR: 调用脚本错误"
        exit  2
    fi

    if [ $2 -eq 0 ];then            #正常申请流程
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
    else                            #紧急申请流程
        cd $URGENT
        git clone -b urgent git@127.0.0.1:$1
        if [ $? -ne 0 ]; then
            echo "ERROR: 克隆紧急上线代码失败"
            exit 1
        fi
    cd $1
        chown -R www:www $URGENT$1
        commit=`git log  --oneline -1 --pretty=format:"%h"`
        echo "OK: $commit"
    fi
}

    
function emu_prepare(){     #tag  commit  project_name  path($CLONE_DIR|$URGENT)
    if [ $4 == '/data/urgent/' ];then
       tmp=${2}_urgent
    else
       tmp=$2
    fi
    cd $4$3
    git tag -a $1 $2 -m $1
    if  [ $? -ne 0 ];then
        echo "ERROR: 标示本地版本失败!"
        exit 2
    fi
    git push origin $1
    if  [ $? -ne 0 ];then
        echo  "ERROR: 标示远程版本失败!"
        exit 2
    fi
    tar zcf $BACK_UP$3/$tmp.tar.gz -C $WORK_DIR $3
    if [ $? -ne 0 ];then
        echo "ERROR: 备份代码失败!"
        exit 2
    fi
    /usr/bin/rsync -avz    --exclude=.git  --include=assets/js --include=assets/css --include=assets/images --include=assets/wechat --include=assets/My97DatePicker --exclude=assets/*/  $4$3/ $WORK_DIR$3
    if [ $? -ne 0 ];then
        echo "ERROR: 仿真环境同步失败!"
        exit 2
    fi
    ansible  test1:test2  -a  "mkdir -p /data/wwwroot/$3"
    ansible test1:test2  -m synchronize -a "src=/data/wwwroot/$3/ dest=/data/wwwroot/$3/ compress=yes"
    echo "OK: 正常仿真环境发布成功!"
}
#灰度发布
function emulation(){
    if [ $# != 4 ];then
        echo "传入参数错误, sh $0 emulation tag,commit,project_name,apply_type"
        exit 2
    fi
    mkdir -p $BACK_UP$3;mkdir -p $WORK_DIR$3 
    if [ $4 -eq 0 ];then
        emu_prepare  $1 $2 $3 $CLONE_DIR
    else
        emu_prepare  $1 $2 $3 $URGENT
    fi
}

#取消发布
function cancel(){
    if [ $1 -eq 1 ];then
        #如果是没有经过灰度，点击取消，则什么都不需要操作
        echo "OK: 取消仿真发布成功"
        exit 2
    elif [ $1 -eq 2 ] && [ $4 -eq 0 ];then        #正常发布取消
        #如果是进行了灰度，点击取消，需要删除新打的tag,并将仿真环境的代码回滚(待定)
        cd  $CLONE_DIR$2 
    elif [ $1 -eq 2 ] && [ $4 -eq 1 ];then      #紧急发布取消
        cd $URGENT$2
    else
        echo "ERROR: 未知发布状态，取消发布失败"
        exit 2
    fi
    if [ $# -lt 4 ];then
        echo "Usage sh $0 cancel_flag project_name tag apply_type" 
        exit
    fi
    echo $1  $2  $3  $4
    git tag -d $3
    if [ $? -ne 0 ];then
        echo "ERROR: 取消本地版本失败!"
        exit 2
    fi
    git push origin --delete tag $3
    if [ $? -ne 0 ];then
        echo "ERROR: 取消远程版本失败!"
        exit 2
    fi
    rm -rf  $URGENT$2
    echo "OK: 取消正式发布成功"

}

#正式发布
function product(){
    if  [ $# != 2 ];then
        echo -e  "\033[31musage:\n sh $0  prouct  project-name apply_type\033[0m"
        exit  2
    fi

    if [ $2 -eq 1 ];then
        rm -rf  $URGENT$1
    fi

    #将$WORK_DIR下面的项目通过ansible批量推送到目标服务器
    ansible  web:nginx1:im  -a  "mkdir -p /data/wwwroot/$1"
    ansible web:nginx1:im  -m synchronize -a "src=/data/wwwroot/$1/ dest=/data/wwwroot/$1/ compress=yes"
    echo "OK: 正式发布成功"
}


case $1 in
    cancel)
        cancel $2 $3 $4 $5;         #$2=cancel_flag  $3=project_name  $4=tag  $5=apply_type
        ;;
    emulation)
        emulation $2 $3 $4 $5;       #$2=tag $3=commit  $4=project_name  $5=apply_type
        ;;
    product)
        product $2 $3;               #$2=project_name   $3-apply_type
        ;;
    apply)
        apply  $2 $3;               #$2=project_name  $3=apply_type
        ;;
    *)
        echo "Usage: sh $0 cancel cancel_flag project_name tag apply_type
       sh $0 emulation tag commit project_name  apply_type
       sh $0 product project_name  apply_type
       sh $0 apply project_name apply_type
"
esac

