from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

TEMPLAT_PATH = 'chatbot/tickets.png'
FONT_PATH = 'ofont.ru_Primus.ttf'

BLACK = (0, 0, 0, 255)
TOWN_FROM_OFSET = (45, 195)
TOWN_TO_OFSET = (45, 260)
DATA_OFSET = (285, 260)
REIS_OFSET = (45, 325)
PLACE_OFSET = (200, 325)


def generate_ticket(from_town, to_town, reis, data, place):
    ticket = Image.open('tickets.png').convert('RGBA')
    fnt = ImageFont.truetype('ofont.ru_Primus.ttf')

    d = ImageDraw.Draw(ticket)
    d.text(TOWN_FROM_OFSET, from_town, font=fnt, fill=BLACK)
    d.text(TOWN_TO_OFSET, to_town, font=fnt, fill=BLACK)
    d.text(DATA_OFSET, data, font=fnt, fill=BLACK)
    d.text(REIS_OFSET, reis, font=fnt, fill=BLACK)
    d.text(PLACE_OFSET, place, font=fnt, fill=BLACK)

    temp_file = BytesIO()
    ticket.save(temp_file, 'png')
    temp_file.seek(0)

    return temp_file


if __name__ == "__main__":
    generate_ticket(from_town='qwee', to_town='qwer', reis='555', data='21-22-2222', place='2')
