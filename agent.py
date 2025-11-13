import json
import os
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from db import create_ticket, append_message_to_DB, get_documents_id_and_description
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

# Tool Functions
def add_ticket(json_input: str) -> str:
    """Create a new ticket."""
    try:
        data = json.loads(json_input)
        ticket_id = create_ticket(
            type=data.get("type", "other"),
            title=data.get("title", "Untitled"),
            description=data.get("description", ""),
            action=data.get("action", ""),
            messages=data.get("messages", [])
        )
        return f"SUCCESS: Ticket created with ID {ticket_id}"
    except Exception as e:
        return f"ERROR: {str(e)}"

def append_message_tool(json_input: str) -> str:
    """Append message to existing ticket."""
    try:
        data = json.loads(json_input)
        append_message_to_DB(
            doc_id=ObjectId(data["ticket_id"]),
            new_message=data["message"]
        )
        return f"SUCCESS: Message appended to ticket {data['ticket_id']}"
    except Exception as e:
        return f"ERROR: {str(e)}"

# Define Tools
tools = [
    Tool(
        name="CreateTicket",
        func=add_ticket,
        description='Creates a new ticket. Input must be valid JSON: {"type": "task", "title": "Title here", "description": "Details", "action": "Next step", "messages": ["msg"]}'
    ),
    Tool(
        name="UpdateTicket",
        func=append_message_tool,
        description='Appends message to existing ticket. Input must be valid JSON: {"ticket_id": "507f1f77bcf86cd799439011", "message": "Update text"}'
    )
]

# React Prompt Template
template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action (must be valid JSON)
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

EXISTING TICKETS:
{tickets}

Question: {input}
Thought:{agent_scratchpad}"""

prompt = PromptTemplate.from_template(template)

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0
)

# Create Agent
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=4
)

def process_message(user_message: str) -> dict:
    """
    Process message using agent with tools.
    Returns: {"status": "success/error", "output": str}
    """
    try:
        # Get existing tickets
        tickets = get_documents_id_and_description()
        tickets_text = "\n".join([
            f"- ID: {t['_id']} | Title: {t.get('title', 'N/A')} | Desc: {t.get('description', '')[:60]}"
            for t in tickets
        ]) if tickets else "No tickets yet"
        
        # Enhanced input with instructions
        enhanced_input = f"""Analyze this message: "{user_message}"

Instructions:
1. If this is a NEW task/reminder/follow-up, use CreateTicket tool
2. If this UPDATES an existing ticket, use UpdateTicket tool
3. Classify type as: task, reminder, follow-up, or other
4. Provide clear title and description
5. Use valid JSON for tool inputs

Decide and take action now."""
        
        # Run agent
        result = agent_executor.invoke({
            "input": enhanced_input,
            "tickets": tickets_text
        })
        
        return {
            "status": "success",
            "output": result["output"]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "output": f"Agent error: {str(e)}"
        }

# Test
if __name__ == "__main__":
    test_messages = [
        "Create task: Prepare Q4 presentation for board meeting",
        "Reminder: Backup databases every month end",
    ]
    
    for msg in test_messages:
        print(f"\n{'='*60}")
        print(f"Message: {msg}")
        print('='*60)
        result = process_message(msg)
        print(f"\nStatus: {result['status']}")
        print(f"Output: {result['output']}")