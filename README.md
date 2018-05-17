# pyzulipbot
A simple programmable zulipbot. Meant to allow for a easy interface to create custom slackbots.

based on [https://github.com/gregmccoy/pyslackbot](https://github.com/gregmccoy/pyslackbot)

## Install
`pip install git+https://github.com/gregmccoy/pyzulipbot.git`

## Usage
```python
from pyzulipbot.zulipbot import ZulipBot

def run():
    print("Hello World")

def get_time():
    handler = bot.get_handler("TIME")
    handler.format_reply(datetime.now())

bot = ZulipBot("zuliprc", True)
bot.add_handler("ID-4", "print", "", run)
bot.add_handler_json("data.json")
bot.add_handler("TIME", "What time is it?", "{}", get_time)
```


data.json
```json
{
    "handlers": [
        {
            "id":"#GREET",
            "message": [
                "Hello",
                "Hi",
                "Howdy"
            ],
            "reply": [
                "Hello",
                "Hi",
                "Howdy"
            ]
        },
    ]
}
```




