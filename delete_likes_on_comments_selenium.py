import random
import time

import cv2
from python_anticaptcha import AnticaptchaClient, ImageToTextTask
from selenium import webdriver
from skimage import io

from sensitive import login, password, anticaptcha_key, profile_path


def solve_captcha_if_needed(driver):
    try:
        captcha = driver.find_element_by_class_name('captcha_img')
    except:
        # no captcha, fine
        return 0
    else:
        url = captcha.get_attribute('src')
        image = io.imread(url)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        cv2.imwrite('captcha.jpg', image)

        captcha_fp = open('captcha.jpg', 'rb')
        client = AnticaptchaClient(anticaptcha_key)
        task = ImageToTextTask(captcha_fp)
        job = client.createTask(task)
        job.join()
        key = job.get_captcha_text()

        driver.find_element_by_name('captcha_key').send_keys(key)
        driver.find_element_by_css_selector('input.button').click()

        attempts = solve_captcha_if_needed(driver)
        if attempts > 0:
            print('COMPLAINT', job.task_id, key)
        else:
            print('SUCCESS', job.task_id, key)
        return attempts + 1


def main():
    fp = webdriver.FirefoxProfile(profile_path)
    driver = webdriver.Firefox(fp)
    driver.get("https://m.vk.com/feed?section=likes&filter=wall_reply")
    driver.find_element_by_name('email').send_keys(login)
    driver.find_element_by_name('pass').send_keys(password)
    driver.find_element_by_css_selector('input.button').click()

    while True:
        for element in driver.find_elements_by_css_selector('a.item_like'):
            element.click()
            if solve_captcha_if_needed(driver) > 0:
                break
            time.sleep(random.randint(1, 2))
        driver.refresh()


if __name__ == '__main__':
    main()
