import json, os
from langchain.agents import initialize_agent, Tool, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from db import create_ticket, append_message_to_DB, get_documents_id_and_description
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

def add_ticket(args: str) -> str:
    try:
        data = json.loads(args)
        ticket_id = create_ticket(
            type=data.get("type", "other"),
            title=data.get("title", ""),
            description=data.get("description", ""),
            action=data.get("action", ""),
            messages=data.get("messages", [])
        )
        return f"Ticket created: {ticket_id}"
    except Exception as e:
        return f"AddTicket error: {e}"

def append_message(args: str) -> str:
    try:
        data = json.loads(args)
        modified_count = append_message_to_DB(
            doc_id=ObjectId(data["ticket_id"]),
            new_message=data["message"]
        )
        return f"Message appended, modified_count: {modified_count}"
    except Exception as e:
        return f"AppendMessage error: {e}"

tools = [
    Tool(name="AddTicket", func=add_ticket, description="Create a new ticket using JSON input."),
    Tool(name="AppendMessage", func=append_message, description="Append a message to an existing ticket using JSON input.")
]

chat_model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2 # Controls creativity/randomness
)

agent = initialize_agent(
    tools=tools,
    llm=chat_model,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, # Reasoning and Acting Loop 
    verbose=False,
    max_iterations=3,
    handle_parsing_errors=True
)

def process_message(user_message: str) -> str:
    prev_tickets = get_documents_id_and_description()
    tickets_summary = ""
    if prev_tickets:
        tickets_summary = "\n".join([
            f"Ticket ID: {str(t['_id'])} | Description: {t.get('description', '')}"
            for t in prev_tickets
        ])
    else:
        tickets_summary = "No previous tickets."

    prompt = f"""
        You are a Smart Follow-Up Assistant. A user sent the following message:

        "{user_message}"

        Previous tickets:
        {tickets_summary}

        Decide whether:
        1. This message requires creating a new ticket (use AddTicket tool)
        2. This message should be appended to an existing ticket (use AppendMessage tool)

        Return a JSON object in one of these formats:

        # If creating a new ticket:
        {{
        "tool": "AddTicket",
        "args": {{
            "type": "follow-up / reminder / task / other",
            "title": "Short title for ticket",
            "description": "Detailed description",
            "action": "Suggested next action",
            "messages": ["{user_message}"]
        }}
        }}

        # If appending to an existing ticket:
        {{
        "tool": "AppendMessage",
        "args": {{
            "ticket_id": "<ID of the existing ticket>",
            "message": "summary of new message"
        }}
        }}
    """

    try:
        response = agent.invoke({"input": prompt})

        if isinstance(response, dict):
            agent_output = response.get("output", "")
        else:
            agent_output = str(response)

        try:
            action_json = json.loads(agent_output)
        except json.JSONDecodeError:
            return f"⚠️ Couldn't parse agent output as JSON: {agent_output}"

        return str(action_json)

    except Exception as e:
        return f"Error processing message: {e}"

if __name__ == "__main__":
    messages = [
        "Task: Prepare the presentation for the board meeting.",
        "Reminder: backup all databases at the end of each month.",
        "Follow-up: Get feedback from the finance team about the expense report."
    ]

    for msg in messages:
        result = process_message(msg)
        print(f"Message: {msg}")
        print(f"Agent Output: {result}")
        print("-" * 80)