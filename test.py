from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from datetime import datetime
from time import sleep
import requests
import unittest


class TechnicalTask(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.login = input('Enter login for Gmail: ') + '@gmail.com'
        cls.password = input('Enter password for Gmail: ')

        options = Options()
        options.add_argument('--incognito')
        options.add_argument('--start-fullscreen')
        cls.driver = webdriver.Chrome(options=options)

        timeout = 60
        cls.wait = WebDriverWait(cls.driver, timeout)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.quit()

    def test_01_load_mail_page(self):
        mail_url = 'https://getnada.com/'
        self.driver.get(mail_url)

        # assertion loading mail page
        element_on_page = '//nav/h3[contains(text(), "Temp Inboxes")]'
        self.wait.until(EC.presence_of_element_located((By.XPATH, element_on_page))).is_displayed()

        # Mailing_address
        new_mail_address_path = '//span[@class="address what_to_copy"]'

        # Get random mail address
        mailing_address = self.wait.until(EC.presence_of_element_located((By.XPATH, new_mail_address_path))).text

        urls_for_random_pic = ['https://aws.random.cat/meow',
                               'https://random.dog/woof.json',
                               'https://randomfox.ca/floof/']

        # Get pictures link to dict for message
        pictures_links = []
        keys_for_links = ['file', 'url', 'link']
        for url in urls_for_random_pic:
            for key in keys_for_links:
                r = requests.get(url).json().get(key)
                if r:
                    pictures_links.append(r)

        # Open new tab for Gmail and login
        gmail_url = "window.open('https://mail.google.com/')"
        self.driver.execute_script(gmail_url)
        self.driver.switch_to_window(self.driver.window_handles[1])

        login_mail_field = '//input[@id="identifierId"]'
        self.wait.until(EC.presence_of_element_located((By.XPATH, login_mail_field))).send_keys(self.login)

        button_next = '//span[contains(text(), "Далее")]/following-sibling::div'
        self.wait.until(EC.presence_of_element_located((By.XPATH, button_next))).click()

        password_field = '//input[@name="password"]'
        self.wait.until(EC.presence_of_element_located((By.XPATH, password_field))).send_keys(self.password)
        sleep(3)
        self.wait.until(EC.presence_of_element_located((By.XPATH, button_next))).click()

        # Send new mail
        new_mail_button = "//div[contains(text(), 'Написать')]"
        self.wait.until(EC.presence_of_element_located((By.XPATH, new_mail_button))).click()

        field_to = '//textarea[@aria-label = "Кому"]'
        self.wait.until(EC.presence_of_element_located((By.XPATH, field_to))).send_keys(mailing_address)

        # Fill message text
        message_text = '//tbody//div[@aria-label="Тело письма"]'
        for text in pictures_links:
            self.wait.until(EC.presence_of_element_located((By.XPATH, message_text))).send_keys(text + '\n')

        send_button = "//tbody//div[contains(text(), 'Отправить')]"
        self.wait.until(EC.presence_of_element_located((By.XPATH, send_button))).click()

        # check send successfully on Gmail
        check_confirm_message = "//span[contains(text(), 'Письмо отправлено.')]"
        self.wait.until(EC.presence_of_element_located((By.XPATH, check_confirm_message)))

        # Close Gmail ant switch to getnada
        self.driver.close()
        self.driver.switch_to_window(self.driver.window_handles[0])

        # wait until message has arrived and go to message
        message_from = '//*[text()[contains(., "{}")]]'.format(self.login)
        self.wait.until(EC.presence_of_element_located((By.XPATH, message_from))).click()

        # switch to iframe with inbox message and get message text for assert
        inbox_frame = '//iframe[@id="idIframe"]'

        message_item = '//*[contains(text(), "{}")]'
        text_from_inbox_message = []

        for elem in pictures_links:
            self.driver.switch_to_frame(self.wait.until(EC.presence_of_element_located((By.XPATH, inbox_frame))))
            link_from_message = self.driver.find_element_by_xpath(message_item.format(elem))
            link_from_message.click()
            text_from_inbox_message.append(link_from_message.text)
            self.driver.switch_to_window(self.driver.window_handles[1])
            name_for_screenshot = 'Screenshots/{}.png'.format(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
            self.driver.get_screenshot_as_file(name_for_screenshot)
            self.driver.close()
            self.driver.switch_to_window(self.driver.window_handles[0])

        assert pictures_links == text_from_inbox_message, 'So sad...'


if __name__ == '__main__':
    unittest.main()
