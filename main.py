from langchain_anthropic import ChatAnthropic
from browser_use import Agent
import asyncio
from dotenv import load_dotenv
load_dotenv()

task = """
   ### Prompt for Github robot

**Objective:**
Visit [Github vllm mainpage](https://github.com/vllm-project/vllm), click pull requests, get all content and save these content as csv file.

"""

async def main():
    agent = Agent(
        task=task,
        llm=ChatAnthropic(model="claude-3-7-sonnet-20250219"),
    )
    await agent.run()

asyncio.run(main())