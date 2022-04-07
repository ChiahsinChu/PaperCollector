from selenium import webdriver
import time
import os


def startdownload(url,
                  record_num,
                  SAVE_TO_DIRECTORY,
                  record_format='excel',
                  reverse=False):
    '''url -> 检索结果网址; \n 
       record_num -> 需要导出的记录条数(检索结果数); \n
       SAVE_TO_DIRECTORY -> 记录导出存储路径(文件夹);\n
       reverse -> 是否设置检索结果降序排列, default=False \n
       ----------------------------------------------------
       tip1:首次打开wos必须登录,在学校统一身份认证处需要手动输入验证码并点击登录; 
       tip2:第一次导出时需要手动修改文件处理方式为"保存文件",并勾选"以后都采用相同动作处理此类文件"
    '''
    fp = webdriver.FirefoxProfile()
    fp.set_preference('browser.download.dir', SAVE_TO_DIRECTORY)
    fp.set_preference("browser.download.folderList", 2)
    fp.set_preference("browser.download.manager.showWhenStarting", False)
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/plain")
    browser = webdriver.Firefox(executable_path=r'geckodriver',
                                firefox_profile=fp)
    browser.get(url)
    time.sleep(4)
    login(browser)
    browser.get(url)  # 登陆后会跳转到首页,这里直接重新打开检索结果页面
    time.sleep(5)

    # 获取需要导出的文献数量
    # record_num = int(browser.find_element_by_css_selector('.brand-blue').text)
    # 按时间降序排列
    if reverse:
        browser.find_element_by_css_selector(
            '.top-toolbar wos-select:nth-child(1) button:nth-child(1) span:nth-child(2)'
        ).click()
        browser.find_element_by_css_selector(
            "div.wrap-mode:nth-child(2) span:nth-child(1)").click()
        time.sleep(3)

    # 叉掉弹窗。网站弹窗时常会改，报错的话可以自己重新获取一下节点哦。
    browser.find_element_by_css_selector(
        '#onetrust-accept-btn-handler').click()
    time.sleep(1)
    browser.find_element_by_css_selector('#pendo-close-guide-ecbac349').click()

    # 开始导出
    start = 1  # 起始记录
    i = 0  # 导出记录的数字框id随导出次数递增
    flag = 1  # mac文件夹默认有一个'.DS_Store'文件
    while start < record_num:
        browser.find_element_by_css_selector(
            'button.cdx-but-md:nth-child(2) span:nth-child(1)').click()  # 导出
        if record_format == 'excel':
            browser.find_element_by_css_selector(
                '#exportToExcelButton').click()  # 选择导出格式为excel
            browser.find_element_by_css_selector(
                '#radio3 label:nth-child(1) span:nth-child(1)').click(
                )  # 选择自定义记录条数
            send_key(browser, '#mat-input-%d' % i, start)  #mat-input-2
            send_key(browser, '#mat-input-%d' % (i + 1), start + 999)
            browser.find_element_by_css_selector(
                '.margin-top-5 button:nth-child(1)').click()  # 更改导出字段
            browser.find_element_by_css_selector(
                'div.wrap-mode:nth-child(3) span:nth-child(1)').click(
                )  # 选择所需字段(excel:3完整/4自定义; txt:3完整/4完整+引文)
            browser.find_element_by_css_selector(
                'div.flex-align:nth-child(3) button:nth-child(1)').click(
                )  # 点击导出
            while len(os.listdir(SAVE_TO_DIRECTORY)) == flag:
                time.sleep(1)  # 等待下载完毕
            # 导出文件按照包含的记录编号重命名
            rename_file(SAVE_TO_DIRECTORY,
                        'record-' + str(start) + '-' + str(start + 999),
                        record_format=record_format)
            start = start + 1000
        else:
            browser.find_element_by_css_selector(
                '#exportToFieldTaggedButton').click()  # 选择导出格式为txt
            browser.find_element_by_css_selector(
                '#radio3 label:nth-child(1) span:nth-child(1) span:nth-child(1)'
            ).click()  # 选择自定义记录条数
            send_key(browser, '#mat-input-%d' % i, start)  #mat-input-2
            send_key(browser, '#mat-input-%d' % (i + 1), start + 499)
            browser.find_element_by_css_selector(
                '.margin-top-5 button:nth-child(1)').click()  # 更改导出字段
            browser.find_element_by_css_selector(
                'div.wrap-mode:nth-child(4) span:nth-child(1)').click(
                )  # 选择所需字段(excel:3完整/4自定义; txt:3完整/4完整+引文)
            browser.find_element_by_css_selector(
                'div.flex-align:nth-child(3) button:nth-child(1)').click(
                )  # 点击导出
            while len(os.listdir(SAVE_TO_DIRECTORY)) == flag:
                time.sleep(1)  # 等待下载完毕
            # 导出文件按照包含的记录编号重命名
            rename_file(SAVE_TO_DIRECTORY,
                        'record-' + str(start) + '-' + str(start + 499),
                        record_format=record_format)
            start = start + 500
        i = i + 2
        flag = flag + 1

    time.sleep(10)
    browser.quit()


def login(browser):
    '''登录wos'''
    # 通过CHINA CERNET Federation登录
    browser.find_element_by_css_selector('.mat-select-arrow').click()
    browser.find_element_by_css_selector(
        '#mat-option-9 span:nth-child(1)').click()
    browser.find_element_by_css_selector(
        'button.wui-btn--login:nth-child(4) span:nth-child(1) span:nth-child(1)'
    ).click()
    time.sleep(3)
    login = browser.find_element_by_css_selector('#show')
    login.send_keys('xxxx大学')  # 改成你的学校名
    time.sleep(0.5)
    browser.find_element_by_css_selector(
        '.dropdown-item strong:nth-child(1)').click()
    browser.find_element_by_css_selector('#idpSkipButton').click()
    time.sleep(1)
    #! 跳转到学校的统一身份验证(想自动输入账号密码就把下面两行注释解除,按照自己学校的网址修改一下css选择器路径)
    # browser.find_element_by_css_selector('input#un').send_keys('你的学号') # 改成你的学号/账号
    # browser.find_element_by_css_selector('input#pd').send_keys('你的密码') # 改成你的密码
    time.sleep(20)  #! 手动输入账号、密码、验证码，点登录


def send_key(browser, path, value):
    '''browser -> browser;\n
       path -> css选择器;\n
       value -> 填入值
    '''
    markto = browser.find_element_by_css_selector(path)
    markto.clear()
    markto.send_keys(value)


def rename_file(SAVE_TO_DIRECTORY, name, record_format='excel'):
    '''导出文件重命名 \n
       SAVE_TO_DIRECTORY -> 导出记录存储位置(文件夹)；\n 
       name -> 重命名为
    '''
    # files = list(filter(lambda x:'savedrecs' in x and len(x.split('.'))==2,os.listdir(SAVE_TO_DIRECTORY)))
    while True:
        files = list(
            filter(lambda x: 'savedrecs' in x and len(x.split('.')) == 2,
                   os.listdir(SAVE_TO_DIRECTORY)))
        if len(files) > 0:
            break

    files = [os.path.join(SAVE_TO_DIRECTORY, f)
             for f in files]  # add path to each file
    files.sort(key=lambda x: os.path.getctime(x))
    newest_file = files[-1]
    # newest_file=os.path.join(SAVE_TO_DIRECTORY,'savedrecs.txt')
    if record_format == 'excel':
        os.rename(newest_file, os.path.join(SAVE_TO_DIRECTORY, name + ".xls"))
    else:
        os.rename(newest_file, os.path.join(SAVE_TO_DIRECTORY, name + ".txt"))


if __name__ == '__main__':

    # WOS“检索结果”页面的网址
    url = 'https://www.webofscience.com/wos/woscc/summary/64c4e5ff-832d-476d-8112-51e908a600b1-1d5405d5/relevance/1'
    # 导出到本地的存储路径(自行修改)
    download_path = '/Users/username/folder'

    startdownload(url,
                  80195,
                  download_path,
                  record_format='excel',
                  reverse=False)  # 主要函数
    print('Done')
