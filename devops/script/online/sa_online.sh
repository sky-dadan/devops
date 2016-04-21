#!/bin/bash
DIR_PROJECT='/data/wwwroot/'
BACKUP='/data/backup/'
HOST=''

export PATH=/usr/bin:$PATH

#backup $1 $2     $1=commit  $2=project_name  每次备份保存commit
function sa_backup(){
    time=`date`
    mkdir -p  $BACKUP$2
    mkdir -p  $DIR_PROJECT$2
    tar -czf $BACKUP$2/$1.tar.gz  -C  $DIR_PROJECT  $2    
    echo $1 $time  >> $BACKUP$2/version
}

#sa_rsync_emulation  $1=project_name
function sa_rsync_emulation(){
    ansible  test1:test2  -a  "mkdir -p /data/wwwroot/$1"
    ansible test1:test2  -m synchronize -a "src=/data/wwwroot/$1/ dest=/data/wwwroot/$1/ compress=yes"
}

#sa_rsync_product   $1=project_name
function sa_rsync_product(){
    ansible  web  -a  "mkdir -p /data/wwwroot/$1"
    ansible web  -m synchronize -a "src=/data/wwwroot/$1/ dest=/data/wwwroot/$1/ compress=yes"

}

#sa_cancel  $1=cancel_flag  $2=project
function sa_cancel(){
    if [ $1 -eq 2];then
        rm -rf $DIR_PROJECT$2
        last_commit=`tail -1 $BACKUP$2/version | awk '{print $1}'`
        tar  zxf $BACKUP$2/$last_commit.tag.gz -C $DIR_PROJECT$2
        #rsync
    else
        echo "cancel_flag error"
    fi

}


case $1 in
    sa_backup)
        sa_backup $2 $3;     #$2=commit   $3=project_name
        ;;
    sa_rsync_emulation)
        sa_rsync_emulation $2 ;   #$2=project_name
        ;;
    sa_rsync_product)
        sa_rsync_product  $2;           #$2=project_name
        ;;
    sa_cancel)
        sa_cancel $2 $3;                #$2=cancel_flag   $3=project_name
        ;;
    *)
    echo "review $0 usage~!"
esac
