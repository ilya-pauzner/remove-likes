import glob
import random
import time

import vk_api
from bs4 import BeautifulSoup

from sensitive import login, password
from solve_captcha import solve_captcha


def parse(url):
    stripped = url.split('/')[-1]
    owner_id, item_id = stripped.split('_')
    owner_id = ''.join(filter(lambda c: c in '1234567890-', owner_id))
    like_type = ''
    if 'wall' in stripped:
        like_type = 'post'
    elif 'photo' in stripped:
        like_type = 'photo'
    elif 'video' in stripped:
        like_type = 'video'
    elif 'note' in stripped:
        like_type = 'note'
    return like_type, owner_id, item_id


def get_parsed(name):
    with open(name) as f:
        soup = BeautifulSoup(f, features="html.parser")
    answer = []
    for link in soup.find_all('a'):
        content = link.get('href')
        if 'vk' in content:
            answer.append(parse(content))
    return answer


def dislike(vk, triplet):
    print(triplet, end=' ')
    like_type, owner_id, item_id = triplet
    try:
        vk.likes.delete(type=like_type, owner_id=owner_id, item_id=item_id)
    except vk_api.ApiError as err:
        if err.code == 15:
            print('Already disliked!')
    else:
        print('Disliked successfully!')


def captcha_handler(captcha):
    """ При возникновении капчи вызывается эта функция и ей передается объект
        капчи. Через метод get_url можно получить ссылку на изображение.
        Через метод try_again можно попытаться отправить запрос с кодом капчи
    """
    print('CAPTCHA')
    key, task_id = solve_captcha(captcha.get_url())
    # Пробуем снова отправить запрос с капчей
    return captcha.try_again(key)


def main():
    vk_session = vk_api.VkApi(login, password, captcha_handler=captcha_handler)
    vk_session.auth()

    vk = vk_session.get_api()

    for filename in glob.glob('likes/**/*.html', recursive=True):
        for triplet in get_parsed(filename):
            dislike(vk, triplet)
            time.sleep(random.uniform(0.5, 1.5))


if __name__ == '__main__':
    main()
