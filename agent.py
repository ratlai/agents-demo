from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from langchain.utilities.tavily_search import TavilySearchAPIWrapper
import os
import logging
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_community.agent_toolkits import GmailToolkit
import json
from prompts import prompt_template, MEMORY_KEY
from dotenv import load_dotenv
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_experimental.tools import PythonREPLTool

load_dotenv()

logging.basicConfig(level=logging.INFO)

# Initialize state in terms of memory or session data
user_sessions = {}

# Define the memory key for chat history
MEMORY_KEY = "internal_chat_history"

# Function to get or create user session
def get_user_session(user_email):
    if user_email not in user_sessions:
        user_sessions[user_email] = {
            "internal_chat_history": [],
            "first_name": user_email.split('@')[0].capitalize()
        }
    return user_sessions[user_email]

llm = ChatOpenAI(api_key=os.getenv('OPENAI_API_KEY'), model=os.getenv('MODEL'), streaming=True)

# Define the agent with memory and prompt template
search = TavilySearchAPIWrapper()
tavily_tool = TavilySearchResults(api_wrapper=search)
gmail_toolkit = GmailToolkit()
gmail_tools = gmail_toolkit.get_tools()
pyhon_tools = [PythonREPLTool()]

# requests_tools = load_tools(["requests_all"], allow_dangerous_tools=True)
# request_tools_dict = {tool.name: tool for tool in requests_tools}
pyhon_tools_dict = {tool.name: tool for tool in pyhon_tools}

bujji_tools = [
    tavily_tool,
    *gmail_tools,
    # *requests_tools,
    *pyhon_tools
]

llm_with_tools = llm.bind_tools(bujji_tools)

bujji_agent = {
    "input": lambda x: x["input"],
    "agent_scratchpad": lambda x: format_to_openai_tool_messages(x["intermediate_steps"]),
    MEMORY_KEY: lambda x: x[MEMORY_KEY],
} | prompt_template | llm_with_tools | OpenAIToolsAgentOutputParser()

bujji_agent_executor = AgentExecutor(agent=bujji_agent, tools=bujji_tools, verbose=True)

# Function to handle the delegation based on the Task Manager's intelligent decision
def delegate_task(user_input: str):
    session = get_user_session(os.getenv('USER_EMAIL'))
    session[MEMORY_KEY].append({"role": "user", "content": user_input})
    
    try:
        response = bujji_agent_executor({
            "input": user_input,
            MEMORY_KEY: session[MEMORY_KEY],
            "agent_scratchpad": []
        })

        logging.info('DEBUG agent response:', response)
        
        response_str = response["output"].replace('```json', '').replace('```', '').strip()
            
        try:
            response_json = json.loads(response_str)
            for item in response_json:
                role = "assistant" if item["agent"] != "USER" else "user"
                content = item["response"]
                if not isinstance(content, str):
                    content = str(content)
                session[MEMORY_KEY].append({"role": role, "content": item["response"]})
            return response_json
        except json.JSONDecodeError:
            if response_str:
                fallback_message = [{"agent": "Bujji", "response": response_str}]
            else:
                fallback_message = [{"agent": "Bujji", "response": "Can you tell again, I did not get you."}]
            session[MEMORY_KEY].append({"role": "assistant", "content": fallback_message[0]["response"]})
            return fallback_message
    except Exception as e:
        logging.error(f"General Exception: {e}")
        fallback_message = [
            {"agent": "Bujji", "response": "An unexpected error occurred, please try again."}
        ]
        session[MEMORY_KEY].append({"role": "assistant", "content": fallback_message[0]["response"]})
        return fallback_message
