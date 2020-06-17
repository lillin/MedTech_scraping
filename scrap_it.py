import csv
import os

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class Client:
    COMPANY_NAME = 'company_name'
    CONTACT = 'contact'
    TITLE = 'title'
    WEBSITE = 'website'

    LINKS_CATALOG = []
    FIELDNAMES = [COMPANY_NAME, CONTACT, TITLE, WEBSITE, ]

    def __init__(self):
        self.driver = \
            os.path.join('C:' + os.sep, 'Users', 'Lina', 'Documents', 'geckodriver-v0.26.0-win64', 'geckodriver.exe')
        self.options = Options()
        self.options.add_argument('-headless')

        self.browser = webdriver.Firefox(executable_path=self.driver, options=self.options)
        self.browser.get('https://medtechinnovator.org/company-list/')

        self.file = open('companies.csv', 'w')
        self.writer = \
            csv.DictWriter(self.file, fieldnames=self.FIELDNAMES)
        self.writer.writeheader()

    def __call__(self, *args, **kwargs):
        return self.return_output()

    def return_output(self):
        self.compose_catalog()
        self.get_from_page()

        self.file.close()

    def compose_catalog(self):
        next_page_elem = self.browser.find_element_by_css_selector('a.next.page-numbers')

        while True:
            try:
                WebDriverWait(self.browser, 60).until(EC.element_to_be_clickable(
                    (By.XPATH, '/html/body/div[1]/div[2]/div[1]/div/section/div/div[1]/div[4]/a[10]')
                ))
                try:
                    next_page_elem.click()
                except StaleElementReferenceException:
                    next_page_elem = self.browser.find_element_by_css_selector('a.next.page-numbers')
                    next_page_elem.click()
                self.get_links()
            except NoSuchElementException:
                self.get_links()
                break

    def get_links(self):
        links_to_companies = self.browser.find_elements_by_class_name('portfolio-overlay-wrapper')
        for elem in links_to_companies:
            link = elem.get_property('href')
            self.LINKS_CATALOG.append(link)

    def get_from_page(self):
        for link in self.LINKS_CATALOG:
            data = dict.fromkeys(self.FIELDNAMES)

            self.browser.get(link)

            try:
                data[self.COMPANY_NAME] = \
                    self.browser.find_element_by_class_name('gdlr-page-title').text
            except NoSuchElementException:
                pass
            try:
                data[self.CONTACT] = \
                    self.browser.find_element_by_css_selector(
                        'div.portfolio-info.portfolio-contact_name'
                    ).text.partition(' ')[2]
            except NoSuchElementException:
                pass
            try:
                data[self.TITLE] = \
                    self.browser.find_element_by_css_selector(
                        'div.portfolio-info.portfolio-contact_title'
                    ).text.partition(' ')[2]
            except NoSuchElementException:
                pass
            try:
                websites = \
                    self.browser.find_elements_by_css_selector('div.portfolio-info.portfolio-website')
                data[self.WEBSITE] = ' '.join([site.text for site in websites])
            except NoSuchElementException:
                pass

            self.writer.writerow(data)


if __name__ == '__main__':
    Client()()
