import asyncio
import signal
from time import time

import websockets
import json
import requests
from decouple import config
import os

# two-dimensional, two conversation participants
CONVERSATION_BETWEEN = {}

REQUESTS_URL = os.environ["URL"]

def process_convo_init_json(convo_init_json):
    try:
        valid_convo_init_obj = json.loads(convo_init_json)
        assert valid_convo_init_obj["type"] == "init"
        assert valid_convo_init_obj["sender"] != None
        assert valid_convo_init_obj["receiver"] != None
        return valid_convo_init_obj, None
    except json.decoder.JSONDecodeError as e:
        return None, e
    except KeyError as e:
        return None, e
    except TypeError as e:
        return None, e
    except AssertionError as e:
        return None, e

def process_message_json(message_json):
    try:
        valid_message_obj = json.loads(message_json)
        assert valid_message_obj["type"] == "message"
        assert valid_message_obj["sender"] != None
        assert valid_message_obj["receiver"] != None
        assert valid_message_obj["body"] != None
        assert valid_message_obj["token"] != None
        return valid_message_obj, None
    except json.decoder.JSONDecodeError as e:
        return None, e
    except KeyError as e:
        return None, e
    except TypeError as e:
        return None, e
    except AssertionError as e:
        return None, e

async def error(websocket, message):
    event = {
        "type": "error",
        "message": message,
    }
    print(event)
    await websocket.send(json.dumps(event))

async def success(websocket, message):
    event = {
        "type": "success",
        "message": message,
    }
    print(event)
    await websocket.send(json.dumps(event))

async def execute_conversation(websocket, connected):
    """
    Receive and process messages from a user.
    """
    async for message in websocket:
        # Load JSON of the event
        valid_message_obj, e = process_message_json(message)
        # If improperly formatted, throw back error
        if not valid_message_obj:
            await error(websocket,
            f"Improperly formatted message... JSON Error: {e}")
        else: 
            token = valid_message_obj.pop("token")
            valid_message_obj["timestamp"] = time()
            print(valid_message_obj)
            # Post to database
            r = requests.post(
                REQUESTS_URL, 
                data=valid_message_obj, 
                headers={
                    'Authorization': f'Token {token}'
                })
            if r.status_code > 200 and r.status_code < 299:
                # Broadcast to all connected sockets
                valid_message_obj['id'] = r.data.get('id')
                websockets.broadcast(connected, json.dumps(valid_message_obj))
            else:
                await error(websocket,
                f"Could not POST message to database... {r.text}")

async def start_conversation(websocket, user1, user2):
    if user1 not in CONVERSATION_BETWEEN: CONVERSATION_BETWEEN[user1] = {}
    try:
        CONVERSATION_BETWEEN[user1][user2] = {websocket}
        await success(websocket, f"Beginning conversation between {user1} and {user2}")
        await execute_conversation(websocket, CONVERSATION_BETWEEN[user1][user2])
    finally:
        CONVERSATION_BETWEEN[user1][user2].remove(websocket)
        if not CONVERSATION_BETWEEN[user1][user2]:
            del CONVERSATION_BETWEEN[user1][user2]

async def join_conversation(websocket, user1, user2):
    try:
        CONVERSATION_BETWEEN[user1][user2].add(websocket)
        await success(websocket, f"Joining conversation between {user1} and {user2}")
        await execute_conversation(websocket, CONVERSATION_BETWEEN[user1][user2])
    finally:
        CONVERSATION_BETWEEN[user1][user2].remove(websocket)
        if not CONVERSATION_BETWEEN[user1][user2]:
            del CONVERSATION_BETWEEN[user1][user2]

async def handler(websocket):
    """
    Handle a connection and dispatch it according to who is connecting.
    """
    convo_init_json = await websocket.recv()
    valid_convo_init_obj, e = process_convo_init_json(convo_init_json)
    # Only process valid conversation initalization requests
    if not valid_convo_init_obj:
        await error(websocket, f"Could not instantiate conversation... JSON Error: {e}")
        return
    
    # To standardize the socket indexing, 
    # the user earlier in the alphabet will be the first layer
    # the user later in the alphabet will be the second layer
    users = [valid_convo_init_obj["sender"], valid_convo_init_obj["receiver"]]
    users.sort()
    user1, user2 = users
    # Either start or join a conversation
    conversation_started = (user1 in CONVERSATION_BETWEEN and 
                            user2 in CONVERSATION_BETWEEN[user1] and 
                            CONVERSATION_BETWEEN[user1][user2])
    if conversation_started: await join_conversation(websocket, user1, user2)
    else: await start_conversation(websocket, user1, user2)

async def main():
    # Set the stop condition when receiving SIGTERM.
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
    
    async with websockets.serve(handler, host="", port=int(os.environ["PORT"])):
        await stop

if __name__ == "__main__":
    asyncio.run(main())