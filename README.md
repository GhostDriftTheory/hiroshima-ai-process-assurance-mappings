# Profiles / Profile追加ガイド

各Profileは、**2ファイルだけ**で完結します。

```text
profiles/<slug>/
  README.md      人が読む説明、日本語・英語を同居
  profile.toml   対象・証拠・義務・Reporting v2限定ブリッジの正本
```

## 新規追加

```bash
python validate.py --init <new-slug>
```

11のHAIP行動とReporting v2の7セクションを安全側の`NOT_ASSESSED / NO_PROFILE_COVERAGE`で持つ下書きが作成されます。その後、次だけ行います。

1. 2ファイル内の残りの`REPLACE_*`を置換
2. 証拠を追加し、根拠がある義務だけ判定を引き上げる
3. ルートREADMEのProfile表へ1行追加
4. `python validate.py --profile <new-slug>`

既存Profileの証拠・判定を流用して自動的に穴埋めしてはいけません。参照する場合も、新Profile側で証拠、用途及び限界を明示します。

## English

A profile consists of exactly two maintained files. Run `python validate.py --init <slug>`, edit the two files, add one catalogue row to the root README, and run the validator. Profiles remain independent and are never aggregated into a HAIP compliance score.
