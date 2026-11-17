"""任意の文面に、カシスがどう返事をするかを試す。

Mastodon には接続せず、投稿もしない。SOUL.md や返事の決まりを調整するときに使う。
文面は環境変数 TEST_MESSAGE で渡す（改行区切りで複数の文面を一度に試せる）。

注意: 公開リポジトリの Actions から実行すると、文面と返事はログに残り、誰でも読める。
"""
import os
import sys
from pathlib import Path

import anthropic

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import reply  # noqa: E402

ME = {'id': 'me'}


def main():
	messages = [m.strip() for m in os.getenv('TEST_MESSAGE', '').splitlines() if m.strip()]
	if not messages:
		sys.exit('環境変数 TEST_MESSAGE に試す文面を入れてください。')
	client = anthropic.Anthropic()
	system = reply.build_system_prompt()
	for text in messages:
		status = {'account': {'id': 'tester', 'acct': 'tester'}, 'content': text}
		print(f'> {text}')
		answer = reply.generate_reply(client, system, reply.build_user_message(ME, [], status))
		print(f'< {answer if answer is not None else "（返事をしない）"}\n')


if __name__ == '__main__':
	main()
