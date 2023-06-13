import requests
import random
import csv
from openpyxl import Workbook

def get_random_groups(token):  #Объявление функици для выбора рандомных сообществ и выгрузки этих сообществ в массив
    params = {      # задается список параметров, которые будут выгружены о группах в массиве данных
        'access_token': token,  #токен доступа к социальной сети Вконтакте
        'v': '5.131',   #версия API VK
        'group_ids': ','.join(str(i) for i in random.sample(range(100000000, 1000000000), 500)), # Случайные идентификаторы сообществ
        'fields': 'city, description, deactivated, type, age_limits, links, activity, ' # Дополнительные поля для получения информации о сообществе
    }

    try:
        response = requests.get('https://api.vk.com/method/groups.getById', params=params) #Выполнение запроса к социальной сети методом из VK API (Groups.getById)
        data = response.json()  #Выгрузка данных в массив

        if 'response' in data:     #Проверка работоспособности токена(если присутствуют в выборке критерии заданные выше, значит токен работает)
            groups = data['response']
            # if city_title:
            #     groups = [group for group in groups if group.get('city', {}).get('title') == city_title]
            return groups
        else:
            print('Ошибка при выполнении запроса:', data)
    except requests.exceptions.RequestException as e:
        print('Ошибка при выполнении запроса:', e)

    return []

# Укажите свой токен доступа ВКонтакте
access_token = ''
city_title = 'Пермь' #критерий отбора по городу
age_limit = int('1')  #критерий отбора по возрастному ограничению(1-без ограничений, 2-16+, 3-18+
publ = ('Публичная страница')  #Критерий отбора активности
clos = ('Закрытая группа')      #Критерий отбора активности

filename = 'random_groups.csv'  # Имя файла для сохранения данных
filtered_groups = []  #создание массива с отфильтрованным списком групп по критериям
activ = []
tablex = 'data.xlsx'

workbook = Workbook()
sheet = workbook.active
datahead =['№ п/п', 'Название', 'Описание', 'Город', 'Возрастное ограничение', 'Активность']
headers = datahead
sheet.append(datahead)
activity_count = {}

while len(filtered_groups) < 30:    #здесь задается колиество строк, которое будет в полученном файле по итогу
    random_groups = get_random_groups(access_token)  #вызов функции генерирующей 500 случайных сообществ(500 т.к. это функциональное ограничение vk api)

    print(len(filtered_groups), end=' ')    #просто проверка наполняемости массива отфильтрованного списка сообществ, для удобства использования кода

    for group in random_groups:  #получение параметров в списке сообществ
        description = group.get('description')    #описание в сообществе Вконтакте
        city = group.get('city', {}).get('title')       #город
        deactivated = group.get('deactivated')    #статус сообщества (заблокировано, удалено)
        group_type = group.get('type')      #тип сообщества (группа, мероприятие, официальная страница)
        age_limits = group.get('age_limits')    #возрастное ограничение
        activity = group.get('activity')
#city == city_title and
        if deactivated not in ['deleted', 'banned'] and group_type == 'group' and age_limits == age_limit and not description == '' and not activity == publ and not activity == clos:  #условия отбора сообществ(сообщество не должно быть заблокировано или удалено, тип сообщества должен быть именно сообщество, не должно быть возрастного ограничения
            filtered_groups.append(group)   #если условия отбора выполнены для конкретного сообщества, то оно заносится в отфильтрованный список

with open(filename, 'w', newline='', encoding='utf-8-sig') as file:     #здесь происходит открытие файла для записи отфильтрованного массива сообществ. Файл открывается для перезаписи. Т.е. все данные, что находились в файле-стираются, и записываются новые данные.
    writer = csv.writer(file)
    if file.tell() == 0:
        writer.writerow(['№ п/п', 'Название', 'Описание', 'Город', 'Возрастное ограничение', 'Активность'])  # Запись заголовков столбцов в файл


    for i, group in enumerate(filtered_groups, start=1):
        name = group['name']
        city = group.get('city', {}).get('title', 'Не указан')
        description = group.get('description', 'Нет описания')
        age_limits = group.get('age_limits', 'Не указано')
        if age_limits == group.get('age_limits', 'Не указано'):
            age_lim = ('Без возрастного ограничения')
        activity = group.get('activity')
        #if activity not in activ:
        activ.append(activity)
        for word in activ:
            if word in activity_count:
                activity_count[word] += 1
            else:
                activity_count[word] = 1
        row = [i, name, description, city, age_lim, activity]
        sheet.append(row)
        workbook.save(tablex)
        writer.writerow([i, name, description, city, age_lim, activity])  # Запись данных в файл
# print(activ)
print(activity_count)
print(f'Данные сохранены в файл: {filename}')
