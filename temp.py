from src.agentCRS.builder import build_single_agent
from src.multiAgentCRS.utils import save_graph_image

save_graph_image(build_single_agent().graph, "data/agent_graph.png")

# from src.multiAgentCRS.graph.builder import build_multi_agent_graph
# from src.multiAgentCRS.utils.chat import start_chat
# from src.multiAgentCRS.utils import save_graph_image

# graph = build_multi_agent_graph()

# import uuid
# import asyncio

# async def get_response(message):
#     config = {
#         "configurable": {
#             "thread_id": str(uuid.uuid4()),
#             "user_id": "123"  # new_user_id
#         }
#     }
    
#     response = await graph.ainvoke(
#         {"messages": ("user", message)}, 
#         config, 
#     )
#     return response

# async def chat_loop():
#     _printed = set()
    
#     while True:
#         question = input("Enter your message (or 'q' to quit): ")
#         if question.lower() == 'q':
#             break
            
#         # try:
#         event = await get_response(question)
#         print(event["messages"][-1].content)
#         # except Exception as e:
#         #     print(f"Error: {e}")

# # Run the async loop
# if __name__ == "__main__":
#     asyncio.run(chat_loop())


# # save_graph_image(graph)
# # import uuid

# # thread_id = str(uuid.uuid4())
# # old_user_id = "A30Q8X8B1S3GGT"
# # new_user_id = "123"

# # config = {
# #     "configurable": {
# #         "thread_id": thread_id,
# #         "user_id": new_user_id
# #     }
# # }

# # start_chat(graph, config)

# # from src.utils.fetch_data import get_user_data

# # print(get_user_data("A30Q8X8B1S3GGT"))

# from src.common.config import load_config
# from src.infrastructure.search_engine.faiss import FAISS_Search
# config = load_config()

# ss = FAISS_Search()
# print("\n".join([d[0].page_content for d in ss.search("User is looking for movies similar to The Shawshank Redemption and Seven.").response]))
