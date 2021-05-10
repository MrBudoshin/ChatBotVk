from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch, Mock, ANY

from pony.orm import db_session, rollback
from vk_api.bot_longpoll import VkBotMessageEvent, VkBotEvent

import settings
from chatbot import ChatBotVk
from create_ticket import generate_ticket


def isolate_db(test_funk):
    def wrapper(*args, **kwargs):
        with db_session():
            test_funk(*args, **kwargs)
            rollback()

    return wrapper


class Test1(TestCase):
    RAW_EVENT = {
        'type': 'message_new',
        'object': {'date': 1604345690, 'from_id': 34236608, 'id': 99, 'out': 0, 'peer_id': 34236608,
                   'text': 'привет', 'conversation_message_id': 95, 'fwd_messages': [], 'important': False,
                   'random_id': 0, 'attachments': [], 'is_hidden': False},
        'group_id': 198361966, 'event_id': '51f8f75fb242bb47f4614e52928deb4fe8c67279'}

    def test_run(self):
        count = 5
        obj = {'a': 1}
        events = [obj] * count  # [obj, obj, ...]
        long_poller_mock = Mock(return_value=events)
        long_poller_listen_mock = Mock()
        long_poller_listen_mock.listen = long_poller_mock

        with patch('chatbot.vk_api.VkApi'):
            with patch('chatbot.VkBotLongPoll', return_value=long_poller_listen_mock):
                bot = ChatBotVk("", "")
                bot.on_event = Mock()
                bot.send_image = Mock()
                bot.run()

                bot.on_event.assert_called()
                bot.on_event.assert_any_call(obj)
                assert bot.on_event.call_count == count

    INPUTS = [
        "привет",
        "/help",
        "/ticket",
        "Москва",
        "Симферополь",
        "25-03-2033",
        "1",
        "5",
        "коммент",
        "Да",
        "8/925/926/99/94",
        "8-925-926-99-94",
    ]
    EXPECTED_OUTPUTS = [
        settings.DEFAULT_ANSWER,
        settings.INTENTS[1]["answer"],
        settings.SCENARIO["registration"]["steps"]["step1"]["text"],
        settings.SCENARIO["registration"]["steps"]["step2"]["text"].format(handle_town_from="Москва"),
        settings.SCENARIO["registration"]["steps"]["step3"]["text"],
        settings.SCENARIO["registration"]["steps"]["step4"]["text"].format(data=('1 Дата вылета 25-03-2021. Номер '
                                                                                 'рейса 118',
                                                                                 '2 Дата вылета 25-03-2021. Номер '
                                                                                 'рейса 669',
                                                                                 '3 Дата вылета 26-03-2021. Номер '
                                                                                 'рейса 118',
                                                                                 '4 Дата вылета 27-03-2021. Номер '
                                                                                 'рейса 118',
                                                                                 '5 Дата вылета 27-03-2021. Номер '
                                                                                 'рейса 669')),
        settings.SCENARIO["registration"]["steps"]["step5"]["text"],
        settings.SCENARIO["registration"]["steps"]["step6"]["text"],
        settings.SCENARIO["registration"]["steps"]["step7"]["text"].format(handle_town_from="Москва",
                                                                           handle_town_to="Симферополь",
                                                                           reis='\n1 Дата вылета 25-03-2021. Номер '
                                                                                'рейса 118',
                                                                           place="5"
                                                                           ),
        settings.SCENARIO["registration"]["steps"]["step8"]["text"],
        settings.SCENARIO["registration"]["steps"]["step8"]["failure_text"],
        settings.SCENARIO["registration"]["steps"]["step9"]["text"].format(phone="8-925-926-99-94")
    ]

    @isolate_db
    def test_run_ok(self):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send = send_mock

        events = []
        for input_text in self.INPUTS:
            event = deepcopy(self.RAW_EVENT)
            event['object']['text'] = input_text
            events.append(VkBotMessageEvent(event))

        long_poller_mock = Mock()
        long_poller_mock.listen = Mock(return_value=events)

        with patch('chatbot.VkBotLongPoll', return_value=long_poller_mock):
            bot = ChatBotVk('', '')
            bot.api = api_mock
            bot.send_image = Mock()
            bot.run()

        real_outputs = []
        for call in send_mock.call_args_list:
            args, kwargs = call
            real_outputs.append(kwargs['message'])
        assert real_outputs == self.EXPECTED_OUTPUTS

    def test_image_generation(self):
        ticket_file = generate_ticket(from_town='qwee', to_town='qwer', reis='555', data='21-22-2222', place='2')
        with open('tickets_example.png', 'rb') as expected_file:
            expected_bites = expected_file.read()

        assert ticket_file.read() == expected_bites
