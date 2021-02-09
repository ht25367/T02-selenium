import os
import logging
from selenium.webdriver import Chrome, ChromeOptions
import time
import pandas as pd

# Chromeを起動する関数
def set_driver(driver_path, headless_flg):
	# Chromeドライバーの読み込み
	options = ChromeOptions()

	# ヘッドレスモード（画面非表示モード）の設定
	if headless_flg == True:
		options.add_argument('--headless')

	# 起動オプションの設定
	options.add_argument(
		'--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
	# options.add_argument('log-level=3')
	options.add_argument('--ignore-certificate-errors')
	options.add_argument('--ignore-ssl-errors')
	options.add_argument('--incognito')		  # シークレットモードの設定を付与

	# ChromeのWebDriverオブジェクトを作成する。
	# 説明：課題02のスクリプトやchromedriver は、もう一層下の T02-selenium フォルダ
	os.chdir( os.path.dirname(os.path.abspath(__file__)) )

	return Chrome(executable_path=os.getcwd() + "/" + driver_path, options=options)


# サイトのページを移動する関数
def page_mv(driver, page: int):

	if page == 1 :			# 次のページへ移動
		driver.find_element_by_class_name("iconFont--arrowLeft").click()
		time.sleep(5)
	elif page == -1:		# 前のページへ移動
		driver.find_element_by_class_name("iconFont--arrowRight").click()
		time.sleep(5)
	else:
		return "Error"



# main処理
def main():
	log_fmt = "%(asctime)s-%(name)s-[%(lineno)d] %(levelname)s :%(message)s"

	logging.basicConfig(
		format=log_fmt,
		level=logging.INFO,
		encoding='utf-8',
	 	filename="./T02-test_log.txt"
	)
	logging.info("－－－START－－－")

	log_con = logging.getLogger(__name__)  # ロガー生成
	h1 = logging.StreamHandler() # ﾊﾝﾄﾞﾗｰ生成
	h1.setLevel(logging.DEBUG)   # 出力レベル設定
	# log_fmt = "%(funcName)s-%(lineno)d %(name)s-%(levelname)s : %(message)s"
	# h1.setFormatter( log_fmt )  # フォーマッター設定
	log_con.addHandler(h1)


	search_keyword = "高収入"
	selector = ""

	# driverを起動
	logging.info("driverを起動し、マイナビにアクセス")
	if os.name == 'nt': #Windows
		driver = set_driver("chromedriver.exe", False)
	elif os.name == 'posix': #Mac
		driver = set_driver("chromedriver", False)
	# Webサイト「マイナビ」を開く
	driver.get("https://tenshoku.mynavi.jp/")
	time.sleep(5)


	logging.info("マイナビ、ポップアップを閉じる")
	try:
		# ポップアップを閉じる
		driver.execute_script('document.querySelector(".karte-close").click()')
		time.sleep(5)
		# ポップアップを閉じる
		driver.execute_script('document.querySelector(".karte-close").click()')
	except:
		pass


	search_keyword = input("検索ワードを入力して下さい:")

	logging.info(f"ﾜｰﾄﾞ「{search_keyword}」で検索")
	# 検索窓に入力
	driver.find_element_by_class_name(
		"topSearch__text").send_keys(search_keyword)
	# 検索ボタンクリック
	driver.find_element_by_class_name("topSearch__button").click()


	# name_list ：ドライバー（会社名リスト）
	# office_list :ドライバー（勤務地リスト）
	# exp_name_list :会社名データを格納するリスト
	# exp_office_list:勤務地データを格納するリスト
	exp_name_list = []
	exp_office_list = []

	logging.info("スクレイピング処理1ページ目")
	# 会社名と勤務地を取得
	print("------------1ページ目------------")
	name_list = driver.find_elements_by_class_name("cassetteRecruit__name")
	selector = ".tableCondition tbody tr:nth-child(3) td"
	office_list = driver.find_elements_by_css_selector(selector)
	# tr[1仕事内容、2対象となる方、3勤務地、4給与、5初年度年収 ]

	print(f"取得件数： {len(name_list)}件")  # 検索結果の件数を表示
	for name,office in zip(name_list,office_list): # 件数分,ループでリストに追加
		exp_name_list.append(name.text[:10])
		exp_office_list.append(office.text[:10])
		log_con.info(f"{name.text[:10]}")


	# ページ移動関数の呼び出し（ドライバー、前ページ-1/次ページ+1）
	logging.info("ページ移動")
	page_mv(driver,1)
	print("------------2ページ目------------")

	# 会社名と勤務地を取得
	logging.info("スクレイピング処理2ページ目")
	selector = "cassetteRecruit__name"
	name_list = driver.find_elements_by_class_name(selector)
	selector = ".tableCondition tbody tr:nth-child(3) td"
	office_list = driver.find_elements_by_css_selector(selector)

	print(f"取得件数： {len(name_list)}件")  # 検索結果の件数を表示
	for name,office in zip(name_list,office_list): # 件数分,ループでリストに追加
		exp_name_list.append(name.text[:10])
		exp_office_list.append(office.text[:10])
		log_con.info(f"{name.text[:10]}")


	logging.info("CSVファイルに保存")

	recruit_pd = pd.DataFrame(             # pandas にデータ渡し
		{ "会社名":exp_name_list,
		"勤務地":exp_office_list },
		)

	recruit_pd.to_csv("T02-Recruit_data.csv") # pandas.to_csv でcsvﾌｧｲﾙに保存
	print(f"\n{len(exp_name_list)}件のデータを T02-Recruit_data.csv に保存しました。")

	logging.info( "－－－END－－－\n\n" )



if __name__ == "__main__":
	main()
