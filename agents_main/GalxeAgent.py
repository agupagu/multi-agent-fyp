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


@controller.action('Save quests to a file named Galxequests.json', param_model=Quests)
def save_quests(params: Quests):
	file_path = 'Galxequests.json'

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

@controller.action('Read quests from Galxequests.json file')
def read_quests():
	with open('Galxequests.json', 'r') as f:
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
		ClaudeAIModel = ChatAnthropic(model_name='claude-3-7-sonnet-20250219', timeout=25, stop=None, temperature=0.3)
		OpenAIModel = ChatOpenAI(model='gpt-4o', temperature=0.3)


		# Initialize browser agent
		LoginCheckerAgent = Agent(
			task="""
				Objective: Detect User Login Status
				Detection Method:

				Navigate to https://app.galxe.com/quest/explore/all?sortType=Trending
				Wait for user to complete login process
				Confirm login by verifying absence of "Log In" button on screen

				Verification Criteria:

				User interface changes to logged-in state
				"Log In" button no longer visible

				Confirmation Signal:

				Visual absence of login button indicates successful authentication

				Note: Rely on visual UI state change as login confirmation mechanism.
			""",
			llm=ClaudeAIModel,
			browser_context=context,
		)
		AlphaHunterAgent = Agent(
			task="""
					Objective: Systematically capture details of the top 3 Trending Quests

					Detailed Steps:
					1. Locate the Quests section by scrolling down
					2. For the first quest:
					- Click into the quest details page
					- Extract and record:
						* Full quest name
						* Complete quest URL (Not just the path)
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

					Save the extracted quests to a file named Galxequests.json
			""",
			llm=ClaudeAIModel,
			controller=controller,
			browser_context=context,
		)

		TaskCompletionAgent = Agent(
			task="""
				OBJECTIVE: Complete All Tasks in Each Quest

				PROCESS OVERVIEW:
				1. Access each quest URL sequentially from Galxequests.json (DO NOT DO ANY OTHER QUESTS APART FROM THOSE IN Galxequests.json)
				2. Identify all required tasks for the current quest
				2. Extract the information for each task
				4. Complete each task methodically
				5. Verify completion
				6. Move to next quest

				DETAILED TASK EXECUTION:
				1. TASK IDENTIFICATION
				- Scan the entire quest page to identify all required tasks
				- Extract the task information including the task text and action required
				- Understand each task requirement before attempting completion

				2. TASK COMPLETION
				- For clickable tasks: Click directly on the task text (NOT surrounding elements) to be redirected
				- Example: For "Follow @Username on Twitter" - click specifically on this text
				- After completing each task action, IMMEDIATELY click the "Refresh" button located to the right of the task text
				- Wait for visual confirmation of task completion (green checkmark or similar indicator)

				3. PLATFORM-SPECIFIC INSTRUCTIONS:
				- Twitter/X tasks: Complete all following, liking, retweeting as directed
				- Link clicking tasks: Follow links and head back to the quest page to verify completion. There is no need to complete the
				specified task like "Sign up for an account" on the external site if it is from tasks that say "Visit the website" or something
				along those lines.
				- Q&A tasks: Provide accurate answers based on available information
				- Telegram tasks: Wait exactly 30 seconds after task initiation to allow manual completion
				- Discord tasks: Skip entirely and proceed to next task
				- All other platforms: Complete as directed without delay

				4. VERIFICATION PROTOCOL:
				- After completing each individual task, click the "Refresh" button
				- Before leaving any quest page, scroll through entire page to verify all tasks show completed status
				- If any task shows incomplete status, retry that specific task

				5. NAVIGATION:
				- After verifying all tasks are complete for current quest, return to Galxequests.json
				- Select next quest URL in sequence
				- Repeat process until all quests in json file are completed

				ERROR HANDLING:
				- If a task fails to register as complete after 3 refresh attempts, note the issue and proceed to next task
				- If redirection fails when clicking task text, try once more before reporting the issue

				CRITICAL REMINDER: ALWAYS click the "Refresh" button after completing each task to verify successful completion.
			""",
			llm=ClaudeAIModel,
			controller=controller,
			browser_context=context,
		)
		TaskVerificationAgent = Agent(
			task="""
				OBJECTIVE: Verify Completion Status of All Quests in Galxequests.json

				VERIFICATION PROCESS:
				1. Access each quest URL sequentially from Galxequests.json
				2. Perform thorough verification of all tasks within each quest
				3. Refresh incomplete tasks as needed
				4. Document verification results
				5. Proceed systematically through all quests

				DETAILED VERIFICATION PROTOCOL:
				1. INITIAL ASSESSMENT
				- Load quest page completely
				- Scroll through entire page from top to bottom to ensure all elements are visible
				- Identify all task elements requiring verification

				2. COMPLETION STATUS IDENTIFICATION
				- Verification indicators:
					• GREEN CIRCULAR CHECKMARK on right side of task = COMPLETED
					• GREEN BOX surrounding task text = COMPLETED
					• ABSENCE of green indicators = INCOMPLETE

				3. REFRESH PROCEDURE
				- ONLY for tasks WITHOUT green indicators:
					• Locate the "Refresh" button positioned on the right side of the task text
					• Click the refresh button ONCE
					• Wait 3 seconds for page response
					• Confirm whether green indicator appears after refresh

				4. COMPREHENSIVE VERIFICATION
				- After addressing individual incomplete tasks:
					• Scroll through entire page once more
					• Confirm ALL tasks display either a green checkmark or green box
					• Document any persistently incomplete tasks

				5. NAVIGATION SEQUENCE:
				- Once current quest verification is complete:
					• Return to Galxequests.json file
					• Select next quest URL in sequence
					• Repeat verification process for new quest

				COMPLETION CRITERIA:
				- All quests from Galxequests.json have been accessed
				- Every task within each quest shows a green completion indicator
				- Full documentation of any exceptions or incomplete tasks

				CRITICAL REQUIREMENTS:
				- ALWAYS scroll through entire page to ensure all tasks are visible
				- NEVER skip the refresh procedure for tasks without green indicators
				- ALWAYS perform a final verification scroll before proceeding to next quest
			""",
			llm=ClaudeAIModel,
			controller=controller,
			browser_context=context,
		)
			
		QuestCompletionAgent = Agent(
			task="""
				Quest Completion Check Workflow:
				Objective: Validate Quest Completion Status
				Process:

				Open first quest URL from Galxequests.json
				Status Check:

				Verify "Completed" or "Claimed" status
				If the quest is not completed, check for the presence of a "Claim", "Participate" or a button of similar nature.
				Press that button to complete the quest if it has not already been pressed.
				If a pop up appears that says "Claim Directly" press that button to complete the quest! Wait for 10 seconds for the pop up to appear. 

				If there is a timer on the raffle it means the quest is successfully completed.
				Navigation:

				If completed, return to Galxequests.json
				Proceed to next quest URL


				Repeat until all quests verified

				Key Focus:

				Systematic status confirmation
				Sequential quest processing
			""",
			llm=ClaudeAIModel,
			controller=controller,
			browser_context=context,
		)


		LoginCheckerAgenthistory = await LoginCheckerAgent.run()
		LoginCheckerAgenthistoryTokens = LoginCheckerAgenthistory.total_input_tokens()
		LoginCheckerAgenthistorytime = LoginCheckerAgenthistory.total_duration_seconds()
		print("Tokens used for LoginCheckerAgent:", LoginCheckerAgenthistoryTokens)
		print("Time taken for LoginCheckerAgent:", LoginCheckerAgenthistorytime)


		AlphaHunterAgenthistory = await AlphaHunterAgent.run()
		AlphaHunterAgenthistoryTokens = AlphaHunterAgenthistory.total_input_tokens()
		AlphaHunterAgenthistorytime = AlphaHunterAgenthistory.total_duration_seconds()
		print("Tokens used for AlphaHunterAgent:", AlphaHunterAgenthistoryTokens)
		print("Time taken for AlphaHunterAgent:", AlphaHunterAgenthistorytime)


		# TaskCompletionAgenthistory = await TaskCompletionAgent.run()
		# TaskCompletionAgenthistoryTokens = TaskCompletionAgenthistory.total_input_tokens()
		# TaskCompletionAgenthistorytime = TaskCompletionAgenthistory.total_duration_seconds()
		# print("Tokens used for TaskCompletionAgent:", TaskCompletionAgenthistoryTokens)
		# print("Time taken for TaskCompletionAgent:", TaskCompletionAgenthistorytime)


		# TaskCompletionAgenthistory = await TaskVerificationAgent.run()
		# TaskCompletionAgenthistoryTokens = TaskCompletionAgenthistory.total_input_tokens()
		# TaskCompletionAgenthistorytime = TaskCompletionAgenthistory.total_duration_seconds()
		# print("Tokens used for TaskVerificationAgent:", TaskCompletionAgenthistoryTokens)
		# print("Time taken for TaskVerificationAgent:", TaskCompletionAgenthistorytime)


		# QuestCompletionAgenthistory = await QuestCompletionAgent.run()
		# QuestCompletionAgenthistoryTokens = QuestCompletionAgenthistory.total_input_tokens()
		# QuestCompletionAgenthistorytime = QuestCompletionAgenthistory.total_duration_seconds()
		# print("Tokens used for QuestCompletionAgent:", QuestCompletionAgenthistoryTokens)
		# print("Time taken for QuestCompletionAgent:", QuestCompletionAgenthistorytime)

asyncio.run(main())


