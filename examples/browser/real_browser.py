import os
import sys

from langchain_openai import ChatOpenAI

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio

from browser_use import Agent, Browser, Controller
from browser_use.controller.service import Controller
from langchain_anthropic import ChatAnthropic
from browser_use.browser.browser import BrowserConfig
from pydantic import BaseModel
from typing import List
import json, os

controller = Controller()

class Quest(BaseModel):
	name: str
	url: str


class Quests(BaseModel):
	quests: List[Quest]


@controller.action('Save quests to a file named quests.json', param_model=Quests)
def save_quests(params: Quests):
	file_path = 'quests.json'

	# Load existing data if the file exists
	if os.path.exists(file_path):
		with open(file_path, 'r') as f:
			quests = json.load(f)
	else:
		quests = []

	# Append new quests
	for quest in params.quests:
		quests.append({"name": quest.name, "url": quest.url})

	# Write the updated data to the JSON file
	with open(file_path, 'w') as f:
		json.dump(quests, f, indent=4)

@controller.action('Read quests from quests.json file')
def read_quests():
	with open('quests.json', 'r') as f:
		return f.read()
	  

# Video: https://preview.screen.studio/share/8Elaq9sm
async def main():
	# Persist the browser state across agents


	browser = Browser(
	config=BrowserConfig(
		headless=False,
		chrome_instance_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  # Adjust this path for your OS
		extra_chromium_args=["--disable-extentions"]
		)
	)

	async with await browser.new_context() as context:
		model = ChatAnthropic(model_name='claude-3-7-sonnet-20250219', timeout=25, stop=None, temperature=0.3)
		openaimodel = ChatOpenAI(model='gpt-4o')


		# Initialize browser agent
		TesterAgent = Agent(
			task="""
				1. Go to jumper.exchange and bridge 0.001 ETH from Optimism to Base

			""",
			llm=model,
			browser_context=context,
		)
			
		# NextStepAgent = Agent(
		# 	task="""
		#         1. Complete the first step of this quest.
		#         2. If there is a need to log in/sign in always choose the wallet connect option. Wait for the user to finish signing in
		#         before continuing
		#         3. Return back to the home page and press the verify button once done

		# 	""",
		# 	llm=openaimodel,
		# 	browser_context=context,
		# )
			
		# VerifyAgent = Agent(
		# 	task="""
		#         3. Return back to the quest page and press the verify button once done with the first step

		# 	""",
		# 	llm=openaimodel,
		# 	browser_context=context,
		# )



		history = await TesterAgent.run()
		print(history.input_token_usage())
		
		# await NextStepAgent.run()
		# await VerifyAgent.run()


asyncio.run(main())


