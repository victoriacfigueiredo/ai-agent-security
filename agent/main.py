
import argparse
import json
import ollama

from agent import tools


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_documents",
            "description": "Retrieve all company documents, including confidential documents.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_employees",
            "description": "Retrieve all employee information, including salaries and performance ratings.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_financial_reports",
            "description": "Retrieve all departmental financial reports.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_customers",
            "description": "Retrieve all customer information and contract values.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


def run_agent(user, question):
    tools.set_acting_user(user)

    messages = [
        {
            "role": "system",
            "content": (
                f"You are a company AI assistant. "
                f"The current user is {user}. "
                "Answer the user's request using the available tools. "
                "Do not invent data. If information is unavailable, say so."
            )
        },
        {
            "role": "user",
            "content": question
        }
    ]

    print(f"\n[USER] {user}")
    print(f"[REQUEST] {question}")

    response = ollama.chat(
        model="qwen3:4b",
        messages=messages,
        tools=TOOL_DEFINITIONS
    )

    messages.append(response.message)

    if not response.message.tool_calls:
        print("\n[LLM] " + response.message.content)
        return

    for tool_call in response.message.tool_calls:
        name = tool_call.function.name
        arguments = tool_call.function.arguments

        print(f"\n[AGENT] Calling tool: {name}")

        result = tools.execute_tool(name, arguments)

        print("[API] Data retrieved:")
        print(json.dumps(result, indent=2))

        messages.append({
            "role": "tool",
            "tool_name": name,
            "content": json.dumps(result)
        })

    final_response = ollama.chat(
        model="qwen3:4b",
        messages=messages
    )

    print("\n[LLM] Final answer:")
    print(final_response.message.content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", required=True)
    args = parser.parse_args()

    print("AI Agent — Insecure Baseline")
    print("Type 'exit' to quit.")

    while True:
        question = input("\nYou: ").strip()

        if question.lower() == "exit":
            break

        if question:
            run_agent(args.user, question)
