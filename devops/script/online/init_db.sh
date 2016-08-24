#!/bin/sh

DATA_DIR=/data/sql;
MYSQL="/usr/bin/mysql -h192.168.1.123 -ufalcon -p0b3998d1d61a6fedf7140f914c59ba95"
MYSQLDUMP="/usr/bin/mysqldump -h192.168.1.18 -ufalcon -p0b3998d1d61a6fedf7140f914c59ba95"
mkdir -p $DATA_DIR;

function dump_mall_data()
{
    #商城数据
    start_time=`date +%s`
    #$MYSQLDUMP -P3306 mall -w " 1=1 limit 30000" > ${DATA_DIR}/mall.sql;
    $MYSQLDUMP -P3306 mall > ${DATA_DIR}/mall.sql;
    echo "CREATE DATABASE IF NOT EXISTS mall; USE mall; SOURCE ${DATA_DIR}/mall.sql;" | $MYSQL -P3306
    end_time=`date +%s`
    echo "Dump 'mall' finish... $(($end_time-$start_time))";
}

function dump_100xhs_data()
{
    #咨询问答数据
    start_time=`date +%s`
    $MYSQLDUMP -P3307 ask_db -w " 1=1 limit 30000" > ${DATA_DIR}/ask.sql;
    echo "CREATE DATABASE IF NOT EXISTS ask_db; USE ask_db; SOURCE ${DATA_DIR}/ask.sql;" | $MYSQL -P3307
    end_time=`date +%s`
    echo "Dump 'ask_db' finish... $(($end_time-$start_time))";

    start_time=`date +%s`
    $MYSQLDUMP -P3307 jf_db -w " 1=1 limit 30000" > ${DATA_DIR}/jf.sql;
    echo "CREATE DATABASE IF NOT EXISTS jf_db; USE jf_db; SOURCE ${DATA_DIR}/jf.sql;" | $MYSQL -P3307
    end_time=`date +%s`
    echo "Dump 'jf_db' finish... $(($end_time-$start_time))";

    start_time=`date +%s`
    $MYSQLDUMP -P3307 jibing_db -w " 1=1 limit 100000" > ${DATA_DIR}/jibing.sql;
    echo "CREATE DATABASE IF NOT EXISTS jibing_db; USE jibing_db; SOURCE ${DATA_DIR}/jibing.sql;" | $MYSQL -P3307
    end_time=`date +%s`
    echo "Dump 'jibing_db' finish... $(($end_time-$start_time))";

    start_time=`date +%s`
    $MYSQLDUMP -P3307 jingyan_db -w " 1=1 limit 30000" > ${DATA_DIR}/jingyan.sql;
    echo "CREATE DATABASE IF NOT EXISTS jingyan_db; USE jingyan_db; SOURCE ${DATA_DIR}/jingyan.sql;" | $MYSQL -P3307
    end_time=`date +%s`
    echo "Dump 'jingyan_db' finish... $(($end_time-$start_time))";

    start_time=`date +%s`
    $MYSQLDUMP -P3307 mall -w " 1=1 limit 100000" > ${DATA_DIR}/mall1.sql;
    echo "CREATE DATABASE IF NOT EXISTS mall; USE mall; SOURCE ${DATA_DIR}/mall1.sql;" | $MYSQL -P3307
    end_time=`date +%s`
    echo "Dump 'mall' finish... $(($end_time-$start_time))";

    start_time=`date +%s`
    $MYSQLDUMP -P3307 scrapy_ask -w " 1=1 limit 30000" > ${DATA_DIR}/scrapy.sql;
    echo "CREATE DATABASE IF NOT EXISTS scrapy_ask; USE scrapy_ask; SOURCE ${DATA_DIR}/scrapy.sql;" | $MYSQL -P3307
    end_time=`date +%s`
    echo "Dump 'scrapy_ask' finish... $(($end_time-$start_time))";

    start_time=`date +%s`
    $MYSQLDUMP -P3307 service -w " 1=1 limit 100000" > ${DATA_DIR}/service.sql;
    echo "CREATE DATABASE IF NOT EXISTS service; USE service; SOURCE ${DATA_DIR}/service.sql;" | $MYSQL -P3307
    end_time=`date +%s`
    echo "Dump 'service' finish... $(($end_time-$start_time))";

    start_time=`date +%s`
    $MYSQLDUMP -P3307 shopnc -w " 1=1 limit 100000" > ${DATA_DIR}/shopnc.sql;
    echo "CREATE DATABASE IF NOT EXISTS shopnc; USE shopnc; SOURCE ${DATA_DIR}/shopnc.sql;" | $MYSQL -P3307
    end_time=`date +%s`
    echo "Dump 'shopnc' finish... $(($end_time-$start_time))";

    start_time=`date +%s`
    $MYSQLDUMP -P3307 spider -w " 1=1 limit 30000" > ${DATA_DIR}/spider.sql;
    echo "CREATE DATABASE IF NOT EXISTS spider; USE spider; SOURCE ${DATA_DIR}/spider.sql;" | $MYSQL -P3307
    end_time=`date +%s`
    echo "Dump 'spider' finish... $(($end_time-$start_time))";

    start_time=`date +%s`
    $MYSQLDUMP -P3307 user_db -w " 1=1 limit 50000" > ${DATA_DIR}/user.sql;
    echo "CREATE DATABASE IF NOT EXISTS user_db; USE user_db; SOURCE ${DATA_DIR}/user.sql;" | $MYSQL -P3307
    end_time=`date +%s`
    echo "Dump 'user_db' finish... $(($end_time-$start_time))";

    start_time=`date +%s`
    $MYSQLDUMP -P3307 usercenter > ${DATA_DIR}/usercenter.sql;
    echo "CREATE DATABASE IF NOT EXISTS usercenter; USE usercenter; SOURCE ${DATA_DIR}/usercenter.sql;" | $MYSQL -P3307
    end_time=`date +%s`
    echo "Dump 'usercenter' finish... $(($end_time-$start_time))";

    start_time=`date +%s`
    $MYSQLDUMP -P3307 words_db -w " 1=1 limit 100000" > ${DATA_DIR}/words.sql;
    echo "CREATE DATABASE IF NOT EXISTS words_db; USE words_db; SOURCE ${DATA_DIR}/words.sql;" | $MYSQL -P3307
    end_time=`date +%s`
    echo "Dump 'words_db' finish... $(($end_time-$start_time))";

    start_time=`date +%s`
    $MYSQLDUMP -P3307 zhuanti_db -w " 1=1 limit 30000" > ${DATA_DIR}/zhuanti.sql;
    echo "CREATE DATABASE IF NOT EXISTS zhuanti_db; USE zhuanti_db; SOURCE ${DATA_DIR}/zhuanti.sql;" | $MYSQL -P3307
    end_time=`date +%s`
    echo "Dump 'zhuanti_db' finish... $(($end_time-$start_time))";

    start_time=`date +%s`
    $MYSQLDUMP -P3307 lecture_db > ${DATA_DIR}/lecture.sql;
    echo "CREATE DATABASE IF NOT EXISTS lecture_db; USE lecture_db; SOURCE ${DATA_DIR}/lecture.sql;" | $MYSQL -P3307
    end_time=`date +%s`
    echo "Dump 'lecture_db' finish... $(($end_time-$start_time))";
}

function dump_api_data()
{
    #API数据
    start_time=`date +%s`
    $MYSQLDUMP -P3308 analytics_db -w " 1=1 limit 50000" > ${DATA_DIR}/analytics.sql;
    echo "CREATE DATABASE IF NOT EXISTS analytics_db; USE analytics_db; SOURCE ${DATA_DIR}/analytics.sql;" | $MYSQL -P3308
    end_time=`date +%s`
    echo "Dump 'analytics_db' finish... $(($end_time-$start_time))";

    start_time=`date +%s`
    $MYSQLDUMP -P3308 fms_db -w " 1=1 limit 50000" > ${DATA_DIR}/fms.sql;
    echo "CREATE DATABASE IF NOT EXISTS fms_db; USE fms_db; SOURCE ${DATA_DIR}/fms.sql;" | $MYSQL -P3308
    end_time=`date +%s`
    echo "Dump 'fms_db' finish... $(($end_time-$start_time))";

    start_time=`date +%s`
    $MYSQLDUMP -P3308 dapp_db -w " 1=1 limit 50000" > ${DATA_DIR}/dapp.sql;
    echo "CREATE DATABASE IF NOT EXISTS dapp_db; USE dapp_db; SOURCE ${DATA_DIR}/dapp.sql;" | $MYSQL -P3308
    end_time=`date +%s`
    echo "Dump 'dapp_db' finish... $(($end_time-$start_time))";

    start_time=`date +%s`
    $MYSQLDUMP -P3308 sapp_db -w " 1=1 limit 50000" > ${DATA_DIR}/sapp.sql;
    echo "CREATE DATABASE IF NOT EXISTS sapp_db; USE sapp_db; SOURCE ${DATA_DIR}/sapp.sql;" | $MYSQL -P3308
    end_time=`date +%s`
    echo "Dump 'sapp_db' finish... $(($end_time-$start_time))";

    start_time=`date +%s`
    $MYSQLDUMP -P3308 wxcs -w " 1=1 limit 50000" > ${DATA_DIR}/wxcs.sql;
    echo "CREATE DATABASE IF NOT EXISTS wxcs; USE wxcs; SOURCE ${DATA_DIR}/wxcs.sql;" | $MYSQL -P3308
    end_time=`date +%s`
    echo "Dump 'wxcs' finish... $(($end_time-$start_time))";
}

function dump_im_data()
{
    #IM数据
    start_time=`date +%s`
    $MYSQLDUMP -P3309 teamtalk -w " 1=1 limit 50000" > ${DATA_DIR}/teamtalk.sql;
    echo "CREATE DATABASE IF NOT EXISTS teamtalk; USE teamtalk; SOURCE ${DATA_DIR}/teamtalk.sql;" | $MYSQL -P3309
    end_time=`date +%s`
    echo "Dump 'teamtalk' finish... $(($end_time-$start_time))";
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
        all)
            dump_mall_data;
            dump_100xhs_data;
            dump_api_data;
            dump_im_data;
            ;;
        *)
            echo "Usage: $0 [mall|100xhs|api|im]"
            echo "ERROR: Parameter error"
            exit;
    esac
    echo "OK: Reset $1 finish";
fi
