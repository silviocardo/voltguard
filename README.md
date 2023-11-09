# Energy Shortage Detector

A simple Telegram bot, running on a Raspberry Pi, designed to detect instances of energy shortages.\
I developed this solution to address the recurring shortages I experienced in my previous apartment, especially when I was away for an extended period.

## Set-up

I used a "Raspberry Pi 3 Model Bi +" to run the bot script. The Raspberry was connected to the Wi-Fi network (which was shared in the building, so always on). Then I created the bot with the corresponding [Telegram Bot API](https://core.telegram.org/api#bot-api) and communicated with it through Telegram on my phone with simple commands.

## Installation

Install the required packages listed in requirements.txt

### MacOS
`$ pip3 install -r requirements.txt`

### Raspberry PI
`$ pip3 install -r requirements.txt`

## Configuring the service
In order to make the bot run 24/7 *at startup*, a possible solution is to use `systemctl`.\
Create a service with:
```sudo systemctl edit --force --full telegram_bot.service```

Insert in the editor the following code:
```
[Unit]
Description=Telegram bot
Wants=network.target
After=network.target

[Service]
User=pi
ExecStart=/usr/bin/python3 /home/pi/voltguard/bot_main.py

[Install]
WantedBy=multi-user.target
```

Need to enable the service:
```sudo systemctl enable telegram_bot.service```

Now reboot and check the status with:
```systemctl status telegram_bot.service```

_[Check: https://raspberrypi.stackexchange.com/questions/90148/running-a-python-telegram-bot-at-startup-and-24-7]_

## Possible issues by running `main.py`

* From numpy package => libf77blas.so.3: cannot open shared object file: No such file or directory
  
  run the following
  `sudo apt-get install libatlas-base-dev`

  to install the missing libraries expected by the self-compiled NumPy (ATLAS is a possible provider of linear algebra).

  _[Check: https://numpy.org/devdocs/user/troubleshooting-importerror.html]_
  