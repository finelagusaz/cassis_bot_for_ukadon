"""Claude API の認証（ID フェデレーション）だけを確認する。

Claude Console の Workload identity federation 設定で
「ワークロードを実行してください」と求められたときに、Actions から実行する。
最小限のリクエストを1回だけ送る（費用はごくわずか）。
"""
import os

import anthropic

MODEL = os.getenv('CLAUDE_MODEL', 'claude-opus-5-5')

client = anthropic.Anthropic()
response = client.messages.create(
	model=MODEL,
	max_tokens=64,
	output_config={'effort': 'low'},
	messages=[{'role': 'user', 'content': '「ok」とだけ返してください。'}],
)
print(f'認証に成功しました: model={response.model} stop_reason={response.stop_reason} '
	f'usage(in={response.usage.input_tokens}, out={response.usage.output_tokens})')
