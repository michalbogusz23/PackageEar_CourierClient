import requests
import json
from jwt import encode, decode
from datetime import datetime, timedelta
from os import getenv
from dotenv import load_dotenv

load_dotenv()
LOGIN = 'admin'
PASSWORD = 'admin'
JWT_SECRET = getenv('JWT_SECRET')
API_ADDRESS = 'https://secret-island-24073.herokuapp.com/'
# API_ADDRESS = 'http://localhost:5050/'

def generate_header_with_token():
    payload = {
        'usr': 'courier_client',
        'type': 'courier',
        'exp': datetime.utcnow() + timedelta(seconds=100)
    }
    token = encode(payload, JWT_SECRET, algorithm='HS256')
    token = token.decode()
    headers = {"Authorization": "Bearer " + token}
    return headers

def auth_user():
    login = input("Podaj login: ")
    password = input("Podaj haslo: ")
    if login == LOGIN and password == PASSWORD:
        return True
    print("Niepoprawne dane, spróbuj jeszcze raz!")
    auth_user()

def menu():
    print("Witaj w panelu sterowania paczkami!")
    print("Wybierz swoją akcje, dzielny rozwozicielu: ")
    print("1. Wyświetl wszystkie etykiey")
    print('2. Zarejestruj paczkę')
    print('3. Zmień status paczki')
    print('4. Wyświetl wszystkie paczki(do sprawdzania, nie jest wymagane)')
    print('5. Wyjdź')
    option = input()

    switcher = {
        1: print_all_labels,
        2: register_package,
        3: update_package,
        4: print_all_packages,
        5: exit
    }
    func = switcher.get(int(option), lambda: "Ten numer to kłopoty")
    return func()

def print_all_labels():
    headers = generate_header_with_token()
    r = requests.get(API_ADDRESS + 'label', headers=headers)
    response = json.loads(r.text)
    print("Dostępne etykiety paczek:")
    for id, label in enumerate(response['labels']):
        print(str(id) + ': ' + str(label))
    print("\nNaciśnij enter aby wrócić do menu(polecam skopiować id wybranej etykiety)")
    input()

def register_package():
    label_id = input('Podaj id etykiety, lepiej żeby było poprawne: ')
    package = {
        'label_id': label_id,
        'status': 'zarejestrowana'
    }
    send_notification(label_id, 'zarejestrowana')
    headers = generate_header_with_token()
    requests.post(API_ADDRESS + 'package', headers=headers, json=package)
    print('\nPomyślnie zarejestrowano nową paczkę!\n')

def update_package():
    label_id = input('Podaj id etykiety, lepiej żeby było poprawne: ')
    print('Wybierz status na który chcesz zmienić')
    print('Nacisnij enter aby wrócić')
    print('1. Wydana')
    print('2. W trakcie dostawy')
    print('3. Dostarczona')
    option = input()
    switcher = {
        1: 'wydana',
        2: 'w drodze',
        3: 'dostarczona',
    }
    status = switcher.get(int(option), lambda: menu())
    package = {
        'label_id': label_id,
        'status': status
    }
    send_notification(label_id, status)
    headers = generate_header_with_token()
    requests.put(API_ADDRESS + 'package/' + label_id, headers=headers, json=package)
    print('\nPomyślnie zaktualizowano status paczki!\n')

def print_all_packages():
    headers = generate_header_with_token()
    r = requests.get(API_ADDRESS + 'package', headers=headers)
    response = json.loads(r.text)
    print("Dostępne etykiety paczek:")
    for id, package in enumerate(response['packages']):
        print(str(id) + ': ' + str(package))
    print("\nNaciśnij enter aby wrócić do menu(polecam skopiować id wybranej etykiety)")
    input()

def send_notification(label_id, status):
    headers = generate_header_with_token()
    r = requests.get(API_ADDRESS + 'label', headers=headers)   
    response = json.loads(r.text)
    sender = ''
    for keyval in response['labels']:
        if label_id == keyval['id']:
            sender = keyval['sender']
    print(sender)
    label = {"login": sender, "msg": status, "id": label_id}
    headers = generate_header_with_token()
    requests.post(API_ADDRESS + 'notification', headers=headers, json=label)

# auth_user()
while True:
    menu()

