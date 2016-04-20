#!/bin/bash
cd  /root/gitolite-admin/conf
git add gitolite.conf
git commit -m "update git"
git push origin master

if [ $? -ne 0 ]; then
    echo "ERROR: 更新Git配置文件失败"
    exit 2
fi
echo "OK: 更新Git配置文件成功"
