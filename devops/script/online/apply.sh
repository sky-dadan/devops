#!/bin/bash

if [ $# != 1 ];then
    echo -e  "\033[31musage:\n sh apply.sh project-name \033[0m"
    exit
fi

cd   /data/gitclone
if [ ! -d $1 ]; then
     mkdir /data/gitclone/$1
fi

cd $1
git pull>/dev/null
commit=`git log |awk  'NR==1{ print substr($2,1,6)}'`
tag=`git log |awk  'NR==11{for(i=1;i<=NF;i++) printf $i " "}'`
echo "$commit"
echo "$tag"

##########  python 脚本调用 ################################################
# cat test.py 
# import subprocess
#
# p = subprocess.Popen(['sh','apply.sh','liuziping'],stdout=subprocess.PIPE)
# commit = p.stdout.readline().rstrip('\n')    #获取commit
# tag = p.stdout.readline().rstrip('\n')       #获取tag
 

