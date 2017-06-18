from selenium import webdriver
from selenium import common
import re
import random


# TODO: export path with geckodriver or chromedriver automatically and put driver in project files
# TODO: automatically download geckodriver or chromedriver
class Proxy():
    def __init__(self, proxies=None):
        "docstring"
        #self.proxies = [] if proxies is None else proxies
        self.proxies = proxies or []

    def download(self, limit=0):
        print('Transparent proxies')
        self._download('Transparent', limit)
        print('Elite       proxies')
        self._download('elite', limit)

    def _download(self, type, limit=0):
        driver = webdriver.PhantomJS('./phantomjs')
        driver.maximize_window()
        driver.get('http://www.gatherproxy.com/proxylist/anonymity/?t=' + type)
        full_list_button = driver.find_element_by_xpath(
            '//input[@type="submit" and @value="Show Full List"]')
        full_list_button.click()
        #print(driver.page_source)
        for match in re.finditer(
                '<a href="#(.*?)" class="inactive" onclick="gp.pageClick',
                driver.page_source):
            pass
        if limit == 0:
            pages_nr = int(match.group(1))
        else:
            pages_nr = limit
        for i in range(1, pages_nr + 1):
            self._get_proxies(driver.page_source)
            try:
                driver.execute_script('gp.pageClick(' + str(i) + ')')
            except common.exceptions.WebDriverException:
                import ipdb
                ipdb.set_trace()
                driver.execute_script('gp.pageClick(' + str(i) + ')')
            print(i)

    def random(self):
        return random.choice(self.proxies)

    def _get_proxies(self, html):
        for match in re.findall(
                "<td><script>document.write\('(.*?)'[\w\W]*?<td><script>document.write\(gp.dep\('(.*?)'",
                html):
            proxy = (match[0], str(int(match[1], 16)))
            self.proxies.append(proxy)


if __name__ == '__main__':
    p = Proxy()
    p.download()
    proxy = p.random()
