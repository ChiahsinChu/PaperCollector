import time, glob, os, xlrd, sys, logging
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

format_dict = {
    'endnote_desktop': ['//*[@id="exportToEnwDesktopButton"]', 1000],
    'excel': ['//*[@id="exportToExcelButton"]', 1000],
    'txt': ['//*[@id="exportToFieldTaggedButton"]', 1000],
    'ris': ['//*[@id="exportToRisButton"]', 1000]
}
refs_prefix = 'savedrecs'

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler("ppclt.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class AutoTask:

    def __init__(self, save_path, browser, executable_path) -> None:
        self.save_path = os.path.abspath(save_path)
        browser = browser.lower()
        getattr(self, '%s_init' % browser)(executable_path)
        self.check_save_path()
        self.wait = WebDriverWait(self.browser, 60)

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
        self.browser.implicitly_wait(10)

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

    def wait_for_click(self, by, value):
        button = self.wait.until(EC.element_to_be_clickable((by, value)))
        self.browser.execute_script("arguments[0].click();", button)

    def wait_for_sendkeys(self, by, value, keys):
        input = self.wait.until(EC.presence_of_element_located((by, value)))
        input.send_keys(keys)


class WOS(AutoTask):

    def __init__(self, **params) -> None:
        logger.info("Init WOS")
        # required parameters
        self.url = params['url']
        self.username = params['username']
        self.password = params['password']
        self.institute = params['institute']
        # optional parameters
        self.format = params.get('format', 'ris').lower()
        self.sortby = params.get('sortby', None)

        super().__init__(params['wos_path'], params.get('browser', 'chrome'),
                         params.get('executable_path', None))

    def download(self):
        self._login()
        self.browser.get(self.url)
        self._close_popup()
        if self.sortby is not None:
            self._sort()

        logger.info("Start downloading from WOS")
        n_refs = int(
            self.browser.find_element(By.CSS_SELECTOR,
                                      '.brand-blue').text.replace(',', ''))
        ii = 0
        #flag = self.flag + 1
        for start in range(1, n_refs, format_dict[self.format][1]):
            # download
            self._single_download(start, ii)
            ii = ii + 2
            """
            # wait to finish
            while len(os.listdir(self.save_path)) == flag:
                time.sleep(1)
            """
            #flag = flag + 1
        # rename
        self._rename()

        time.sleep(10)
        self.browser.quit()

    def _login(self):
        self.browser.get('http://www.webofknowledge.com/?DestApp=WOS')
        self.browser.find_element(By.CSS_SELECTOR, '.mat-select-arrow').click()
        # * if you want to change the institue, change here!
        self.browser.find_element(By.CSS_SELECTOR,
                                  '#mat-option-9 span:nth-child(1)').click()
        self.browser.find_element(
            By.CSS_SELECTOR,
            'button.wui-btn--login:nth-child(4) span:nth-child(1) span:nth-child(1)'
        ).click()
        login = self.browser.find_element(By.CSS_SELECTOR, '#show')
        login.send_keys(self.institute)
        time.sleep(0.5)
        sel_unvi = self.browser.find_element(
            By.CSS_SELECTOR, '.dropdown-item strong:nth-child(1)')
        self.browser.execute_script("arguments[0].click();", sel_unvi)
        self.browser.find_element(By.CSS_SELECTOR, '#idpSkipButton').click()
        time.sleep(5)
        # * If you want to have a new login page of your institue, change here
        usr_name = self.browser.find_element(By.ID, 'username')
        #usr_name = self.browser.find_element(By.XPATH, '//*[@id="username"]')
        usr_name.send_keys(self.username)
        usr_pw = self.browser.find_element(By.ID, 'password')
        #usr_pw = self.browser.find_element(By.XPATH, '//*[@id="password"]')
        usr_pw.send_keys(self.password)
        self.browser.find_element(
            By.XPATH, '//*[@id="casLoginForm"]/p[4]/button').click()
        time.sleep(2)
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

    def _sort(self):
        sort_dict = {
            'Date: newest first':
            '//*[@id="date-descending"]',
            'Date: oldest first':
            '//*[@id="date-ascending"]',
            'Citations: highest first':
            '//*[@id="times-cited-descending"]',
            'Citations: lowest first':
            '//*[@id="times-cited-ascending"]',
            'Usage (all time): most first':
            '//*[@id="usage-count-descending"]',
            'Usage (last 180 days): most first':
            '//*[@id="usage-count-180-descending"]'
        }
        # Click "Sort by"
        self.browser.find_element(
            By.CSS_SELECTOR,
            '.top-toolbar wos-select:nth-child(1) button:nth-child(1) span:nth-child(2)'
        ).click()
        sel_sort = self.browser.find_element(By.XPATH, sort_dict[self.sortby])
        self.browser.execute_script("arguments[0].click();", sel_sort)
        time.sleep(2)

    def _single_download(self, start, ii):
        time.sleep(3)
        # Click "Export"
        export = self.browser.find_element(
            By.XPATH,
            '//*[@id="snRecListTop"]/app-export-menu/div/button/span[1]')
        self.browser.execute_script("arguments[0].click();", export)
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

    """
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
    """

    def _rename(self):
        """
        Rename the latest downloaded files 
        savedrecs.* to refs-*-.*
        """
        files = glob.glob(os.path.join(self.save_path, refs_prefix + '*'))
        n_files = len(files)
        _fname, suffix = os.path.splitext(files[0])
        self.suffix = suffix

        fname = 'refs-%06d-%06d' % (1, format_dict[self.format][1])
        os.rename(refs_prefix + suffix,
                  os.path.join(self.save_path, fname + suffix))
        for ii in range(1, n_files):
            fname = 'refs-%06d-%06d' % (
                ii * format_dict[self.format][1],
                (ii + 1) * format_dict[self.format][1] - 1)
            os.rename("%s(%d)%s" % (refs_prefix, ii, suffix),
                      os.path.join(self.save_path, fname + suffix))


class DOIGenerator:

    def __init__(self, refs_list, save_path) -> None:
        suffix_dict = {
            ".ris": "ris",
            ".xls": "excel",
            ".html": "html",
            ".txt": "txt"
        }

        self.all_refs = refs_list
        self.save_path = save_path
        fname, suffix = os.path.splitext(self.all_refs[0])
        try:
            self.format = suffix_dict[suffix]
        except:
            raise AttributeError('Unsupported format!')

    def export_dois(self):
        dois = getattr(self, 'dois_from_%s' % self.format)()
        #print(dois)
        dois = self.rm_duplicate(dois)
        try:
            np.savetxt(os.path.join(self.save_path, "DOIs.txt"),
                       dois,
                       fmt="%s")
        except:
            raise AttributeError('Missing save path for DOIs.txt')
        return dois

    def dois_from_excel(self):
        dois = []
        for f in self.all_refs:
            data = xlrd.open_workbook(f)
            doi_id = data.sheets()[0].row_values(0).index("DOI")
            dois.extend(data.sheets()[0].col_values(doi_id)[1:])
        return dois

    def dois_from_txt(self):
        dois = []
        for f in self.all_refs():
            data = xlrd.open_workbook(f)
            doi_id = data.sheets()[0].row_values(0).index("DOI")
            dois.extend(data.sheets()[0].col_values(doi_id)[1:])
        return dois

    def dois_from_ris(self):
        pass

    def dois_from_html(self):
        pass

    def rm_duplicate(self, dois):
        dois = list(set(dois))
        dois.sort()
        if len(dois[0]) == 0:
            dois = dois[1:]
        return dois


class SciHub(AutoTask):

    def __init__(self, dois, **params) -> None:
        """
        Params
        ------
        dois: Array or List or Str
            read from external txt file or pass a np.ndarray/list
        """
        self.dois = np.loadtxt(dois, dtype=str)
        self.save_path = params.get('scihub_path',
                                    os.path.join(params['wos_path'], 'PDF'))
        super().__init__(self.save_path, params.get('browser', 'chrome'),
                         params.get('executable_path', None))

    def download_pdfs(self):
        failed = []
        for doi in self.dois:
            try:
                self.browser.get("http://sci-hub.mksa.top/" + doi)
                time.sleep(2)
                save = self.browser.find_element(
                    By.XPATH, '//*[@id="buttons"]/ul/li[2]/a')
                self.browser.execute_script("arguments[0].click();", save)
                """
                try:
                    self.browser.switch_to.alert.accept()
                except:
                    pass
                """
                time.sleep(1)
            except:
                failed.append(doi)
        while len(glob.glob(os.path.join(
                self.save_path, '*.pdf'))) + len(failed) < len(self.dois):
            time.sleep(10)
        np.savetxt(os.path.join(self.save_path, "failed_download.txt"),
                   failed,
                   fmt="%s")
        self.browser.quit()
