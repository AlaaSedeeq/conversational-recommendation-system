from src.common.config import load_config

CONFIG = load_config()

async def fetch_user_information(
    state, 
    config
):
    print(); print("Current Node: Fetch User Info")
    configuration = config.get("configurable", {})
    user_id = configuration.get("user_id", None)

    user_data = {}
    
    if not user_id:
        return {
            "user_context": {
                "user_data": user_data, 
                "user_exists": False,
            },
        }
    
    try:
        from src.utils.tools import read_dialogue, read_user_data, read_jsonl, read_json, get_conversation_by_id

        final_data_path = CONFIG.data.final_data
        Conversation_path = CONFIG.data.conversations
        user_map_path = CONFIG.data.user_map
        item_map_path = CONFIG.data.item_map
        
        item_map = read_json(item_map_path)
        user_map = read_json(user_map_path)
        Conversation = read_dialogue(Conversation_path)

        if user_id in user_map:
            user_information = read_user_data(final_data_path, user_id)
            history_interaction = user_information['history_interaction']
            user_might_likes = user_information['user_might_like']
        
            user_data = {
                    "history_interaction": [item_map[history_interaction[k]] for k in range(len(history_interaction))],
                    "user_might_like": [item_map[user_might_likes[k]] for k in range(len(user_might_likes))],
                    "conversations": ""
                }
            Conversation_info = user_information['Conversation']
            for j in range(len(Conversation_info)):
                per_conversation_info = Conversation_info[j]['conversation_{}'.format(j + 1)]
                user_likes_id = per_conversation_info['user_likes']
                user_dislikes_id = per_conversation_info['user_dislikes']
                rec_item_id = per_conversation_info['rec_item']
                conversation_id = per_conversation_info['conversation_id']
                dialogue = get_conversation_by_id(Conversation, conversation_id)
                user_data['conversations'] += "==================================\n\n" + dialogue
        
            return {
                "user_context": {
                    "user_data": user_data, 
                    "user_exists": True,
                },
            }

        return {
            "user_context": {
                "user_data": user_data, 
                "user_exists": False,
            },
        }

    except Exception as e:
        print(e)
        return {
            "user_context": {
                "user_data": user_data, 
                "user_exists": False,
            },
        }
