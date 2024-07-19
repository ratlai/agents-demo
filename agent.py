from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from langchain.utilities.tavily_search import TavilySearchAPIWrapper
import os
import logging
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_experimental.tools import PythonREPLTool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv

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
gmail_tools = []

# Conditionally add Gmail tools if credentials file exists
if os.path.exists('credentials.json'):
    from langchain_community.agent_toolkits import GmailToolkit
    gmail_toolkit = GmailToolkit()
    gmail_tools = gmail_toolkit.get_tools()

python_tools = [PythonREPLTool()]

# Combine all tools
ratl_tools = [
    tavily_tool,
    *gmail_tools,
    *python_tools
]

llm_with_tools = llm.bind_tools(ratl_tools)

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are Ratl, an intelligent agent responsible for handling all user queries directly and performing tasks using various integrated tools. Always respond to the user in a conversational tone, and ensure all interactions are clear and helpful."
        ),
        MessagesPlaceholder(variable_name=MEMORY_KEY),
        ("user", "{input}"),
        ("assistant", "I will take care of this for you."),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)
ratl_agent = {
    "input": lambda x: x["input"],
    "agent_scratchpad": lambda x: format_to_openai_tool_messages(x["intermediate_steps"]),
    MEMORY_KEY: lambda x: x[MEMORY_KEY],
} | prompt_template | llm_with_tools | OpenAIToolsAgentOutputParser()

ratl_agent_executor = AgentExecutor(agent=ratl_agent, tools=ratl_tools, verbose=True, handle_parsing_errors=True)

# Function to handle the delegation
def delegate_task(user_input: str):
    session = get_user_session(os.getenv('USER_EMAIL'))
    session[MEMORY_KEY].append({"role": "user", "content": user_input})
    
    try:
        response = ratl_agent_executor.invoke({
            "input": user_input,
            MEMORY_KEY: session[MEMORY_KEY],
            "agent_scratchpad": []
        })

        logging.info('DEBUG agent response:', response)
        
        response_str = response["output"]
        session[MEMORY_KEY].append({"role": "assistant", "content": response_str})
        return response_str
    except Exception as e:
        logging.error(f"General Exception: {e}")
        fallback_message = "An unexpected error occurred, please try again."
        session[MEMORY_KEY].append({"role": "assistant", "content": fallback_message})
        return fallback_message
