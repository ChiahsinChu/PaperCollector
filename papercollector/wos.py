import time, glob, os, xlrd, sys
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
#from selenium.webdriver.support.ui import WebDriverWait

format_dict = {
    'endnote_desktop': ['//*[@id="exportToEnwDesktopButton"]', 1000],
    'excel': ['//*[@id="exportToExcelButton"]', 1000],
    'txt': ['//*[@id="exportToFieldTaggedButton"]', 1000],
    'ris': ['//*[@id="exportToRisButton"]', 1000]
}


class AutoTask:

    def __init__(self, save_path, browser, executable_path) -> None:
        self.save_path = os.path.abspath(save_path)
        browser = browser.lower()
        getattr(self, '%s_init' % browser)(executable_path)
        self.check_save_path()
        # 300s无响应就关闭窗口
        #self.wait = WebDriverWait(self.browser, 300)

    def chrome_init(self, executable_path):
        options = webdriver.ChromeOptions()
        # no popups
        # set download path
        prefs = {
            'profile.default_content_settings.popups': 0,
            'download.default_directory': self.save_path
        }
        options.add_experimental_option('prefs', prefs)
        # run in background
        #options.add_argument('headless')
        try:
            self.browser = webdriver.Chrome(chrome_options=options)
        except:
            self.browser = webdriver.Chrome(executable_path=executable_path,
                                            chrome_options=options)

    def firefox_init(self, executable_path):
        fp = webdriver.FirefoxProfile()
        # set download path
        fp.set_preference('browser.download.dir', self.save_path)
        fp.set_preference("browser.download.folderList", 2)
        fp.set_preference("browser.download.manager.showWhenStarting", False)
        fp.set_preference("browser.helperApps.neverAsk.saveToDisk",
                          "text/plain")
        self.browser = webdriver.Firefox(executable_path=executable_path,
                                         firefox_profile=fp)

    def check_save_path(self):
        if os.path.isdir(self.save_path) == False:
            os.makedirs(self.save_path)
        else:
            if os.listdir(self.save_path):
                warning = input(
                    "Given save path is not empty. Do you want to continue?\n[Input 'y' or 'Y' to confirm. && Input other to cancel.]"
                )
                if warning.lower() == 'y':
                    pass
                else:
                    sys.exit()
        self.flag = len(os.listdir(self.save_path))


class WOS(AutoTask):

    def __init__(self, **params) -> None:

        # required parameters
        self.url = params['url']
        self.username = params['username']
        self.password = params['password']
        # optional parameters
        self.reverse = params.get('time_reverse', False)
        self.format = params.get('format', 'ris').lower()

        super().__init__(params['wos_path'], params.get('browser', 'chrome'),
                         params.get('executable_path', None))

    def download_refs(self):
        self._login()
        self.browser.get(self.url)
        self._close_popup()
        self._download_setup()

        n_refs = int(
            self.browser.find_element(By.CSS_SELECTOR,
                                      '.brand-blue').text.replace(',', ''))
        ii = 0
        flag = self.flag + 1
        for start in range(1, n_refs, format_dict[self.format][1]):
            # download
            self._single_download(start, ii)
            ii = ii + 2
            # wait to finish
            while len(os.listdir(self.save_path)) == flag:
                time.sleep(1)
            flag = flag + 1
            # rename
            fname = 'refs-%06d-%06d' % (start, start +
                                        format_dict[self.format][1] - 1)
            self._rename_file(fname)

        time.sleep(2)
        self.browser.quit()

    def _login(self):
        self.browser.get('http://www.webofknowledge.com/?DestApp=WOS')
        self.browser.find_element(By.CSS_SELECTOR, '.mat-select-arrow').click()
        # if you want to change the institue, change here!
        self.browser.find_element(By.CSS_SELECTOR,
                                  '#mat-option-9 span:nth-child(1)').click()
        self.browser.find_element(
            By.CSS_SELECTOR,
            'button.wui-btn--login:nth-child(4) span:nth-child(1) span:nth-child(1)'
        ).click()
        login = self.browser.find_element(By.CSS_SELECTOR, '#show')
        login.send_keys('Xiamen University')
        time.sleep(0.5)
        sel_unvi = self.browser.find_element(
            By.CSS_SELECTOR, '.dropdown-item strong:nth-child(1)')
        self.browser.execute_script("arguments[0].click();", sel_unvi)
        self.browser.find_element(By.CSS_SELECTOR, '#idpSkipButton').click()
        time.sleep(2)
        usr_name = self.browser.find_element(By.XPATH, '//*[@id="username"]')
        usr_name.send_keys(self.username)
        usr_pw = self.browser.find_element(By.XPATH, '//*[@id="password"]')
        usr_pw.send_keys(self.password)
        self.browser.find_element(
            By.XPATH, '//*[@id="casLoginForm"]/p[4]/button').click()
        time.sleep(1)
        self.browser.find_element(
            By.XPATH, '/html/body/form/div/div[2]/p[2]/input[2]').click()
        time.sleep(1)

    def _close_popup(self):
        for ii in range(3):
            try:
                time.sleep(5)
                self.browser.find_element(
                    By.CSS_SELECTOR, '#onetrust-accept-btn-handler').click()
                time.sleep(2)
                self.browser.find_element(
                    By.CSS_SELECTOR, '#pendo-close-guide-ecbac349').click()
            except:
                continue
            else:
                break
        time.sleep(0.5)

    def _download_setup(self):
        if self.reverse:
            self._set_time_reverse()

    def _set_time_reverse(self):
        self.browser.find_element(
            By.CSS_SELECTOR,
            '.top-toolbar wos-select:nth-child(1) button:nth-child(1) span:nth-child(2)'
        ).click()
        self.browser.find_element(
            By.CSS_SELECTOR,
            "div.wrap-mode:nth-child(2) span:nth-child(1)").click()
        time.sleep(3)

    def _single_download(self, start, ii):
        # Click "Export"
        self.browser.find_element(
            By.XPATH,
            '//*[@id="snRecListTop"]/app-export-menu/div/button/span[1]'
        ).click()
        # Choose format
        sel_fmt = self.browser.find_element(By.XPATH,
                                            format_dict[self.format][0])
        self.browser.execute_script("arguments[0].click();", sel_fmt)
        time.sleep(1)
        # Choose "Record from -- to --"
        self.browser.find_element(By.XPATH,
                                  '//*[@id="radio3"]/label/span[1]').click()
        # input start/end id
        self._send_id('//*[@id="mat-input-%d"]' % ii, start)
        self._send_id('//*[@id="mat-input-%d"]' % (ii + 1),
                      start + format_dict[self.format][1] - 1)
        """
        # 更改导出字段
        self.browser.find_element(By.CSS_SELECTOR,
                                  '.margin-top-5 button:nth-child(1)').click()
        # 选择所需字段(excel:3完整/4自定义; txt:3完整/4完整+引文)
        self.browser.find_element(
            By.CSS_SELECTOR,
            'div.wrap-mode:nth-child(3) span:nth-child(1)').click()
        """
        # Click "Export"
        self.browser.find_element(
            By.XPATH,
            '/html/body/app-wos/div/div/main/div/div[2]/app-input-route[1]/app-export-overlay/div/div[3]/div[2]/app-export-out-details/div/div[2]/form/div/div[2]/button[1]/span[1]/span'
        ).click()

    def _send_id(self, xpath, value):
        markto = self.browser.find_element(By.XPATH, xpath)
        markto.clear()
        markto.send_keys(value)

    def _rename_file(self, fname):
        while True:
            files = list(
                filter(lambda x: 'savedrecs' in x and len(x.split('.')) == 2,
                       os.listdir(self.save_path)))
            if len(files) > 0:
                break
        # add path to each file
        files = [os.path.join(self.save_path, f) for f in files]
        files.sort(key=lambda x: os.path.getctime(x))
        _file = files[-1]
        _fname, suffix = os.path.splitext(_file)
        self.suffix = suffix
        os.rename(_file, os.path.join(self.save_path, fname + suffix))

    @property
    def all_refs(self):
        all_refs = glob.glob(
            os.path.join(self.save_path, "refs*" + self.suffix))
        all_refs.sort()
        return all_refs

    @property
    def dois(self, save_dois=False):
        if self.format in ['excel', 'txt', 'ris']:
            dois = getattr(self, 'dois_from_%s' % self.format)()
        else:
            raise AttributeError('Unsupported format!')

        if save_dois:
            np.savetxt(os.path.join(self.save_path, "DOIs.txt"),
                       dois,
                       fmt="%s")
        return dois

    def dois_from_excel(self):
        dois = []
        for f in self.all_refs():
            data = xlrd.open_workbook(f)
            dois.extend(data.sheets()[0].col_values(28)[1:])
        return dois

    def dois_from_txt(self):
        pass

    def dois_from_ris(self):
        pass


class SciHub(AutoTask):

    def __init__(self, dois, **params) -> None:
        """
        Params
        ------
        dois: Array or List or Str
            read from external txt file or pass a np.ndarray/list
        """
        self.get_dois(dois)
        super().__init__(
            params.get('scihub_path', os.path.join(params['wos_path'], 'PDF')),
            params.get('browser', 'chrome'),
            params.get('executable_path', None))

    def get_dois(self, dois):
        if isinstance(dois, list) or isinstance(dois, np.ndarray):
            self.dois = dois
        elif isinstance(self.dois, str):
            self.dois = np.loadtxt(self.doi, dtype=str)
        else:
            raise AttributeError('Unsupported doi type!')

    def download_pdfs(self):
        failed = []
        for doi in self.dois:
            if len(doi) > 0:
                try:
                    self.broswer.get("http://sci-hub.mksa.top")
                    input = self.broswer.find_element(
                        By.XPATH, '//*[@id="input"]/form/input[2]')
                    input.send_keys(doi)
                    self.broswer.find_element(By.XPATH,
                                              '//*[@id="open"]/p').click()
                    time.sleep(5)
                    self.broswer.find_element(
                        By.XPATH, '//*[@id="buttons"]/ul/li[2]/a').click()
                    time.sleep(2)
                except:
                    failed.append(doi)
        np.savetxt(os.path.join(self.save_path, "failed_download.txt"),
                   failed,
                   fmt="%s")
