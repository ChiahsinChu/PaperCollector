import time, glob, os, xlrd
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


class WOS:

    def __init__(self, **kwargs) -> None:
        """
        TBC
        """
        # required parameters
        self.url = kwargs['url']
        self.username = kwargs['username']
        self.password = kwargs['password']
        self.work_path = kwargs['work_path']

        # optional parameters
        self.reverse = kwargs.get('time_reverse', False)
        self.format = kwargs.get('format', 'ris')
        self.pdf_path = kwargs.get('pdf_path',
                                   os.path.join(self.work_path, 'PDF'))

        # browser and download setup
        """
        # Firefox
        self.fp = webdriver.FirefoxProfile()
        # 指定下载路径
        self.fp.set_preference('browser.download.dir', self.save_path)
        self.fp.set_preference("browser.download.folderList", 2)
        # 是否显示开始
        self.fp.set_preference("browser.download.manager.showWhenStarting", False)
        # 对所给文件类型不再弹出框进行询问
        self.fp.set_preference("browser.helperApps.neverAsk.saveToDisk",
                               "text/plain")
        self.browser = webdriver.Firefox(executable_path=executable_path,
                                         firefox_profile=self.fp)
        """

        # Chrome
        options = webdriver.ChromeOptions()
        # no popups
        # set download dir
        prefs = {
            'profile.default_content_settings.popups': 0,
            'download.default_directory': self.work_path
        }
        options.add_experimental_option('prefs', prefs)
        # run in background
        options.add_argument('headless')
        try:
            self.browser = webdriver.Chrome(chrome_options=options)
        except:
            self.browser = webdriver.Chrome(executable_path=kwargs.get(
                'executable_path', None),
                                            chrome_options=options)

        self.dois = None

        # 300s无响应就关闭窗口
        #self.wait = WebDriverWait(self.browser, 300)
        # 定义窗口最大化
        #self.browser.maximize_window()

    def download_refs(self):
        # open the searching page
        self._login()
        for ii in range(3):
            try:
                self._close_popup()
            except:
                pass
        self.browser.get(self.url)
        time.sleep(5)

        # 获取需要导出的文献数量
        n_refs = int(
            self.browser.find_element(By.CSS_SELECTOR,
                                      '.brand-blue').text.replace(',', ''))
        if self.reverse:
            self._set_time_reverse()
        if os.path.isdir(self.save_path) == False:
            os.makedirs(self.save_path)

        # 开始导出
        start = 1  # 起始记录
        i = 0  # 导出记录的数字框id随导出次数递增
        flag = 1  # mac文件夹默认有一个'.DS_Store'文件
        while start < n_refs:
            # Click "Export"
            self.browser.find_element(
                By.CSS_SELECTOR,
                'button.cdx-but-md:nth-child(2) span:nth-child(1)').click()
            self._download(start, i, flag)
            # 导出文件按照包含的记录编号重命名
            fname = 'refs-%06d-%06d' % (start, start +
                                        format_dict[self.format][1] - 1)
            self._rename_file(fname)
            start = start + format_dict[self.format][1]
            i = i + 2
            flag = flag + 1

        time.sleep(10)
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
        self.browser.find_element(
            By.CSS_SELECTOR, '.dropdown-item strong:nth-child(1)').click()
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

    def _close_popup(self):
        time.sleep(5)
        self.browser.find_element(By.CSS_SELECTOR,
                                  '#onetrust-accept-btn-handler').click()
        time.sleep(2)
        self.browser.find_element(By.CSS_SELECTOR,
                                  '#pendo-close-guide-ecbac349').click()

    def _set_time_reverse(self):
        self.browser.find_element(
            By.CSS_SELECTOR,
            '.top-toolbar wos-select:nth-child(1) button:nth-child(1) span:nth-child(2)'
        ).click()
        self.browser.find_element(
            By.CSS_SELECTOR,
            "div.wrap-mode:nth-child(2) span:nth-child(1)").click()
        time.sleep(3)

    def _download(self, start, i, flag):

        # 选择导出格式
        self.browser.find_element(By.CSS_SELECTOR,
                                  format_dict[self.format][0]).click()
        # 选择自定义记录条数
        self.browser.find_element(
            By.CSS_SELECTOR,
            '#radio3 label:nth-child(1) span:nth-child(1)').click()
        # 输入起止序号
        self._send_id('//*[@id="mat-input-%d"]' % i, start)
        self._send_id('//*[@id="mat-input-%d"]' % (i + 1),
                      start + format_dict[self.format][1] - 1)
        # 更改导出字段
        self.browser.find_element(By.CSS_SELECTOR,
                                  '.margin-top-5 button:nth-child(1)').click()
        # 选择所需字段(excel:3完整/4自定义; txt:3完整/4完整+引文)
        self.browser.find_element(
            By.CSS_SELECTOR,
            'div.wrap-mode:nth-child(3) span:nth-child(1)').click()
        # 点击导出
        self.browser.find_element(
            By.CSS_SELECTOR,
            'div.flex-align:nth-child(3) button:nth-child(1)').click()
        # 等待下载完毕
        while len(os.listdir(self.save_path)) == flag:
            time.sleep(1)

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
        func_dict = {
            'excel': self.dois_from_excel,
            'txt': self.dois_from_txt,
            'ris': self.dois_from_ris
        }
        func = func_dict.get(self.format, None)
        if func is None:
            raise AttributeError('Unsupported format!')
        else:
            dois = func()
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

    def get_pdfs(self, doi_file=None):
        if doi_file is not None:
            self.dois = np.loadtxt(doi_file, dtype=str)
        else:
            if self.dois is None:
                raise AttributeError('DOI info missing.')

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
