# fund-spider
funds spider

# MACOS
    sudo pip install APNSWrapper
    brew install mysql-connector-c
    sudo pip install mysql-python

# CentOS
    yum -y install python-pip
    pip install APNSWrapper
    yum install python-devel
    pip install mysql-python

# 第一步：写cron脚本文件。例如：取名一个 crontest.cron的文本文件，只需要写一行：
    15,30,45,59 * * * * echo "xgmtest.........." >> xgmtest.txt
    表示，每隔15分钟，执行打印一次命令
# 第二步：添加定时任务。执行命令 “crontab crontest.cron”。搞定
# 第三步：如不放心，可以输入 "crontab -l" 查看是否有定时任务