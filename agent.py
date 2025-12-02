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

# -----------------------------
# Tool Functions
# -----------------------------
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

# -----------------------------
# Tools
# -----------------------------
tools = [
    Tool(
        name="CreateTicket",
        func=add_ticket,
        description=(
            'Creates a new ticket. '
            'Input JSON Format:\n'
            '{"type": "task", "title": "Title", "description": "Details", "action": "Next", "messages": ["msg"]}'
        )
    ),
    Tool(
        name="UpdateTicket",
        func=append_message_tool,
        description=(
            'Updates an existing ticket. '
            'Input JSON Format:\n'
            '{"ticket_id": "507f1...", "message": "Update text"}'
        )
    )
]

# -----------------------------
# ReAct Prompt
# -----------------------------
template = """Answer the following questions as best you can. You have access to the following tools:

RULES (IMPORTANT):
- You MUST call EXACTLY ONE tool per user request.
- NEVER call any tool more than once.
- After you call a tool and receive its Observation, STOP and produce Final Answer.
- Do NOT repeat or retry tool calls.

{tools}

Use the following format:

Question: the input question you must answer
Thought: think step-by-step about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action (must be valid JSON)
Observation: the result of the action
... repeat Thought/Action/Action Input/Observation if needed ...
Thought: I now know the final answer
Final Answer: the final answer

EXISTING TICKETS:
{tickets}

Question: {input}
{agent_scratchpad}
"""

prompt = PromptTemplate(
    template=template,
    input_variables=["input", "tickets", "agent_scratchpad", "tools", "tool_names"]
)

# -----------------------------
# LLM
# -----------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0
)

# -----------------------------
# Agent + Executor
# -----------------------------
agent = create_react_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=1,
    return_intermediate_steps=True
)

# -----------------------------
# PROCESS MESSAGE
# -----------------------------

def serialize_steps(steps):
    serializable = []
    for action, observation in steps:
        serializable.append({
            "thought": action.log,
            "action": action.tool,
            "action_input": action.tool_input,
            "observation": observation
        })
    return serializable

def process_message(user_message: str) -> dict:
    try:
        # Fetch existing tickets
        tickets = get_documents_id_and_description()
        tickets_text = "\n".join(
            f"- ID: {t['_id']} | Title: {t.get('title','N/A')} | Desc: {t.get('description','')[:60]}"
            for t in tickets
        ) if tickets else "No tickets yet"

        enhanced_input = f"""
Analyze this message: "{user_message}"

Rules:
1. If this is a NEW task, reminder, or follow-up → use CreateTicket
2. If this UPDATES an existing ticket → use UpdateTicket
3. Classify type as: task, reminder, follow-up, other
4. Provide clear title/description
5. Tool input MUST be valid JSON
"""

        result = agent_executor.invoke({
            "input": enhanced_input,
            "tickets": tickets_text
        })

        steps = serialize_steps(raw["intermediate_steps"])

        # ReAct agents output under "output"
        return {"status": "success", "output": result["output"]}

    except Exception as e:
        return {"status": "error", "output": f"Agent error: {str(e)}"}


# -----------------------------
# TEST
# -----------------------------
if __name__ == "__main__":
    test_messages = [
        "Create task: Prepare Q4 presentation for the board",
        "Reminder: Backup the database every month end",
    ]

    for msg in test_messages:
        print("\n" + "="*60)
        print("Message:", msg)
        print("="*60)
        result = process_message(msg)
        print("Status:", result["status"])
        print("Output:", result["output"])
