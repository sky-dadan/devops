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
commit=`git log  --oneline -1 --pretty=format:"%h"`
tag=`git log --oneline -1 --pretty=format:"%s"`
echo "$commit"
echo "$tag"

##########  python 脚本调用 ################################################
# cat test.py 
# import subprocess
#
# p = subprocess.Popen(['sh','apply.sh','%s' % project-name],stdout=subprocess.PIPE)
# commit = p.stdout.readline()    #获取commit
# tag = p.stdout.readline()       #获取tag
 

