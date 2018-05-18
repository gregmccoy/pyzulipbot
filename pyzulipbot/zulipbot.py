import zulip
import threading
import time
import json
import random

class ZulipBot(object):
    """Handles ZulipBot interface

    Base class from the zulipbot, create a bot and listens for messages.
    Handles messages using handlers.

    Args:
        bot_id (str): The zuliprc used to create the bot.
        debug (bool): Determines if debug mode is enabled.
    """
    def __init__(self, bot_id, debug=False):
        self.client = zulip.Client(config_file=bot_id)
        self.user = self.client.get_profile()
        self.debug = debug

        self.threads = []
        t = threading.Thread(target=self.client.call_on_each_message, args=(self.watch_message,))
        self.threads.append(t)
        t.start()

        self.handlers = []


    def trigger_handler(self, handler_id):
        """Triggers handler based on ID

        Args:
            handler_id (str): Unique ID of handler.
        """
        handler = self.get_handler(handler_id)
        self.run_handler(handler, handler.channel)

    def get_handler(self, handler_id):
        """Gets a handler based on ID

        Args:
            handler_id (str): Unique ID of handler.

        Returns:
            Handler if ID matches a handler, otherwise None
        """
        for h in self.handlers:
            if h.handler_id == handler_id:
                return h
        return None

    def add_handler(self, handler_id, msg, reply, run=None, channel=None):
        """Creates a handler

        Args:
            handler_id (str): Unique ID of handler.
            msg (str): Message that the handler will watch for.
            reply (str): Reply to be send when message is recieved.
            run (Optional [func]): function to be run when message is recieved.
            channel (Optional [str]): Channel reply will be sent to.

        """
        msgs = []
        replys = []
        if type(reply) is str:
            replys.append(reply.lower())
        else:
            replys = reply

        if type(msg) is str:
            msgs.append(msg.lower())
        else:
            for i in range(len(msg)):
                msg[i] = msg[i].lower()
            msgs = msg

        handler = Handler(handler_id, msgs, replys, run, channel)
        self.handlers.append(handler)

    def add_handler_object(self, handler):
        """Adds a handler object of type Handler

        Args:
            handler (Handler): Handler to be added
        """
        self.handlers.append(handler)


    def add_handler_json(self, data):
        """Creates a handler based on json file

        Args:
            data (str): File location of json file.

        """
        with open(data) as f:
            reader = json.load(f)
            for item in reader["handlers"]:
                try:
                    for i in item["reply"]:
                        i = i.encode("utf-8").decode("unicode_escape")
                    for i in item["message"]:
                        i = i.lower()
                    self.add_handler(item['id'], item['message'], item['reply'])
                except Exception as e:
                    print("Error adding handler from CSV")
                    print(e)
                    break


    def watch_message(self, message):
        """Trigger when there's a new message on Zulip

        If the bot is tagged in the message it will check the handlers to
        see if there is a handler for that message.

        """
        type = message.get("type", "")
        if type == "private" or type == "stream":
            if message['sender_id'] != self.user['user_id']:
                try:
                    #There is a message from a user
                    text = message["content"]
                    if self.debug:
                        print("Message - " + text)
                    if message['type'] == "private":
                        message["stream"] = { "to": message["sender_email"] }
                    else:
                        message["stream"] = { "to": message["display_recipient"], "subject": message["subject"] }
                    if "**" + self.user['full_name'] + "**"  in text or message["type"] == 'private':
                        self.parse_message(message)
                except Exception as e:
                    print("Except - {}".format(e))
                    #excepts when the message doesn't have a type, just ignore and keep going
                    pass

    def parse_message(self, message):
        """Checks message for handler

        Args:
            message (dict): Message that was recieved
        """
        for handler in self.handlers:
            for msg in handler.message:
                if msg in message['content'].lower():
                    handler.received = message
                    self.run_handler(handler, message['stream'])
                    return 0
            if message['content'].lower() in handler.message:
                handler.received = message
                self.run_handler(handler, message['stream'])
                return 0

    def run_handler(self, handler, channel):
        """Sends reply and run handler functions

        Sends the reply message over zulip and executes the function if
        it is not None.

        Args:
            handler (:class:`Handler`): Handler that needs to be triggered
            channel (dict): Stream of the message recieved
        """
        handler_reply = None
        if handler.run != None:
            if self.debug:
                print("Excuting - " + str(handler.run))
            try:
                handler_reply = handler.run()
            except Exception as e:
                print("Exception during handler function")
                print(e)

        if handler.reply != [""] and handler.reply != None or handler_reply:
            if handler.channel != None:
                channel = handler.channel
            if channel == None:
                print("Error: No stream selected")
                return 1

            reply = handler_reply or random.choice(handler.reply)
            if self.debug:
                print("Reply: " + str(channel) + "  - " + str(reply))

            if "@" in channel["to"]:
                type = "private"
            else:
                type= "stream"

            if type == "stream":
                self.client.send_message({
                    "type": str(type),
                    "subject": str(channel["subject"]),
                    "to": str(channel["to"]),
                    "content": str(reply),
                })
            else:
                self.client.send_message({
                    "type": str(type),
                    "to": str(channel["to"]),
                    "content": str(reply),
                })
            handler.reply = handler.org_reply




class Handler(object):
    """Handle message triggers and replies

    Class used to create handlers for messages and replies.

    Args:
        handler_id (str): A unique ID for the handler.
        message (list):  List of messages that with trigger the handler.
        reply (list): List of replies to send back when the message is received.
        org_reply (list): Copy of reply to allow reseting reply after it is formatted.
        run (func): An function that will be run when message is received. If it returns
            a string, it will be used for the reply.
        channel (channel): Channel that the reply will be sent to.
        received (channel): Initalizes as None, will be set to the message recievied.
    """
    def __init__(self, handler_id, message, reply, run, channel):
        self.handler_id = handler_id
        self.message = message
        self.reply = reply
        self.org_reply = reply
        self.run = run
        self.channel = channel
        self.received = None

    def format_reply(self, msg):
        self.reply[0] = self.reply[0].format(msg)


