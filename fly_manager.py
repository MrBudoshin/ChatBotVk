# -*- coding: utf-8 -*-

import json
import random
import datetime


class Airbus:

    def __init__(self):
        self.data_now = datetime.datetime.now().strftime('%d-%m-%Y')
        self.fly_reis = {}
        self.reis_num = []
        self.citys = ['Москва', 'Симферополь', 'Владивосток', 'Иркутск']

    def random_keys(self):
        for reis in range(4):
            rand_num_reis = random.randint(100, 999)
            self.reis_num.append(rand_num_reis)

    def fly(self):
        for city_from in self.citys:
            self.fly_reis[city_from] = {}
            for city_to in self.citys:
                if city_from == city_to:
                    continue
                current_ways = []
                for num in range(1, 61):
                    date_now = datetime.datetime.today() + datetime.timedelta(days=num)
                    current_ways.append((date_now.strftime('%d-%m-%Y'), self.reis_num[0]))
                    if date_now.day == 15:
                        current_ways.append((date_now.strftime('%d-%m-%Y'), self.reis_num[1]))
                    elif date_now.day % 2:
                        current_ways.append((date_now.strftime('%d-%m-%Y'), self.reis_num[2]))
                self.fly_reis[city_from][city_to] = current_ways

    def file_save(self):
        with open(r'fly_managers.json', 'w') as write_file:
            json.dump(self.fly_reis, write_file)

    def run(self):
        self.random_keys()
        self.fly()
        self.file_save()


if __name__ == '__main__':
    a = Airbus()
    a.run()
