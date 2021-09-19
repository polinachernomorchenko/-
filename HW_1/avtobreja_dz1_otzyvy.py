import requests
from bs4 import BeautifulSoup
import time
from nltk.tokenize import word_tokenize
from pymystem3 import Mystem
import collections
import copy

m = Mystem()
rec = 'Поздновато в 2019 году писать отзывы на Тонику мама ужас сухой'
known_proxy_ip = '91.149.203.12:3128'
proxy = {'http': known_proxy_ip, 'https': known_proxy_ip}
good, bad, t, s, l, func = [], [], [], [], [], []
url = 'https://irecommend.ru/content/ottenochnyi-balzam-tonika?page=1'
teacher = ['good', 'good', 'good', 'good', 'good', 'bad', 'bad', 'bad', 'bad', 'bad']
sm = 0


def get_parsed_page(url, proxies=proxy):  # выкачиваем страницу
    response = requests.get(url, proxies=proxy)
    parsed_page = response.text
    return parsed_page


def plus(url):  # хождение по страницам
    l = list(url)
    l[-1] = str(int(l[-1])+1)
    url = ''.join(l)
    return url


def titles_stars_parser(url, s, t):  # заголовки и звезды
    for i in range(10):
        page = get_parsed_page(url, proxy)
        soup = BeautifulSoup(page, 'html.parser')

        titles = soup.find_all('div', {'class': "reviewTitle"})
        titles_l = list(titles)[:50]
        t.extend(titles_l)

        stars = soup.find_all('div', {'class': "starsRating"})
        stars_l = list(stars)[:50]
        s.extend(stars_l)

        url = plus(url)

    return t, s


def cr_cl(name1):   # полный словарь для хороших и плохих отзывов
    with open(name1, 'r', encoding='utf-8') as f:
        txt = f.read()

    txt_l = list(txt)
    for i in range(len(txt_l)):
        if txt_l[i] == '\n' or txt_l[i] == '[' or txt_l[i] == ']':
            txt_l[i] = ''

    txt = ''.join(txt_l)
    txt = txt.lower()
    tok = word_tokenize(txt)
    lem = m.lemmatize(' '.join(tok))
    cr = collections.Counter(lem)

    return dict(cr)


def filter(d):  # фильтр на низкочастотные слова
    dd = copy.deepcopy(d)
    for i in dd:
        if dd[i] < 5:
            del d[i]
    return d


def lister(fd1, fd2):  # два списка из отфильтрованного
    lst1 = []
    lst2 = []
    for i in fd1:
        if i not in fd2:
            lst1.append(i)
    for i in fd2:
        if i not in fd1:
            lst2.append(i)
    return lst1, lst2


def text_parser(name, nn, proxy):
    with open(name, 'w', encoding='utf-8') as f:
        for i in nn:
            n = int(i)
            a = t_ln[n].split('>')
            href = a[1][9:-1]
            link = 'https://irecommend.ru' + href
            page = get_parsed_page(link, proxies=proxy)
            soup = BeautifulSoup(page, 'html.parser')
            ps = [p.get_text() for p in soup.find_all("p")]
            f.write(str(ps))
            f.write('\n\n')
            time.sleep(5)


def checker(rec, g_ul, b_ul):   # проверка тональности
    gm = 0
    bm = 0
    l_rec = rec.lower()
    tok = word_tokenize(l_rec)
    lem = m.lemmatize(' '.join(tok))

    for i in lem:
        if i in g_ul:
            gm += 1
        if i in b_ul:
            bm += 1

    if bm > gm:
        print('отзыв отрицательный')
        return 'bad'
    elif gm > bm:
        print('отзыв положительный')
        return 'good'
    else:
        print('отзыв нейтральный/недостаточно данных')
        return 'neut'


# t, s = titles_stars_parser(url, good, bad, s, t)  # возвращает сырые списки тайтлов и состояния звёзд

# for i in range(len(s)):  # определение тональности по звёздам
#     a = str(s[i]).split('><')
#     if a[-5] == 'div class="on"':
#         good.append(str(i))
#     if a[11] == 'div class="off"':
#         bad.append(str(i))
#
# with open('titles2.txt', 'w', encoding = 'utf-8') as f:   # записывает сырые названия
#     for i in t:
#         f.write(str(i) + '\n')
#
# with open('stars2.txt', 'w', encoding = 'utf-8') as f:  # записывает порядковые номера +/- отзывов
#     f.write(' '.join(good[:40]))
#     f.write(' '.join(bad[:40]))

with open('stars2.txt', 'r', encoding='utf-8') as f:  # списки с номерами
    lns = f.readlines()
    gn = lns[0].split()
    bn = lns[1].split()

with open('titles2.txt', 'r', encoding='utf-8') as f:
    t_ln = f.readlines()


# text_parser('g_texts.txt', gn, proxy)
# text_parser('b_texts.txt', bn, proxy)
g_d = cr_cl('g_texts.txt')
b_d = cr_cl('b_texts.txt')
g_fd = filter(g_d)
b_fd = filter(b_d)
g_ul, b_ul = lister(g_fd, b_fd)[0],  lister(g_fd, b_fd)[1]

with open('test_txt.txt', 'r', encoding='utf-8') as f:
    txt = f.read()
    txt = txt.split(']')

for i in txt:
    print(i)
    rate = checker(i, g_ul, b_ul)
    func.append(rate)

for i in range(len(teacher)):
    if teacher[i] == func[i]:
        sm += 1

accuracy = sm/10
print(func)
print(accuracy)

# мулька раз: учитывать биграммы, потому что "яркий" и "слишком яркий" - это маркеры разной тональности, а при
# пословном анализе эта информация теряется
# мулька два - учитывать знаки препинания и регистр: отзыв с капсом и восклицательными знаками скорее всего не нейтральный




