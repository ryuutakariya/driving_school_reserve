import datetime
import re
import time

from linebot import LineBotApi
from linebot.models import TextSendMessage
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

YOUR_CHANNEL_SECRET = 'd6adf18a0c3d204d2a0f55e719d58b63'
YOUR_CHANNEL_ACCESS_TOKEN = 'KvxfbI3Om3fcNl22DsmvIKxI4Vp/JUbPu6R8CIcx8ZWuNIpdPmULsZ9UP9t5WrNVUUcmUOEKhZahteLWapKdKVtGP6Zk4J4CrpeWrL75JKpM4r1vx4hr5DaoieHssU4Ol77SydfUEVd/ylf2wWnHSwdB04t89/1O/w1cDnyilFU='
line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)

execlusion_day_list = ["2020/10/2[3-9]",
                       "2020/10/3.", "2020/11/17", "2020/11/2[0-3]"]


def main():
    # ブラウザのオプションを格納する変数をもらってきます。
    options = Options()

    # Headlessモードを有効にする（コメントアウトするとブラウザが実際に立ち上がります）
    options.set_headless(True)
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')

    try:
        f = open('./log.txt', mode='a')
        # ブラウザを起動する
        driver = webdriver.Chrome(chrome_options=options)

        # ブラウザでアクセスする
        driver.get(f'https://takenotsuka.obic7.obicnet.ne.jp/ZADFavo/Favorite.aspx?p=LglG6YZHJ9uAIqNlw3bWWrfwDaMef%2bt4zWTxaDfXW2YTHL6NPgUsTujRME7%2bWXrt')
        driver.find_element_by_id('lnkToLogin').click()

        switch_iframe('frameMenu', driver)
        driver.find_element_by_id('txtKyoushuuseiNO').send_keys("2203066")
        driver.find_element_by_id('txtPassword').send_keys("0325")
        driver.find_element_by_id('btnAuthentication').click()

        driver.find_element_by_id('btnMenu_YoyakuItiran').click()
        itiran_list = [e for e in driver.find_elements_by_class_name(
            "blocks") if ('2020' in e.text) or ('2021' in e.text)]

        total = 0
        for itiran in itiran_list:
            total += int(itiran.find_element_by_class_name('badge').text)

        if total >= 8:
            return

        driver.find_element_by_class_name('nbtn-img').click()

        driver.find_element_by_id('btnMenu_Kyoushuuyoyaku').click()
        resultlist = []

        cnt = 0
        while True:
            blocks_list = [e for e in driver.find_elements_by_class_name(
                "blocks") if ('2020' in e.text) or ('2021' in e.text)]
            ob_slide_pnl_list = driver.find_elements_by_class_name(
                'slide-down')
            for block, ob_slide_pnl in zip(blocks_list, ob_slide_pnl_list):
                if block.find_element_by_class_name('badge').text == '空':

                    day = block.find_element_by_tag_name('span').text

                    # 予め除外日に設定した日程は除外
                    if any([re.match(execlusion_day, day) for execlusion_day in execlusion_day_list]):
                        continue

                    block.find_element_by_class_name('iconarea').click()
                    time.sleep(0.5)
                    if ('土' in day) or ('日' in day):
                        for period_block in ob_slide_pnl.find_elements_by_class_name("blocks"):
                            resultlist.append(day + ' ' + period_block.text)

                    else:
                        for period_block in ob_slide_pnl.find_elements_by_class_name("blocks"):
                            if period_block.find_element_by_tag_name('span').text in ('01', '11'):
                                resultlist.append(
                                    day + ' ' + period_block.text)
            if cnt == 2:
                break
            cnt += 1
            driver.find_element_by_class_name('next').click()

        if resultlist:
            messages = TextSendMessage(text='\n'.join(resultlist))
            line_bot_api.push_message(
                'Uf0307e36bb400200b8a11dcfbb31d118', messages=messages)
            print(str(datetime.datetime.now()) + " 予約できる時間帯がありました", file=f)
        else:
            print(str(datetime.datetime.now()) + " 予約できる時間帯はありませんでした", file=f)
    except Exception as e:
        print(str(datetime.datetime.now()) + " プログラム実行中にエラーがおきました", file=f)
        print(e, file=f)
    finally:
        driver.quit()
        f.close()


def switch_iframe(id, driver):
    iframe = driver.find_element_by_id(id)
    driver.switch_to_frame(iframe)


if __name__ == "__main__":
    main()
