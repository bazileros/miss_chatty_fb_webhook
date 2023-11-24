import unittest
from unittest.mock import patch
from app import app, call_send_api, handle_message

class TestApp(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_call_send_api(self):
        with patch('app.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            response = {"text": "Test response"}
            call_send_api("sender_psid", response)
            mock_post.assert_called_once()
    
    def test_call_send_api_error(self):
        with patch('app.requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.RequestException("Error")
            response = {"text": "Test response"}
            call_send_api("sender_psid", response)
            mock_post.assert_called_once()

    def test_handle_message_text(self):
        response = {"text": "You just sent me: Test message"}
        sender_psid = "sender_psid"
        received_message = {"text": "Test message"}
        handle_message(sender_psid, received_message)
        # Assert that the response is sent to the sender_psid

    def test_handle_message_no_text(self):
        response = {"text": "This chatbot only accepts text messages"}
        sender_psid = "sender_psid"
        received_message = {"attachment": {"type": "image"}}
        handle_message(sender_psid, received_message)
        # Assert that the response is sent to the sender_psid

if __name__ == '__main__':
    unittest.main()