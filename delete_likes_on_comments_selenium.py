import random
import time

from selenium import webdriver

from sensitive import login, password, profile_path
from solve_captcha import solve_captcha


def solve_captcha_if_needed(driver):
    try:
        captcha = driver.find_element_by_class_name('captcha_img')
    except:
        # no captcha, fine
        return 0
    else:
        url = captcha.get_attribute('src')
        key, task_id = solve_captcha(url)

        driver.find_element_by_name('captcha_key').send_keys(key)
        driver.find_element_by_css_selector('input.button').click()

        attempts = solve_captcha_if_needed(driver)
        if attempts > 0:
            print('COMPLAINT', key, task_id)
        else:
            print('SUCCESS', key, task_id)
        return attempts + 1


def main():
    fp = webdriver.FirefoxProfile(profile_path)
    driver = webdriver.Firefox(fp)
    driver.get("https://m.vk.com/feed?section=likes&filter=wall_reply")
    driver.find_element_by_name('email').send_keys(login)
    driver.find_element_by_name('pass').send_keys(password)
    driver.find_element_by_css_selector('input.button').click()

    elements = driver.find_elements_by_css_selector('a.item_like')
    while len(elements) > 0:
        for element in elements:
            element.click()
            if solve_captcha_if_needed(driver) > 0:
                break
            time.sleep(random.randint(1, 2))
        driver.refresh()
        elements = driver.find_elements_by_css_selector('a.item_like')
    driver.quit()


if __name__ == '__main__':
    main()
