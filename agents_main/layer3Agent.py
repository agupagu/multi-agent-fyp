import os
import sys
from langchain_openai import ChatOpenAI
import importlib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio

import browser_use

# Reload the module
importlib.reload(browser_use)

# Then re-import the classes after reload
from browser_use import Agent, Browser, Controller, AgentHistoryList
from browser_use.controller.service import Controller
from langchain_anthropic import ChatAnthropic
from browser_use.browser.browser import BrowserConfig
from pydantic import BaseModel
from typing import List, Optional
import json, os
from playwright.async_api import BrowserContext



browser = Browser(
config=BrowserConfig(
	headless=False,
	chrome_instance_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  # Adjust this path for your OS
	)
)

controller = Controller()

class Quest(BaseModel):
	name: str
	url: str


class Quests(BaseModel):
	quests: List[Quest]

class elment_on_page(BaseModel):
	index: int
	xpath: Optional[str] = None



@controller.action('Save quests to a file named Layer3quests.json', param_model=Quests)
def save_quests(params: Quests):
	file_path = 'Layer3quests.json'

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

@controller.action('Read quests from Layer3quests.json file')
def read_quests():
	with open('Layer3quests.json', 'r') as f:
		return f.read()
	  

# Video: https://preview.screen.studio/share/8Elaq9sm
async def main():
	  
	# Persist the browser state across agents

	async with await browser.new_context() as context:
		ClaudeModel = ChatAnthropic(model_name='claude-3-7-sonnet-20250219', timeout=25, stop=None, temperature=0.3)
		openaimodel = ChatOpenAI(model='gpt-4o', temperature=0.3)
	


		# Initialize browser agent
		LoginCheckerAgent = Agent(
			task="""
				Objective: Detect User Login Status
				Detection Method:

				Navigate to https://app.layer3.xyz/quests
				Wait for user to complete login process
				Confirm login by verifying absence of "Log In" button on screen

				Verification Criteria:

				User interface changes to logged-in state
				"Log In" button no longer visible

				Confirmation Signal:

				Visual absence of login button indicates successful authentication

				Note: Rely on visual UI state change as login confirmation mechanism.
			""",
			llm=ClaudeModel,
			browser_context=context,
		)
		AlphaHunterAgent = Agent(
			task="""
					Objective: Systematically capture details of the first 3 quests for the first featured quest 
					in the 'New' section of https://app.layer3.xyz/quests

					Detailed Steps:
					1. Navigate to https://app.layer3.xyz/quests
					2. Locate the "New" section which will have 3 quests listed below it
					3. For the first quest:
					- Click into the featured campaign that is being displayed
					- Extract and record:
						* Full quest name
						* Complete quest URL
					- Return to the main main campaign page
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

					Save the extracted quests to a file named Layer3quests.json

			""",
			llm=ClaudeModel,
			controller=controller,
			browser_context=context,
		)

		TaskCompletionAgent = Agent(
			task="""
			Objective: Complete quests in Layer3quests.json

			Each quest comprises of multiple tasks. Complete each task in the quest.
			
			Before starting a task, ensure to extract the description of the task.
			
			Pre-execution Validation:
			1. For each onchain task:
			- Wait for 20 seconds for the user to connect their wallet (This is a must)
			- Verify exact network (e.g., "Ethereum", "Polygon", "Arbitrum")
			- Confirm token name
			- Validate token amount
			- Check wallet balance before execution

			If the task is optional press the skip button and move to the next task.
			Always press the verify button before starting the task in the event the user has already completed the task previously.
			If the tasks have already been marked as complete by a green tick mark, skip the task and move to the next task.
			
			Task Categories and Steps:
			
			1. Social Media Tasks:
			- Verify authentic platform URL
			- Complete specified interaction
			- Wait for confirmation
			- Verify task completion status
			
			2. Link Click Tasks:
			- Validate URL destination
			- Complete click action
			- Verify tracking completion
			
			3. Question/Answer Tasks:
			- Record exact question text
			- Submit specified answer
			- Verify response acceptance
			
			4. Onchain Tasks:
			- PRE-EXECUTION CHECKLIST:
				* Network: Confirm exact network name
				* Token: Verify name matches that specified in the original quest page (e.g., "USDC", "ETH") prior to going to the external link
				* Token: Remember the token name to be used in the transaction (The task page would say something like "Bridge any amoount of XXX to YYY", where XXX is the token name)
				* Amount: Double-check required amount
				* Action: Validate specific action (bridge/stake/swap)
			- Execute only after all checks pass
			- Verify task completion on quest platform

			5. Claim rewards associated with the task by clicking the "Mint Cube" button or a button of similar nature to claim rewards.
			
			5. Next task
			Once a task is completed, proceed to the next task and repeat the validation and execution process.

			ONLY COMPLETE QUESTS IN Layer3quests.json and nothing else. Once a quest has been completed, move on to the next quest in Layer3quests.json.
	
			""",
			llm=ClaudeModel,
			controller=controller,
			browser_context=context,
		)

		TaskVerificationAgent = Agent(
			task="""
				Objective: Verify Completion of quests from Layer3quests.json
				Detailed Process:

				Open first quest URL from Layer3quests.json
				Quest Verification:

				Identify task completion via green tick marks on the left and a completed status
				Claim all rewards if the quest is completed. If there is an option to switch to another network, click that button and proceed with claiming the rewards.

				Verification Criteria:

				Green tick mark = Task completed
				Full page scroll ensures comprehensive task review

				Navigation:

				After verifying all tasks on current quest
				Return to Layer3quests.json
				Proceed to next quest URL
				Repeat verification process

				Termination Condition:

				Complete verification of all quests in Layer3quests.json

				Key Focus:

				Visual confirmation of task completion
				Systematic page-by-page verification
				Ensure 100% task status check
			""",
			llm=ClaudeModel,
			controller=controller,
			browser_context=context,
			use_vision=False,
		)
			
		QuestCompletionAgent = Agent(
			task="""
				Quest Completion Check Workflow:
				Objective: Validate Quest Completion Status
				Process:

				Open first quest URL Layer3quests.json in a new tab. DO NOT use the original layer3.xyz tab that is already open. Do this for all links in Layer3quests.json
				Status Check:

				Verify "Completed" or "Claimed" status
				Navigation:

				If completed, return to Layer3quests.json
				Proceed to next quest URL


				Repeat until all quests verified

				Key Focus:

				Systematic status confirmation
				Sequential quest processing
			""",
			llm=ClaudeModel,
			controller=controller,
			browser_context=context,
		)

		

		# LoginCheckerAgenthistory = await LoginCheckerAgent.run()
		# LoginCheckerAgenthistoryTokens = LoginCheckerAgenthistory.total_input_tokens()
		# LoginCheckerAgenthistorytime = LoginCheckerAgenthistory.total_duration_seconds()
		# print("Tokens used for LoginCheckerAgent:", LoginCheckerAgenthistoryTokens)
		# print("Time taken for LoginCheckerAgent:", LoginCheckerAgenthistorytime)


		# AlphaHunterAgenthistory = await AlphaHunterAgent.run()
		# AlphaHunterAgenthistoryTokens = AlphaHunterAgenthistory.total_input_tokens()
		# AlphaHunterAgenthistorytime = AlphaHunterAgenthistory.total_duration_seconds()
		# print("Tokens used for AlphaHunterAgent:", AlphaHunterAgenthistoryTokens)
		# print("Time taken for AlphaHunterAgent:", AlphaHunterAgenthistorytime)


		TaskCompletionAgenthistory = await TaskCompletionAgent.run()
		TaskCompletionAgenthistoryTokens = TaskCompletionAgenthistory.total_input_tokens()
		TaskCompletionAgenthistorytime = TaskCompletionAgenthistory.total_duration_seconds()
		print("Tokens used for TaskCompletionAgent:", TaskCompletionAgenthistoryTokens)
		print("Time taken for TaskCompletionAgent:", TaskCompletionAgenthistorytime)


		TaskCompletionAgenthistory = await TaskVerificationAgent.run()
		TaskCompletionAgenthistoryTokens = TaskCompletionAgenthistory.total_input_tokens()
		TaskCompletionAgenthistorytime = TaskCompletionAgenthistory.total_duration_seconds()
		print("Tokens used for TaskVerificationAgent:", TaskCompletionAgenthistoryTokens)
		print("Time taken for TaskVerificationAgent:", TaskCompletionAgenthistorytime)


		QuestCompletionAgenthistory = await QuestCompletionAgent.run()
		QuestCompletionAgenthistoryTokens = QuestCompletionAgenthistory.total_input_tokens()
		QuestCompletionAgenthistorytime = QuestCompletionAgenthistory.total_duration_seconds()
		print("Tokens used for QuestCompletionAgent:", QuestCompletionAgenthistoryTokens)
		print("Time taken for QuestCompletionAgent:", QuestCompletionAgenthistorytime)


asyncio.run(main())


