# -*- coding: utf-8 -*-

from linebot import LineBotApi
from linebot.models import TextSendMessage
import json


class LineHandler:
	def __init__(self):
		self.access_token = self.load_access_token()

	def load_access_token(self):
		json_open = open("../config/api_keys.json", 'r')
		json_load = json.load(json_open)
		access_token = json_load["line_message_api"]["access_token"]
		return access_token

	def post_to_igarashi339(self, text):
		text = str(text)
		line_bot_api = LineBotApi(self.access_token)
		user_id = "U1fed3ee82231c47fce0de4a80f93c7be"
		messages = TextSendMessage(text=text)
		line_bot_api.push_message(user_id, messages=messages)