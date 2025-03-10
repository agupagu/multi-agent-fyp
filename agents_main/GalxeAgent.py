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
    	)
	)

	async with await browser.new_context() as context:
		model = ChatAnthropic(model_name='claude-3-5-sonnet-20240620', timeout=25, stop=None, temperature=0.3)
		openaimodel = ChatOpenAI(model='gpt-4o')


		# Initialize browser agent
		LoginCheckerAgent = Agent(
			task="""
				Objective: Detect User Login Status
				Detection Method:

				Navigate to app.galxe.com
				Wait for user to complete login process
				Confirm login by verifying absence of "Log In" button on screen

				Verification Criteria:

				User interface changes to logged-in state
				"Log In" button no longer visible

				Confirmation Signal:

				Visual absence of login button indicates successful authentication

				Note: Rely on visual UI state change as login confirmation mechanism.
			""",
			llm=openaimodel,
			browser_context=context,
		)
		AlphaHunterAgent = Agent(
			task="""
					Objective: Systematically capture details of the top 3 Trending Quests on app.galxe.com

					Detailed Steps:
					1. Navigate to app.galxe.com
					2. Locate the "Trending Quests" section by scrolling down
					3. For the first quest:
					- Click into the quest details page
					- Extract and record:
						* Full quest name
						* Complete quest URL
					- Return to the main "Trending Quests" section
					4. Repeat steps for the next two quests, maintaining the same extraction process

					Data Collection Requirements:
					- Capture exactly 3 quests
					- Ensure unique quest details for each entry
					- Maintain chronological order from the "Trending Quests" section

					Output Format:
					Provide a structured list/dictionary with the following for each quest:
					{
						"quest_name": "[Name of Quest]",
						"quest_url": "[Complete URL]"
					}
			""",
			llm=openaimodel,
			controller=controller,
			browser_context=context,
		)

		TaskCompletionAgent = Agent(
			task="""
				Objective: Complete Tasks in Each Quest
				Process:

				Open first quest URL from quests.json
				Identify task list within quest
				Task Execution:

				Click into each task
				Complete specified actions

				Social media interactions (X/Twitter)
				Link clicks
				Question answering

				Full Page Verification:

				Scroll entire page
				Confirm all tasks completed
                        
				Navigation:

				Return to quests.json
				Proceed to next quest URL


				Repeat process until all quests completed

				Key Focus:

				Systematic task completion
				Comprehensive page verification
				Sequential quest processing
			""",
			llm=openaimodel,
			controller=controller,
			browser_context=context,
		)
		TaskVerificationAgent = Agent(
			task="""
				Objective: Verify Completion of quests from quests.json
				Detailed Process:

				Open first quest URL from quests.json
				Quest Verification:

				Scroll entire page
				Refresh page to confirm task status
				Identify task completion via green tick marks

				Verification Criteria:

				Green tick mark = Task completed
				Full page scroll ensures comprehensive task review

				Navigation:

				After verifying all tasks on current quest
				Return to quests.json
				Proceed to next quest URL
				Repeat verification process

				Termination Condition:

				Complete verification of all questzes in quests.json

				Key Focus:

				Visual confirmation of task completion
				Systematic page-by-page verification
				Ensure 100% task status check
			""",
			llm=openaimodel,
			controller=controller,
			browser_context=context,
		)
            
		QuestCompletionAgent = Agent(
			task="""
				Quest Completion Check Workflow:
				Objective: Validate Quest Completion Status
				Process:

				Open first quest URL from quests.json
				Status Check:

				Verify "Completed" or "Claimed" status
				Navigation:

				If completed, return to quests.json
				Proceed to next quest URL


				Repeat until all quests verified

				Key Focus:

				Systematic status confirmation
				Sequential quest processing
			""",
			llm=openaimodel,
			controller=controller,
			browser_context=context,
		)


		await LoginCheckerAgent.run()
		await AlphaHunterAgent.run()
		await TaskCompletionAgent.run()
		await TaskVerificationAgent.run()	
		await QuestCompletionAgent.run()


asyncio.run(main())


