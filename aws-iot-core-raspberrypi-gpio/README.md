# Raspberry Pi and AWS IoT example

## 概要

こちらは Raspberry Pi に接続したスイッチの状態を AWS IoT Core に送信するサンプルプログラムです。

## 必要なハードウェア

- Raspberry Pi 3 Model B+ (およびmicroSD カード、電源ケーブル)
- ブレッドボード
- ジャンパーワイヤ
- タクトスイッチ

## 事前準備

- タクトスイッチを Raspberry Pi に接続します (片方を 3.3V, もう一方を GPIO に接続します)
- microSD カードに Raspberry Pi OS を書き込み、ネットワークに接続できるようにしておきます
- [AWS IoT Device SDK Python v2](https://github.com/aws/aws-iot-device-sdk-python-v2) を Raspberry Pi にインストールします: `pip3 install awsiotsdk`
- AWS IoT Core で発行したクライアント証明書・秘密鍵および、AWS IoT のルートCA証明書を Raspberry Pi にダウンロードしておきます
- `main.py` の27行目, 44〜47行目の設定をご自身の環境に合わせて修正します
