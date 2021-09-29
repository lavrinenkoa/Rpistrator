echo `date` Copy
USER=pi
HOMEFOLDER=/home/pi
IP=192.168.0.110
# ssh $USER@$IP ls -l $HOMEFOLDER
scp rpistrator.py $USER@$IP:$HOMEFOLDER
#echo Run
#ssh $USER@$IP TERM=xterm-256color python3 $HOMEFOLDER/rpistrator.py
