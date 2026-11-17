import os
import subprocess
import sys
from pathlib import Path

import requests

#投稿先のMastodonのURL
MASTODON_URL = 'https://ukadon.shillest.net/'
#公開範囲 public(公開), unlisted(未収載), private(フォロワーのみ), direct(指定された相手のみ) (directは宛先も必要)
VISIBILITY = 'unlisted'

BASE_DIR = Path(__file__).resolve().parent
SHIORICALLER = BASE_DIR / 'shioricaller' / 'shioricaller.exe'
REQUEST_FILE = BASE_DIR / 'shioricaller' / 'request.txt'
DLL_DIR = BASE_DIR / 'shiori' / 'yaya'
DLL_PATH = DLL_DIR / 'yaya.dll'
ENCODING = 'utf-8'


#栞へ送るリクエストを組み立てる
#トークの巡回位置として、通し番号があれば Reference0 で渡す
def build_request(serial=None):
	request = REQUEST_FILE.read_bytes().decode(ENCODING)
	if serial is not None:
		header = request.rstrip('\r\n')
		request = f'{header}\r\nReference0: {serial}\r\n\r\n'
	return request.encode(ENCODING)


#栞を呼び出して投稿メッセージを取得する
def get_message(serial=None):
	result = subprocess.run(
		# shioricaller はディレクトリ末尾に区切り文字を要求する
		[str(SHIORICALLER), str(DLL_PATH), f'{DLL_DIR}{os.sep}'],
		input=build_request(serial),
		capture_output=True,
		timeout=60,
		check=True,
	)
	response = result.stdout.decode(ENCODING)
	for line in response.splitlines():
		if line.startswith('Value: '):
			return line[len('Value: '):].replace(r'\n', '\n').strip()
	raise RuntimeError(f'栞の応答に Value がありません:\n{response}')


#Mastodonへ投稿する
def post_entry(mastodon_url, access_token, status, visibility='unlisted'):
	url = f'{mastodon_url}api/v1/statuses'
	headers = {'Authorization': f'Bearer {access_token}'}
	payload = {'status': status, 'visibility': visibility}
	r = requests.post(url, data=payload, headers=headers, timeout=30)
	r.raise_for_status()


if __name__ == '__main__':
	#アクセストークン これはGitHubのSettingでActions secretsを設定しておきます ナイショの文字列なので
	access_token = os.getenv('MASTODON_ACCESS_TOKEN')
	if not access_token:
		sys.exit('環境変数 MASTODON_ACCESS_TOKEN が設定されていません。')
	#投稿するメッセージ（GitHub Actions の実行番号でトークの巡回位置を決める）
	status = get_message(os.getenv('GITHUB_RUN_NUMBER'))
	if not status:
		sys.exit('栞から空のメッセージが返されたため、投稿を中止しました。')
	#投稿
	post_entry(MASTODON_URL, access_token, status, VISIBILITY)
	#ログメッセージ
	print(f'正常に {status} と投稿できました。')
