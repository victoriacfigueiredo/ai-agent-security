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


def run_agent(question):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a company AI assistant operating as the "
                "machine client ai-agent. Answer using the available "
                "tools. Do not invent data. If information is unavailable, "
                "say so."
            )
        },
        {
            "role": "user",
            "content": question
        }
    ]

    print(f"\n[REQUEST] {question}")

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

        print("[API] Result:")
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
    print("AI Agent — Stage 2 OAuth2")
    print("Authenticated as machine client: ai-agent")
    print("Type 'exit' to quit.")

    while True:
        question = input("\nYou: ").strip()

        if question.lower() == "exit":
            break

        if question:
            run_agent(question)
