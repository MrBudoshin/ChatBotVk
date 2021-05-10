import json
import re

from create_ticket import generate_ticket

re_data = re.compile(r"\d\d-\d\d-\d{4}")
re_town_from = re.compile(r"\b[\w\-\s]{3,40}\b")
re_town_to = re.compile(r"\b[\w\-\s]{3,40}\b")
re_phone = re.compile(r"\b(?:\+7|8)(?:-\d{2,3}){4}\b")
re_reis = re.compile(r"\b\d{1,3}\b")
re_place = re.compile(r"\b\d{1,5}\b")
dat = []

with open('fly_managers.json', 'r') as read_file:
    loaded_json_file = json.load(read_file)


def handle_data(text, context):
    data = re.findall(re_data, text)
    full_data = []
    town_reis = []
    n = 0
    if data:
        town_reis.clear()
        full_data.clear()
        dat.append(data)
        for town in loaded_json_file[context["handle_town_from"]][context["handle_town_to"]]:
            town_reis.append(town)
        for reise in town_reis:
            if int(data[0][:2]) == int(reise[0][:2]):
                if data[0][4] == reise[0][4]:
                    reis_index = town_reis.index(reise)
                    for d, r in town_reis[reis_index:reis_index + 5]:
                        n += 1
                        full_data.append(f"{n} Дата вылета {d}. Номер рейса {r}")
        context["data"] = full_data
        return True
    else:
        return False


def handle_town_from(text, context):
    towns = re.findall(re_town_from, text)
    if towns:
        for town in loaded_json_file:
            if towns[0] == town:
                context["handle_town_from"] = text
                return True
    else:
        return False


def handle_town_to(text, context):
    towns = re.findall(re_town_from, text)
    if towns:
        for town in loaded_json_file[context["handle_town_from"]]:
            if towns[0] == town:
                context["handle_town_to"] = text
                return True
    else:
        return False


def handle_phone(text, context):
    phone = re.findall(re_phone, text)
    if phone:
        context["phone"] = text
        return True
    else:
        return False


def handle_reis(text, context):
    reis = re.findall(re_reis, text)
    if reis:
        context["reis"] = f"\n{context['data'][int(text)-1]}"
        dat.clear()
        return True
    else:
        return False


def handle_place(text, context):
    place = re.findall(re_place, text)
    if len(place) > 0:
        context["place"] = text
        return True
    else:
        return False


def handle_comment(text, context):
    if text:
        context["comment"] = text
        return True
    else:
        return False


def handle_answer(text, context):
    if text:
        if text.upper() == "ДА":
            context["answer"] = text
            return True
    else:
        return False


def generate_ticket_handler(text, context):
    return generate_ticket(from_town=context["handle_town_from"],
                           to_town=context["handle_town_to"],
                           reis=context['reis'][-3:],
                           data=context['reis'][14:25],
                           place=context['place'])
