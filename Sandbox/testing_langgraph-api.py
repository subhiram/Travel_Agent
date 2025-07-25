# import asyncio
# from langgraph_sdk import get_client
# from langgraph_sdk.schema import Command
# from langchain_core.messages import HumanMessage

# async def main():
#     client = get_client(url="http://127.0.0.1:2024")

#     assistant_id = "agent"

#     # create a thread
#     thread = await client.threads.create()
#     thread_id = thread["thread_id"]

#     # Run the graph until the interrupt is hit.
#     result = await client.runs.wait(
#         thread_id,
#         assistant_id,
#         input={"messages": [HumanMessage(content="Hello, I want to plan a trip to London")]}   
#     )
#     print("result: ", result)
#     print(result['__interrupt__']) 

#     # Resume the graph
#     resumed = await client.runs.wait(
#         thread_id,
#         assistant_id,
#         command=Command(resume="Edited text")   
#     )
#     print(resumed)

# # Run the async main
# if __name__ == "__main__":
#     asyncio.run(main())


import asyncio
from langgraph_sdk import get_client
from langgraph_sdk.schema import Command
from langchain_core.messages import HumanMessage
import pprint

async def main():
    client = get_client(url="http://127.0.0.1:2024")
    assistant_id = "agent"

    # Step 1: Create a thread
    thread = await client.threads.create()
    thread_id = thread["thread_id"]
    print(f"[🧵] Created thread: {thread_id}")

    # Step 2: Start the graph
    result = await client.runs.wait(
        thread_id,
        assistant_id,
        input={"messages": [HumanMessage(content="I want to go to Paris next month for a vacation")]}
    )

    pprint.pprint(result)

    # Step 3: If an interrupt is triggered (via `interrupt()` in your tool), handle it
    if "__interrupt__" in result:
        print("\n[⚠️ INTERRUPT] Human input required")
        interrupt_info = result["__interrupt__"]
        pprint.pprint(interrupt_info)

        # Step 4: Simulate user response (replace this with actual UI input if needed)
        simulated_human_response = "Yes, my destination is Paris"

        # The resume command format must match your tool response schema (usually a dict with "args")
        response_args = {"args": {"question": simulated_human_response}}

        # Step 5: Resume the graph
        resumed = await client.runs.wait(
            thread_id,
            assistant_id,
            command=Command(resume=response_args)
        )

        print("\n[✅ RESUMED] Final result:")
        pprint.pprint(resumed)
    else:
        print("\n[✅] No interrupt. Final result:")
        pprint.pprint(result)

if __name__ == "__main__":
    asyncio.run(main())

