# -*- coding: utf-8 -*-

import random

import requests
import vk_api
import logging

from pony.orm import db_session
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import handlers
from models import UserState, Registration

try:
    import settings
except ImportError:
    exit('Do cp settings.py.default settings.py and set token')
log = logging.getLogger("chatbot")


def configure_logging():
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    stream_handler.setLevel(logging.INFO)
    log.addHandler(stream_handler)

    file_handler = logging.FileHandler("logging_bot")
    file_handler.setFormatter(logging.Formatter("%(asctime)s  %(levelname)s %(message)s", '%H:%M %d-%m-%Y'))
    file_handler.setLevel(logging.DEBUG)
    log.addHandler(file_handler)
    log.setLevel(logging.DEBUG)


class ChatBotVk:
    """
    Chat bot Vk.com

    Use python 3.7
    """

    def __init__(self, group_id, token):
        """
        :param group_id: group id Vk
        :param token: secret token from vk
        """
        self.community_id = group_id
        self.token = token
        self.vk = vk_api.VkApi(token=token)
        self.long_poller = VkBotLongPoll(self.vk, self.community_id)
        self.api = self.vk.get_api()

    def run(self):
        """
        run bot
        :return None
        """
        for event in self.long_poller.listen():
            log.info("Новое событие милорд")
            try:
                self.on_event(event)
            except Exception:
                log.exception("ошибка в обработке событий")

    @db_session
    def on_event(self, event):

        """
        return message if massages text
        :param event: VkBotMessageEvent object
        :return: None
        """
        if event.type != VkBotEventType.MESSAGE_NEW:
            log.info("не умею отвечать на событие %s", event.type)
            return

        user_id = event.object.peer_id
        text = event.object.text
        state = UserState.get(user_id=str(user_id))

        for intent in settings.INTENTS:
            if any(token in text for token in intent["tokens"]):
                if intent["answer"]:
                    self.send_text(intent["answer"], user_id)
                else:
                    if state is not None:
                        state.delete()
                        self.start_scenario(user_id, intent["scenario"], text)
                    else:
                        self.start_scenario(user_id, intent["scenario"], text)
                break
        else:
            if state is not None:
                self.continue_scenario(text, state, user_id)
            else:
                self.send_text(settings.DEFAULT_ANSWER, user_id)

    def send_text(self, text_to_send, user_id):
        self.api.messages.send(
            message=text_to_send,
            random_id=random.randint(0, 2 ** 20),
            peer_id=user_id)

    def send_image(self, image, user_id):
        upload_url = self.api.photos.getMessagesUploadServer()['upload_url']
        upload_data = requests.post(url=upload_url, files={"photo": ('image.png', image, 'image/png')}).json()
        image_data = self.api.photos.saveMessagesPhoto(**upload_data)

        owner_id = image_data[0]['owner_id']
        media_id = image_data[0]['id']
        attachment = f'photo{owner_id}_{media_id}'

        self.api.messages.send(
            attachment=attachment,
            random_id=random.randint(0, 2 ** 20),
            peer_id=user_id
        )

    def send_step(self, step, user_id, text, context):
        if 'text' in step:
            self.send_text(step["text"].format(**context), user_id)
        if 'image' in step:
            handler = getattr(handlers, step["image"])
            image = handler(text, context)
            self.send_image(image, user_id)

    def start_scenario(self, user_id, scenario_name, text):
        scenario = settings.SCENARIO[scenario_name]
        first_step = scenario["first_step"]
        step = scenario["steps"][first_step]
        self.send_step(step, user_id, text, context={})
        UserState(user_id=str(user_id), scenario_name=scenario_name, step_name=first_step, context={})

    def continue_scenario(self, text, state, user_id):
        steps = settings.SCENARIO[state.scenario_name]["steps"]
        step = steps[state.step_name]

        handler = getattr(handlers, step["handler"])
        if handler(text=text, context=state.context):
            """next step"""
            next_step = steps[step["next_step"]]
            self.send_step(next_step, user_id, text, state.context)
            if next_step["next_step"]:
                """switch to next step"""
                state.step_name = step["next_step"]
            else:
                """finish scenario"""
                log.info("Спасибо за регистрацию".format(**state.context))
                Registration(
                    data=state.context['reis'][14:25][-3:],
                    town_from=state.context['handle_town_from'],
                    town_end=state.context['handle_town_to'],
                    phone=state.context['phone'],
                    reis=state.context['reis'][-3:],
                    place=state.context['place'],
                    comment=state.context['comment'],
                    answer=state.context['answer'],
                )
                state.delete()
        else:
            """retry steps"""
            if step["restart"]:
                state.delete()
            text_to_send = step["failure_text"].format(**state.context)
            self.send_text(text_to_send, user_id)


if __name__ == '__main__':
    configure_logging()
    launch_bot = ChatBotVk(group_id=settings.GROUP_ID, token=settings.TOKEN)
    launch_bot.run()
