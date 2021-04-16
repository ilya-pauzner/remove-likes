import glob
import random
import time
from urllib.parse import urlparse, parse_qs

import vk_api
from bs4 import BeautifulSoup

from sensitive import login, password
from solve_captcha import solve_captcha


def parse(url):
    parsed = urlparse(url)
    comment_id = parse_qs(parsed.query)['reply'][0]

    s = parsed.path.strip('/').split('_')[0]
    owner_id = ''.join(filter(lambda c: c in '1234567890-', s))

    return owner_id, comment_id


def get_parsed(name):
    with open(name) as f:
        soup = BeautifulSoup(f, features="html.parser")
    answer = []
    for link in soup.find_all('a'):
        content = link.get('href')
        if 'vk' in content and 'wall' in content and 'z' not in content:
            answer.append(parse(content))
    return answer


def delete(vk, pair):
    print(pair, end=' ')
    owner_id, comment_id = pair
    try:
        vk.wall.deleteComment(owner_id=owner_id, comment_id=comment_id)
    except vk_api.ApiError as err:
        if err.code == 15:
            print('Already disliked!')
        else:
            print(err)
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
    for filename in glob.glob('comments/**/*.html', recursive=True):
        for pair in get_parsed(filename):
            delete(vk, pair)
            time.sleep(random.uniform(0.5, 1.5))


if __name__ == '__main__':
    main()
