import asyncio
import json
import websockets
import os

PORT = int(os.environ["PORT"])
MANY = 50

USER_1 = {
    "ID": 1,
    "TOKEN": "eb622f9ac993c621391de3418bc18f19cb563a61"
}

USER_2 = {
    "ID": 6,
    "TOKEN": "df3b32643068fb94041e54bb316957476d265beb"
}

WEBSOCKET_URL = f"ws://localhost:{PORT}"

async def start_conversation(websocket, sender, receiver):
    convo_init_dict = {
        "type": "init",
        "sender": sender,
        "receiver": receiver,
    }
    convo_init_json = json.dumps(convo_init_dict)
    await websocket.send(convo_init_json)

async def validate_conversation(websocket):
    response_string = await websocket.recv()
    response_dict = json.loads(response_string)
    try:
        assert response_dict["type"] == "success"
    except AssertionError:
        raise AssertionError(response_dict)

async def send_test_message(websocket, sender, receiver, token):
    message_dict = {
        "type": "message",
        "sender": sender, 
        "receiver": receiver,
        "body": "This text message is for testing purposes only.",
        "token": token,
    }
    message_json = json.dumps(message_dict)
    await websocket.send(message_json)

async def receive_test_message(websocket, receiver):
    response_string = await websocket.recv()
    response_dict = json.loads(response_string)
    try:
        assert response_dict["type"] == "message"
        assert response_dict["receiver"] == receiver
    except AssertionError:
        raise AssertionError(response_dict)

async def test_user_1_joins_then_leaves():
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        await start_conversation(websocket, USER_1["ID"], USER_2["ID"])
        await validate_conversation(websocket)

async def test_user_1_joins_then_sends_then_leaves():
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        await start_conversation(websocket, USER_1["ID"], USER_2["ID"])
        await validate_conversation(websocket)
        await send_test_message(websocket, USER_1["ID"], USER_2["ID"], USER_1["TOKEN"])
    
async def test_user_1_joins_then_sends_then_receives_then_leaves():
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        await start_conversation(websocket, USER_1["ID"], USER_2["ID"])
        await validate_conversation(websocket)
        await send_test_message(websocket, USER_1["ID"], USER_2["ID"], USER_1["TOKEN"])
        await receive_test_message(websocket, USER_2["ID"])

        async with websockets.connect(WEBSOCKET_URL) as websocket2:
            await start_conversation(websocket2, USER_2["ID"], USER_1["ID"])
            await validate_conversation(websocket2)
            await send_test_message(websocket2, USER_2["ID"], USER_1["ID"], USER_2["TOKEN"])

        await receive_test_message(websocket, USER_1["ID"])

async def test_user_1_joins_then_sends_many_messages_then_receives_then_leaves():
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        await start_conversation(websocket, USER_1["ID"], USER_2["ID"])
        await validate_conversation(websocket)

        async with websockets.connect(WEBSOCKET_URL) as websocket2:
            await start_conversation(websocket2, USER_2["ID"], USER_1["ID"])
            await validate_conversation(websocket2)

            for i in range(MANY):
                await send_test_message(websocket, USER_1["ID"], USER_2["ID"], USER_1["TOKEN"])
                await receive_test_message(websocket, USER_2["ID"])
                await receive_test_message(websocket2, USER_2["ID"])

async def run_tests():
    tests = [
        test_user_1_joins_then_leaves, 
        test_user_1_joins_then_sends_then_leaves,
        test_user_1_joins_then_sends_then_receives_then_leaves,
        test_user_1_joins_then_sends_many_messages_then_receives_then_leaves,
    ]
    for test in tests:
        print(f'{test.__name__}...', end='')
        try: 
            await test()
        except Exception as e:
            print('FAIL')
            print(e)
            continue
        print('PASS')

asyncio.get_event_loop().run_until_complete(run_tests())