"""トーク辞書 (shiori/yaya/OnMastodon.dic) の簡易チェック。

問題があれば一覧を表示して終了コード1で終わる。
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

DIC_PATH = Path(__file__).resolve().parent.parent / 'shiori' / 'yaya' / 'OnMastodon.dic'
LIST_HEADER = 'CassisTalkList : array'
# Mastodon の投稿文字数上限
MAX_LENGTH = 500

TALK_LINE = re.compile(r'^\t"([^"]*)"$')
CHECKS = [
	# さくらスクリプトは Mastodon ではそのまま文字として出てしまう
	(re.compile(r'\\'), 'バックスラッシュ（さくらスクリプトの消し残し）があります'),
	# YAYA の埋め込み (%変数, %(式)) やさくらスクリプトの環境変数 (%ms 等)
	(re.compile(r'%[A-Za-z_(]'), '% による埋め込みがあります（意図したものか確認してください）'),
	(re.compile(r'[？！]'), '全角の ？ ！ があります（半角 ? ! に統一しています）'),
]


def main():
	errors = []
	seen = defaultdict(list)
	in_list = False
	for no, line in enumerate(DIC_PATH.read_text(encoding='utf-8').splitlines(), 1):
		if line.startswith(LIST_HEADER):
			in_list = True
			continue
		if not in_list:
			continue
		if line == '}':
			break
		stripped = line.strip()
		if stripped in ('', '{') or stripped.startswith('//'):
			continue
		m = TALK_LINE.match(line)
		if not m:
			errors.append((no, 'トークは「タブ + "本文"」の1行で、末尾に空白を付けずに書いてください', line))
			continue
		talk = m.group(1)
		seen[talk].append(no)
		if not talk:
			errors.append((no, '空のトークです', line))
		if len(talk) > MAX_LENGTH:
			errors.append((no, f'{MAX_LENGTH}文字を超えています（{len(talk)}文字）', line))
		for pattern, message in CHECKS:
			if pattern.search(talk):
				errors.append((no, message, line))

	if not in_list:
		errors.append((0, f'"{LIST_HEADER}" が見つかりません', ''))
	for talk, lines in seen.items():
		if len(lines) > 1:
			errors.append((lines[1], f'重複しています（{", ".join(map(str, lines))}行目）', talk))

	total = sum(len(v) for v in seen.values())
	if errors:
		for no, message, text in sorted(errors):
			print(f'{DIC_PATH.name}:{no}: {message}\n    {text.strip()}')
		print(f'\n{len(errors)}件の問題が見つかりました（トーク{total}件）。')
		return 1
	print(f'問題ありません（トーク{total}件）。')
	return 0


if __name__ == '__main__':
	sys.exit(main())
