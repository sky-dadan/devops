#!/bin/sh

DATA_DIR=/data/sql;
mkdir -p $DATA_DIR;

function dump_mall_data()
{
    #商城数据
    /usr/local/mysql/bin/mysqldump -h192.168.1.18 -P3306 -ufalcon -p0b3998d1d61a6fedf7140f914c59ba95 mall > ${DATA_DIR}/mall.sql;
    echo "Dump 'mall' finish...";
}

function dump_100xhs_data()
{
    #咨询问答数据
    /usr/local/mysql/bin/mysqldump -h192.168.1.18 -P3307 -ufalcon -p0b3998d1d61a6fedf7140f914c59ba95 ask_db --ignore-table=ask_db.j1_ask_count --ignore-table=ask_db.j1_ask_posts --ignore-table=ask_db.j1_ask_threads --ignore-table=ask_db.j1_ask_postsbak --ignore-table=ask_db.j1_ask_threads_bak > ${DATA_DIR}/ask.sql;
    /usr/local/mysql/bin/mysqldump -h192.168.1.18 -P3307 -ufalcon -p0b3998d1d61a6fedf7140f914c59ba95 ask_db j1_ask_count j1_ask_posts j1_ask_threads -w " 1=1 limit 100000" >> ${DATA_DIR}/ask.sql;
    echo "Dump 'ask_db' finish...";

    /usr/local/mysql/bin/mysqldump -h192.168.1.18 -P3307 -ufalcon -p0b3998d1d61a6fedf7140f914c59ba95 jf_db > ${DATA_DIR}/jf.sql;
    echo "Dump 'jf_db' finish...";

    /usr/local/mysql/bin/mysqldump -h192.168.1.18 -P3307 -ufalcon -p0b3998d1d61a6fedf7140f914c59ba95 jibing_db > ${DATA_DIR}/jibing.sql;
    echo "Dump 'jibing_db' finish...";

    /usr/local/mysql/bin/mysqldump -h192.168.1.18 -P3307 -ufalcon -p0b3998d1d61a6fedf7140f914c59ba95 jingyan_db > ${DATA_DIR}/jingyan.sql;
    echo "Dump 'jingyan_db' finish...";

    /usr/local/mysql/bin/mysqldump -h192.168.1.18 -P3307 -ufalcon -p0b3998d1d61a6fedf7140f914c59ba95 mall > ${DATA_DIR}/mall1.sql;
    echo "Dump 'mall' finish...";

    /usr/local/mysql/bin/mysqldump -h192.168.1.18 -P3307 -ufalcon -p0b3998d1d61a6fedf7140f914c59ba95 scrapy_ask > ${DATA_DIR}/scrapy.sql;
    echo "Dump 'scrapy_ask' finish...";

    /usr/local/mysql/bin/mysqldump -h192.168.1.18 -P3307 -ufalcon -p0b3998d1d61a6fedf7140f914c59ba95 service > ${DATA_DIR}/service.sql;
    echo "Dump 'service' finish...";

    /usr/local/mysql/bin/mysqldump -h192.168.1.18 -P3307 -ufalcon -p0b3998d1d61a6fedf7140f914c59ba95 shopnc > ${DATA_DIR}/shopnc.sql;
    echo "Dump 'shopnc' finish...";

    /usr/local/mysql/bin/mysqldump -h192.168.1.18 -P3307 -ufalcon -p0b3998d1d61a6fedf7140f914c59ba95 spider --ignore-table=spider.120content --ignore-table=spider.sh120content1 --ignore-table=spider.urllist > ${DATA_DIR}/spider.sql;
    /usr/local/mysql/bin/mysqldump -h192.168.1.18 -P3307 -ufalcon -p0b3998d1d61a6fedf7140f914c59ba95 spider 120content sh120content1 urllist -w " 1=1 limit 50000" >> ${DATA_DIR}/spider.sql;
    echo "Dump 'spider' finish...";

    /usr/local/mysql/bin/mysqldump -h192.168.1.18 -P3307 -ufalcon -p0b3998d1d61a6fedf7140f914c59ba95 user_db --ignore-table=user_db.j1_notices --ignore-table=user_db.j1_user_new --ignore-table=user_db.j1_doctor_user_new > ${DATA_DIR}/user.sql;
    /usr/local/mysql/bin/mysqldump -h192.168.1.18 -P3307 -ufalcon -p0b3998d1d61a6fedf7140f914c59ba95 user_db j1_notices -w " 1=1 limit 100000" >> ${DATA_DIR}/user.sql;
    echo "Dump 'user_db' finish...";

    /usr/local/mysql/bin/mysqldump -h192.168.1.18 -P3307 -ufalcon -p0b3998d1d61a6fedf7140f914c59ba95 usercenter > ${DATA_DIR}/usercenter.sql;
    echo "Dump 'usercenter' finish...";

    /usr/local/mysql/bin/mysqldump -h192.168.1.18 -P3307 -ufalcon -p0b3998d1d61a6fedf7140f914c59ba95 words_db > ${DATA_DIR}/words.sql;
    echo "Dump 'words_db' finish...";

    /usr/local/mysql/bin/mysqldump -h192.168.1.18 -P3307 -ufalcon -p0b3998d1d61a6fedf7140f914c59ba95 zhuanti_db --ignore-table=zhuanti_db.scrapy_feihua_article --ignore-table=zhuanti_db.scrapy_feihua_question --ignore-table=zhuanti_db.scrapy_hot_article --ignore-table=zhuanti_db.scrapy_hot_question --ignore-table=zhuanti_db.zt_admin_operatelog --ignore-table=zhuanti_db.zt_channel_article --ignore-table=zhuanti_db.zt_article > ${DATA_DIR}/zhuanti.sql;
    /usr/local/mysql/bin/mysqldump -h192.168.1.18 -P3307 -ufalcon -p0b3998d1d61a6fedf7140f914c59ba95 zhuanti_db scrapy_feihua_article scrapy_feihua_question scrapy_hot_article scrapy_hot_question zt_admin_operatelog zt_article zt_channel_article -w " 1=1 limit 40000" >> ${DATA_DIR}/zhuanti.sql;
    echo "Dump 'zhuanti_db' finish...";
}

function dump_api_data()
{
    #API数据
    /usr/local/mysql/bin/mysqldump -h192.168.1.18 -P3308 -ufalcon -p0b3998d1d61a6fedf7140f914c59ba95 analytics_db > ${DATA_DIR}/analytics.sql;
    echo "Dump 'analytics_db' finish...";

    /usr/local/mysql/bin/mysqldump -h192.168.1.18 -P3308 -ufalcon -p0b3998d1d61a6fedf7140f914c59ba95 fms_db > ${DATA_DIR}/fms.sql;
    echo "Dump 'fms_db' finish...";

    /usr/local/mysql/bin/mysqldump -h192.168.1.18 -P3308 -ufalcon -p0b3998d1d61a6fedf7140f914c59ba95 dapp_db > ${DATA_DIR}/dapp.sql;
    echo "Dump 'dapp_db' finish...";

    /usr/local/mysql/bin/mysqldump -h192.168.1.18 -P3308 -ufalcon -p0b3998d1d61a6fedf7140f914c59ba95 sapp_db > ${DATA_DIR}/sapp.sql;
    echo "Dump 'sapp_db' finish...";

    /usr/local/mysql/bin/mysqldump -h192.168.1.18 -P3308 -ufalcon -p0b3998d1d61a6fedf7140f914c59ba95 wxcs > ${DATA_DIR}/wxcs.sql;
    echo "Dump 'wxcs' finish...";
}

function dump_im_data()
{
    #IM数据
    /usr/local/mysql/bin/mysqldump -h192.168.1.18 -P3309 -ufalcon -p0b3998d1d61a6fedf7140f914c59ba95 teamtalk > ${DATA_DIR}/teamtalk.sql;
    echo "Dump 'teamtalk' finish...";
}


if [[ $# -ge 1 ]]; then
    case $1 in
        mall)
            dump_mall_data;
            ;;
        100xhs)
            dump_100xhs_data;
            ;;
        api)
            dump_api_data;
            ;;
        im)
            dump_im_data;
            ;;
        *)
            echo "Usage: $0 [mall|100xhs|api|im]"
    esac
else
    dump_mall_data;
    dump_100xhs_data;
    dump_api_data;
    dump_im_data;
fi
