#!/bin/bash
#
# Walker 2016 01 29


CUR_PATH=`pwd`
CUR_LOG=$CUR_PATH/bot.log

#echo $CUR_PATH


function getpid(){
    PID=`ps axu | grep bot.py | grep -v grep | awk '{print $2}'`
    echo "$PID"
}



case $1 in
    "start")
        #python $CUR_PATH/bot.py &> $LOG &
        python $CUR_PATH/bot.py &
        PID=$(getpid)
        echo "bot start at PID: $PID"
    ;;

    "stop")
        #PID=`ps axu | grep bot.py | grep -v grep | awk '{print $2}'`
        PID=$(getpid)
        if [ "$PID" != "" ];then
            kill -9 $PID
            echo "stop bot PID: $PID"
        fi
    ;;

    "restart")
        $0 stop
        sleep 1
        $0 start
    ;;

    "status")
        PID=$(getpid)
        #PID=`ps axu | grep bot.py | grep -v grep | awk '{print $2}'`
        if [ "$PID" != "" ];then
            echo "bot is running at PID: $PID"
        else
            echo "bot is stop!!"
        fi
    ;;

    "log")
        tail -f $CUR_LOG
    ;;

    *)
        echo "Use $0 (start|stop|restart|status|log)"
    ;;
esac
