# atcoder-tool
atcoderのテストと提出をするやつ

完全に自分用です

## How to install
`pip3 install -U git+https://3to5thpower/atcoder_tool.git`

-Uオプションを付けないと途中で止まるので仕方なく付けています。

## How to use
`atcoder_tool login`でログインしてください。
セッションが保存されるので次回からはログインを省略できます。
セッションを破棄するときは`atcoder_tool logout`でそれが可能です。

`~/.config/atcoder_tool.toml`に設定を書きます。

`atcoder_tool new contest_name`で新しいディレクトリを作成します。
_contest\_name_ はatcoderのコンテストページのURLの`contests/`の直後の文字列です。ABCならabcxxxとなっています。

newコマンドを行うとディレクトリ内にa~fの6つの提出コード用のファイルとテストケース保存用のディレクトリが生成されます。
問題数が6問ではないときは`atcoder_tool new abcxxx -u 4`などと指定してください。

コードが書けたら`atcoder_tool test problem_id`でテストできます。
_problem\_id_ はaやb,fなどの小文字アルファベット1文字です。

標準入力からテストケースを入力したいときは`atcoder_tool run problem_id`を実行すると該当するコードを再コンパイルし通常通り実行してくれます。

テストできたら`atcoder_tool submit problem_id`で提出できます。
提出する際もテストを行い、通らなければキャンセルとなりますが、-fオプションで強制的に提出することもできます。