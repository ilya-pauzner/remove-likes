import cv2
from python_anticaptcha import AnticaptchaClient, ImageToTextTask
from skimage import io

from sensitive import anticaptcha_key


def solve_captcha(url):
    image = io.imread(url)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    cv2.imwrite('captcha.jpg', image)

    captcha_fp = open('captcha.jpg', 'rb')
    client = AnticaptchaClient(anticaptcha_key)
    task = ImageToTextTask(captcha_fp)
    job = client.createTask(task)
    job.join()
    return job.get_captcha_text(), job.task_id
