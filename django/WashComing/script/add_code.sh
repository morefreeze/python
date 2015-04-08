if [ $# -lt 1 ];then
    echo "sh $0 FILENAME(without csv)"
    exit 1
fi
name='北京电视台'
cid_thd_id='NULL'
start_time="2015-03-09 00:00:00"
expire_time='2016-01-01 00:00:00'
keep_time='2015-03-09 00:00:00'
exp_thd='0'
price_thd='0'
percent_dst='0'
max_limit='1'
price_dst_low='200'
price_dst_upp='200'
cat $1.csv | awk -F, 'NR>1{printf("INSERT INTO `WashComing_online`.`WCBill_coupon` (`coid`, `name`, `cid_thd_id`, `start_time`, `expire_time`, `keep_time`, `exp_thd`, `price_thd`, `percent_dst`, `max_limit`, `create_time`, `price_dst_low`, `price_dst_upp`, `code`, `use_code`) VALUES(NULL, \"%s\", %s, \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"1\");\n", "'$name'", "'"$cid_thd_id"'", "'" $start_time "'","'" $expire_time "'","'" $keep_time "'",'$exp_thd','$price_thd','$percent_dst','$max_limit',"'"$(date "+%Y-%m-%d %H:%M:%S")"'",'$price_dst_low','$price_dst_upp', $2)}' > $1.sql
