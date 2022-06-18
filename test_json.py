import json
import unittest
from chat_socket.chat import process_convo_init_json, process_message_json

class JsonFormatTest(unittest.TestCase):
    # CONVO INIT    
    def test_process_convo_init_json_should_return_decode_error_given_non_json_string(self):
        non_json_string = "randomStringOfCharacters"
        init, e = process_convo_init_json(non_json_string)
        self.assertEqual(init, None)
        with self.assertRaises(json.decoder.JSONDecodeError):
            raise e
        return

    def test_process_convo_init_json_should_return_type_error_given_dict(self):
        dict_init = {
            "sender": 1,
            "receiver": 2,
        }
        init, e = process_convo_init_json(dict_init)
        self.assertEqual(init, None)
        with self.assertRaises(TypeError):
            raise e
        return

    def test_process_convo_init_json_should_return_key_error_given_no_type(self):
        no_type_init = {
            "sender": 1,
            "receiver": 2,
        }
        init, e = process_convo_init_json(json.dumps(no_type_init))
        self.assertEqual(init, None)
        with self.assertRaises(KeyError):
            raise e
        return

    def test_process_convo_init_json_should_return_key_error_given_no_sender(self):
        no_sender_init = {
            "type": "init",
            "receiver": 2,
        }
        init, e = process_convo_init_json(json.dumps(no_sender_init))
        self.assertEqual(init, None)
        with self.assertRaises(KeyError):
            raise e
        return

    def test_process_convo_init_json_should_return_key_error_given_no_receiver(self):
        no_receiver_init = {
            "type": "init",
            "sender": 1,
        }
        init, e = process_convo_init_json(json.dumps(no_receiver_init))
        self.assertEqual(init, None)
        with self.assertRaises(KeyError):
            raise e
        return

    def test_process_convo_init_json_should_return_error_given_non_init_type(self):
        non_init_type_init = {
            "type": "message",
            "sender": 1,
            "receiver": 2,
        }
        init, e = process_convo_init_json(json.dumps(non_init_type_init))
        self.assertEqual(init, None)
        with self.assertRaises(AssertionError):
            raise e
        return

    def test_process_convo_init_json_should_return_init_given_type_sender_and_receiver(self):
        no_type_init = {
            "type": "init",
            "sender": 1,
            "receiver": 2,
        }
        init, e = process_convo_init_json(json.dumps(no_type_init))
        self.assertEqual(init, no_type_init)
        self.assertIsNone(e)
        return

    # MESSAGE
    def test_process_message_json_should_return_error_given_non_json_string(self):
        non_json_string = "randomStringOfCharacters"
        message_json, e = process_message_json(non_json_string)
        self.assertEqual(message_json, None)
        with self.assertRaises(json.decoder.JSONDecodeError):
            raise e
        return

    def test_process_message_json_should_return_type_error_given_dict(self):
        message_dict = {
            "type": "message",
            "sender": 1,
            "receiver": 2,
            "body": "fakeBody",
            "token": "123455667",
        }
        message_json, e = process_message_json(message_dict)
        self.assertEqual(message_json, None)
        with self.assertRaises(TypeError):
            raise e
        return
    
    def test_process_message_json_should_return_key_error_given_no_type(self):
        no_type_json = {
            "sender": 1,
            "receiver": 2,
            "body": "fakeBody",
            "token": "123455667",
        }
        message_json, e = process_message_json(json.dumps(no_type_json))
        self.assertEqual(message_json, None)
        with self.assertRaises(KeyError):
            raise e
        return

    def test_process_message_json_should_return_key_error_given_no_sender(self):
        no_sender_json = {
            "type": "message",
            "receiver": 2,
            "body": "fakeBody",
            "token": "123455667",
        }
        message_json, e = process_message_json(json.dumps(no_sender_json))
        self.assertEqual(message_json, None)
        with self.assertRaises(KeyError):
            raise e
        return

    def test_process_message_json_should_return_key_error_given_no_receiver(self):
        no_receiver_json = {
            "type": "message",
            "sender": 1,
            "body": "fakeBody",
            "token": "123455667",
        }
        message_json, e = process_message_json(json.dumps(no_receiver_json))
        self.assertEqual(message_json, None)
        with self.assertRaises(KeyError):
            raise e
        return

    def test_process_message_json_should_return_error_given_non_message_type(self):
        non_message_type_json = {
            "type": "init",
            "sender": 1,
            "receiver": 2,
            "body": "fakeBody",
            "token": "123455667",
        }
        message_json, e = process_message_json(json.dumps(non_message_type_json))
        self.assertEqual(message_json, None)
        with self.assertRaises(AssertionError):
            raise e
        return

    def test_process_message_json_should_return_message_json_given_all_fields(self):
        message_json = {
            "type": "message",
            "sender": 1,
            "receiver": 2,
            "body": "fakeBody",
            "token": "123455667",
        }
        valid_message_json, e = process_message_json(json.dumps(message_json))
        self.assertEqual(valid_message_json, message_json)
        self.assertIsNone(e)
        return


if __name__ == '__main__':
    unittest.main()