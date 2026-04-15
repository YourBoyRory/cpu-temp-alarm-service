sudo mkdir -p /etc/cpu-alarm/
sudo cp config.ini /etc/cpu-alarm/
sudo chmod 644 /etc/cpu-alarm/config.ini

sudo cp cpu-alarm.py  /usr/local/bin/cpu-alarm-service
sudo chmod 755 /usr/local/bin/cpu-alarm-service

sudo cp cpu_alarm.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable cpu_alarm
