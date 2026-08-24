#!/usr/bin/env python3
"""Build a public Konbini Radar feed from fetched draft source pages."""

from __future__ import annotations

import argparse
from collections import Counter
import datetime as dt
from html import unescape
from html.parser import HTMLParser
import hashlib
import json
import pathlib
import re
import sys
import unicodedata
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "scripts" / "konbini_sources.json"
PRODUCT_SOURCE_PARSERS = {"seven_weekly", "familymart_weekly", "lawson_weekly", "lawson_lab_weekly"}
MAJOR_THREE_CHAINS = ("7-Eleven", "FamilyMart", "Lawson")
REGION_NAMES = {
    "全国",
    "北海道",
    "東北",
    "関東",
    "甲信越",
    "北陸",
    "東海",
    "近畿",
    "関西",
    "中国",
    "四国",
    "中国・四国",
    "九州",
    "沖縄",
}
CHAIN_NAMES = {
    "7-Eleven": ["セブン", "セブンイレブン", "セブン‐イレブン", "7-Eleven"],
    "FamilyMart": ["ファミマ", "ファミリーマート", "FamilyMart"],
    "Lawson": ["ローソン", "Lawson"],
    "Ministop": ["ミニストップ", "Ministop"],
    "NewDays": ["NewDays", "ニューデイズ"],
}
JP_CHAR_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")
# Lawson article footnotes / store-type disclaimers (not product names).
LAWSON_DISCLAIMER_RES = [
    re.compile(r"お取り扱いがありません"),
    re.compile(r"取り扱いのない場合がございます"),
    re.compile(r"一部取り扱いのない場合"),
    re.compile(r"イメージです"),
    re.compile(r"掲載当時の売価"),
    re.compile(r"フランチャイズチェーン本部"),
    re.compile(r"納品時間が異なる"),
    re.compile(r"内容が一部変更"),
    re.compile(r"ナチュラルローソン", re.I),
    re.compile(r"ローソンストア100"),
]
LAWSON_LAB_PRODUCT_BLOCK_RE = re.compile(
    r"<b>\s*([^<][^<]{0,200}?)\s*</b>\s*<br\s*/>\s*<b>\s*"
    r"(?:<span[^>]*>\s*)?(\d{4}年\d{1,2}月\d{1,2}日[^<]*?発売[^<]*?)(?:\s*</span>)?\s*"
    r"<br\s*/>\s*ローソン標準価格\s*([0-9,]+円\(税込\))",
    re.IGNORECASE | re.DOTALL,
)
LAWSON_NEW_CARD_RE = re.compile(
    r'<a\s+href="(/recommend/(?:original|new)/detail/\d+_\d+\.html)"[^>]*>([\s\S]*?)</a>',
    re.IGNORECASE,
)
FAMILYMART_NEW_CARD_RE = re.compile(
    r'<a\s+href="([^"]*family\.co\.jp/goods/[^"]+\.html)"\s+class="ly-mod-infoset3-link">([\s\S]*?)</a>\s*(?:<p class="ly-mod-infoset3-notes">\s*([\s\S]*?)\s*</p>)?',
    re.IGNORECASE,
)
OG_TITLE_RE = re.compile(
    r'<meta\s+property=["\']og:title["\']\s+content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
OG_IMAGE_RE = re.compile(
    r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
LAWSON_DETAIL_HERO_IMG_RE = re.compile(
    r'<p[^>]*class=(["\'])mb05\1[^>]*>\s*<img[^>]+src=(["\'])([^"\']+)\2',
    re.I,
)
SOURCE_NAME_TRANSLATIONS = {
    "えん食べ konbini roundup": "Entabe konbini roundup",
    "コンビニ チェッカー new items": "Conveni Checker new items",
    "コンビニエブリデイ new products": "Conveni Everyday new products",
    "節約速報 buy-one-get-one campaign roundup": "Setusoku BOGO campaign roundup",
    "もぐナビ konbini ranking": "Mognavi konbini ranking",
    "ローソン研究所 weekly featured products": "Lawson Lab weekly featured products",
}
SETUSOKU_CHAIN_HEADINGS = {
    "セブン-イレブン": "7-Eleven",
    "セブン‐イレブン": "7-Eleven",
    "セブンイレブン": "7-Eleven",
    "ファミリーマート": "FamilyMart",
    "ローソン": "Lawson",
    "ミニストップ": "Ministop",
    "ニューデイズ": "NewDays",
    "ローソンストア100": "Lawson Store 100",
    "デイリーヤマザキ": "Daily Yamazaki",
    "ポプラ": "Poplar",
    "セイコーマート": "Seicomart",
}
REGION_TRANSLATIONS = {
    "全国": "Nationwide",
    "北海道": "Hokkaido",
    "東北": "Tohoku",
    "関東": "Kanto",
    "甲信越": "Koshinetsu",
    "北陸": "Hokuriku",
    "東海": "Tokai",
    "近畿": "Kinki",
    "関西": "Kansai",
    "中国": "Chugoku",
    "四国": "Shikoku",
    "中国・四国": "Chugoku/Shikoku",
    "九州": "Kyushu",
    "沖縄": "Okinawa",
}
CATEGORY_TRANSLATIONS = {
    "おむすび": "Rice ball",
    "お弁当": "Bento",
    "サンドイッチ・ロールパン・バーガー": "Sandwiches, rolls, and burgers",
    "パン": "Bakery",
    "パスタ": "Pasta",
    "サラダ": "Salad",
    "チルド惣菜": "Chilled side dish",
    "デザート": "Dessert",
    "アイス": "Ice cream",
    "菓子": "Snacks",
    "飲料": "Drink",
    "日用品": "Daily goods",
    "キャラクターくじ・エンタメ雑貨など": "Character lottery and entertainment goods",
    "お菓子": "Sweets",
    "コーヒー・フラッペ": "Coffee and frappe",
    "焼き菓子・和菓子": "Baked and Japanese sweets",
    "関東限定 おむすび": "Kanto-only rice ball",
    "東北限定 おむすび": "Tohoku-only rice ball",
    "中国・四国限定 おむすび": "Chugoku/Shikoku-only rice ball",
    "関東限定 お弁当": "Kanto-only bento",
    "東海限定 お弁当": "Tokai-only bento",
}
# Longer phrases first; applied before PHRASE_TRANSLATIONS (see translate_japanese_text).
PRIORITY_JP_PHRASES = [
    ("Afternoon Tea監修 ピーチ香るティーソーダ 500ml", "Afternoon Tea-supervised peach-scented tea soda 500ml"),
    ("銀座デリー監修 カシミールカレー", "Ginza Delhi-supervised Kashmir curry"),
    ("いちごカスタードタルト", "strawberry custard tart"),
    ("プライチキャンペーン: カゴメ 私のフルーツこれ1本 マルチビタミン・1日分の鉄分いずれかを1本買うと、同商品いずれかが1本無料", "BOGO campaign: Kagome Watashi no Fruit Kore Ippon multivitamin or one-day iron, buy one get one free"),
    ("プライチキャンペーン: 三ツ矢サイダー クラシック 500mlを1本買うと、三ツ矢サイダー 500mlが1本無料", "BOGO campaign: Mitsuya Cider Classic 500ml, buy one get one Mitsuya Cider 500ml free"),
    ("【極旨！冷し麺】さっぽろ純連監修 冷し味噌まぜそば", "Sapporo Junren-supervised chilled miso maze-soba"),
    ("さっぽろ純連監修 冷し味噌まぜそば", "Sapporo Junren-supervised chilled miso maze-soba"),
    ("【関東の一部】武蔵野風冷しつけ汁肉うどん", "Musashino-style chilled meat udon with dipping broth"),
    ("【東京都の一部・神奈川県の一部】香り立つ しびれとコクの麻辣湯", "aromatic numbing rich malatang"),
    ("【東海】大盛ごはん！デミハンバーグ&から揚げ弁当", "Tokai large-rice demi hamburger steak and karaage bento"),
    ("【関西】だし巻き玉子&焼鳥重", "Kansai dashimaki egg and yakitori rice box"),
    ("【北陸】香り箱 天津飯", "Hokuriku Kaoribako crab-stick tenshinhan"),
    ("暴君ハバネロメンチカツバーガー", "Bokun Habanero menchi-katsu burger"),
    ("デミグラスソースの鉄板焼ハンバーグ弁当", "teppan-grilled hamburger steak bento with demi-glace sauce"),
    ("やわらかジューシーなグミを味わうグミショコラグレープ", "Gummy Chocolat grape with soft juicy gummies"),
    ("しその香りと魚介の旨み冷や汁", "chilled hiyajiru soup with shiso aroma and seafood umami"),
    ("しらす御飯 茨城県水揚げしらす使用", "shirasu rice with Ibaraki-landed whitebait"),
    ("会津産コシヒカリおむすび 炭火焼鳥", "Aizu Koshihikari rice ball with charcoal-grilled chicken"),
    ("山形県産つや姫おむすび 炭火焼鳥", "Yamagata Tsuyahime rice ball with charcoal-grilled chicken"),
    ("銀河のしずくおむすび 炭火焼鳥", "Ginga no Shizuku rice ball with charcoal-grilled chicken"),
    ("函館麺厨房あじさい 辛塩拉麺", "Hakodate Menchubo Ajisai spicy shio ramen"),
    ("徳島産業 レモンスライス爽やかジュレ", "Tokushima Sangyo refreshing lemon-slice jelly"),
    ("じゃがバター明太おむすび", "potato-butter mentaiko rice ball"),
    ("かむほど旨いたこ燻製", "chewy smoked octopus snack"),
    ("しかるねこぷっくりシール", "Shikaru Neko puffy stickers"),
    ("鉄鍋炒め 肉玉チャーハン", "iron-wok meat-and-egg chahan"),
    ("オールスター海苔弁当", "all-star nori bento"),
    ("フタバ食品 サクレスイカ", "Futaba Foods Sacre watermelon ice"),
    ("豚しゃぶカレー 県産豚使用", "pork shabu curry with local pork"),
    ("シャキシャキレタスサンド", "crisp lettuce sandwich"),
    ("ミックスサンド", "mixed sandwich"),
    ("イカフライ弁当", "squid-fry bento"),
    ("泡ピーチゼリー", "bubbly peach jelly"),
    ("とうもろこし御飯と梅御飯の焼き鯖弁当", "grilled mackerel bento with corn rice and ume rice"),
    ("丸永製菓 フルーツ盛りだくさん白くまバー", "Marunaga fruit-loaded Shirokuma ice bar"),
    ("混ぜ飯おむすびお茶漬け風ごはん 静岡茶使用", "ochazuke-style mixed-rice onigiri with Shizuoka tea"),
    ("ふわふわドームケーキ カスタードホイップ", "fluffy dome cake with custard whipped cream"),
    ("ちょこぶろっくしーるサンエックスユニバース", "Choco Block Seal San-X Universe"),
    ("ブリトータコスミートサルサチーズ", "burrito with taco meat, salsa, and cheese"),
    ("ミニ瀬戸しお えび塩味 51%増量", "mini Seto Shio shrimp chips, 51% bonus size"),
    ("なとり チータラ ピスタチオ風味", "Natori cheese-tara, pistachio flavor"),
    ("キャラポトレ／ディズニーキャラクター", "Chara-Potre Disney Characters"),
    ("ピリッと旨辛ビビンバおむすび", "spicy bibimbap rice ball"),
    ("パイン 塩パインアメ", "Pine salted pineapple candy"),
    ("具だくさん生姜スープ", "ginger soup with lots of ingredients"),
    ("サラダROLL 照焼チキン", "teriyaki chicken vegetable roll"),
    ("サラダROLL 豚しゃぶ", "pork shabu vegetable roll"),
    ("しそひじきおむすび", "shiso hijiki rice ball"),
    ("春日井 ゼリービーンズ", "Kasugai jelly beans"),
    ("明治 ジンジャーエールアップ", "Meiji Ginger Ale Up candy"),
    ("ヒアルロン酸が摂れるこんにゃくゼリー マスカット味", "hyaluronic acid konjac jelly, muscat flavor"),
    ("ちょこぶろっくしーる 思い出のサンリオキャラクターズ", "Choco Block Seal, nostalgic Sanrio Characters"),
    ("スーパーマリオ クムクムパズルヨッシー", "Super Mario Kumukumu Puzzle Yoshi"),
    ("スーパーマリオ ダイカットコインケース", "Super Mario die-cut coin case"),
    ("スーパーマリオ ヨッシー バスボール", "Super Mario Yoshi bath ball"),
    ("ふしぎ遊戯 トレーディングアクリルスタンド", "Fushigi Yugi trading acrylic stand"),
    ("ふしぎ遊戯 トレーディング缶バッジ", "Fushigi Yugi trading can badge"),
    ("山芳 ポテトチップス大人の夏味", "Yamayoshi potato chips, adult summer flavor"),
    ("スッパイマン 半生つまめる梅", "Suppaiman semi-dried snackable ume plums"),
    ("不二家 生ミルキー 愛媛県産せとか", "Fujiya fresh Milky, Ehime-grown Setoka orange"),
    ("うす焼きせんべい 唐辛子味", "thin senbei rice crackers, chili pepper flavor"),
    ("徳島産業 のびーるわらび餅", "Tokushima Sangyo stretchy warabi mochi"),
    ("小さなばかうけ 梅味", "mini Bakauke, ume flavor"),
    ("アマンドフロランタン", "almond florentine"),
    ("サンリオアクリルチャーム", "Sanrio acrylic charm"),
    ("ベイクドスイートポテト", "baked sweet potato"),
    ("マドレーヌグラッセ", "glazed madeleine"),
    ("揚げなすのおみそ汁", "fried eggplant miso soup"),
    ("ザクザク焼ドーナツ", "crunchy baked donut"),
    ("ベイクドショコラ", "baked chocolate"),
    ("あじの寿司", "horse mackerel sushi"),
    ("しいたけスナック うま塩味", "shiitake mushroom snack, savory salt flavor"),
    ("ほろにがコーヒーゼリードリンク", "bittersweet coffee jelly drink"),
    ("クリート もちまろグミもちしゅわアソート", "Cleat Mochimaro gummy fizzy assortment"),
    ("ドルチェ とろむに巨峰味", "Dolce Toromuni Kyoho grape flavor"),
    ("冷たいコーンポタージュ", "chilled corn potage"),
    ("モカショコラ", "mocha chocolate"),
    ("1食分の野菜が摂れる パリパリ麺のサラダ", "crispy noodle salad (one vegetable serving)"),
    ("ごまドレで食べるバンバンジー風サラダ", "bang bang chicken-style salad with sesame dressing"),
    ("雉虎亭キジ監修", "Kiji-supervised (Kijiko-tei)"),
    ("きじ監修", "Kiji-supervised"),
    ("ミルクたっぷり 塩バニララテ", "extra-milk salted vanilla latte"),
    ("塩バニララテ", "salted vanilla latte"),
    ("半熟玉子ぶっかけうどん", "udon with soft-boiled egg and chilled dashi poured on top"),
    ("温・冷　気分で選べる！ 半熟玉子ぶっかけうどん", "hot-or-cold udon with soft-boiled egg and chilled dashi poured on top"),
    ("玉子ぶっかけうどん", "udon with egg and chilled dashi poured on top"),
    ("ぶっかけうどん", "udon with chilled dashi poured on top"),
    ("たんぱく質が摂れる！しそ入り鶏つくねのサラダ", "Chicken tsukune salad with shiso (high protein)"),
    ("たんぱく質が摂れるチキンロール", "High protein chicken roll"),
    ("1食分の野菜が摂れる", "one vegetable serving"),
    ("パリパリ麺のサラダ", "crispy noodle salad"),
    ("ハムとマカロニのサラダ", "ham and macaroni salad"),
    # Onigiri / omusubi (long product-style strings first; parse uses regular spaces).
    ("炭火で焼いた焼おにぎり(ひしほ醤油使用)", "charcoal-grilled yaki onigiri (Hishiho soy sauce)"),
    ("味付のりおにぎり 山わさび(だし醤油仕立て)", "seasoned nori rice ball, mountain wasabi (dashi soy style)"),
    ("味付のりおにぎり 梅おかか", "seasoned nori rice ball, ume and bonito flakes"),
    ("おおきなおむすび すじこ(醤油麹仕立て)", "large rice ball, sujiko roe (soy sauce koji style)"),
    ("おおきなおむすび 和風ツナマヨネーズ", "large rice ball, Japanese-style tuna mayo"),
    ("だしむすび 焼しゃけ", "dashi-seasoned rice ball, grilled salmon"),
    ("五目おこわおむすび あぶくまもち使用", "gomoku okowa rice ball (Abukuma mochi rice)"),
    ("鶏ごぼう味めしおむすび 青森県産ごぼう使用", "chicken burdock seasoned rice ball (Aomori burdock)"),
    ("手巻おにぎり ピリ辛高菜", "hand-wrapped rice ball, spicy takana greens"),
    ("漬物おむすび 仙台味噌漬胡瓜", "pickle rice ball, Sendai miso pickled cucumber"),
    ("紀州南高梅使用カリカリ梅おむすび", "crunchy ume rice ball (Kishu Nanko ume)"),
    ("五穀米おむすび", "five-grain rice ball"),
    ("アスパラベーコンおむすび", "asparagus bacon rice ball"),
    ("佐賀県産さがびよりおむすび 柚子ちりめん", "Saga Sagabiyori rice ball, yuzu chirimen"),
    ("山形県産つや姫おむすび 柚子ちりめん", "Yamagata Tsuyahime rice ball, yuzu chirimen"),
    ("新潟県産コシヒカリおむすび 柚子ちりめん", "Niigata Koshihikari rice ball, yuzu chirimen"),
    ("旨さ相盛おむすび 卵黄とコク旨肉そぼろ", "double-topping rice ball, egg yolk and rich savory minced meat"),
    ("旨さ相盛おむすび 卵黄と肉そぼろ", "double-topping rice ball, egg yolk and minced meat"),
    ("こもち昆布おむすび", "komochi kelp rice ball"),
    ("ソースカツおむすび", "sauce katsu rice ball"),
    ("直巻おむすび 海老天むす", "hand-rolled omusubi, shrimp tempura temusu"),
    ("香ばし炒め玉子チャーハンおむすび", "aromatic fried-egg chahan rice ball"),
    ("おにぎり 紀州南高梅", "rice ball, Kishu Nanko ume"),
    ("焼きスフレサンド カスタードホイップ", "baked souffle sandwich with custard whipped cream"),
    ("ドルチェ あの夏のラムネグミ", "Dolce That Summer Ramune gummy"),
    ("かむかむ 南国フルーツソーダ", "Kamukamu tropical fruit soda"),
    ("スケープグレース ジントニック", "Scapegrace gin and tonic"),
    ("スケープグレース ブラックジンソーダ", "Scapegrace black gin soda"),
    ("ニンニクまぜそば", "garlic maze-soba"),
    ("レジットハイボール サイレントムーン", "Legit Highball Silent Moon"),
    ("レジットハイボール スプラッシュスター", "Legit Highball Splash Star"),
    ("サンヨー食品 サッポロ一番 あさ利監修 旨辛ネギラーメン", "Sanyo Foods Sapporo Ichiban Asari-supervised spicy negi ramen"),
    ("吉野家監修 具!おにぎり まるで牛すき丼", "Yoshinoya-supervised stuffed onigiri, beef sukiyaki-don style"),
    ("サンコック監修 黒酢からあげ", "Sancook-supervised black-vinegar karaage"),
    ("サンコック監修天津炒飯", "Sancook-supervised tenshin chahan"),
    ("ゴーゴーカレー監修 ロースかつカレー", "Go Go Curry-supervised loin katsu curry"),
    ("とろける白いミルクチーズケーキ 2個", "melting white milk cheesecake, 2-pack"),
    ("バター香るもちもち食感バター餅", "buttery aromatic chewy butter mochi"),
    ("高知県産ゆず ゆず香るいなり＆冷しぶっかけうどん", "Kochi yuzu inari and chilled broth-poured udon"),
    ("高知県産ゆず ゆず香るいなり and 冷しぶっかけうどん", "Kochi yuzu inari and chilled broth-poured udon"),
    ("もちむにシュー（いちごミルククリーム）", "Mochimuni cream puff (strawberry milk cream)"),
    ("もちぷよ(北海道産生クリーム入りミルククリーム)", "Mochipuyo milk cream with Hokkaido fresh cream"),
    ("ファミチキ（ファミマ味）", "Famichiki (Famima flavor)"),
    ("甘い香りとろける果肉白桃", "sweet aromatic melting white peach"),
    ("4種のひとくちサンドBOX", "4-kind bite-size sandwich box"),
    ("どらもっち バニラ", "Doramocchi vanilla"),
    ("アールグレイ 無糖 900ml", "Earl Grey unsweetened 900ml"),
    ("ジャスミン茶 900ml", "jasmine tea 900ml"),
    ("ゴロチョコ!ベーグル", "chunky chocolate bagel"),
    ("チョコバナナロール", "chocolate banana roll"),
    ("レモンジュレで食べるサーモンカルパッチョ", "salmon carpaccio to eat with lemon jelly"),
    ("ファミマ味お米スナック", "Famima-flavor rice snack"),
    ("ファミマ味ポテトチップス", "Famima-flavor potato chips"),
    ("ポテトチップスにんにく甘口しょうゆ味", "potato chips, mild garlic soy sauce flavor"),
    ("マルエス にんにくころろん 旨しおごま油味", "Maruesu Garlic Kororon, savory white sesame oil flavor"),
    ("壮関 あまみがつまったドライなし", "Sokan dried pear packed with sweetness"),
    ("大盛 ミートソース", "large-serving meat sauce pasta"),
    ("プラレールおふろで水あそびっこ", "Plarail bath water-play toy"),
    ("トミカ・プラレールブロック トーマス／パーシー／ジェームス", "Tomica Plarail Block Thomas/Percy/James"),
    ("はぴだんぶい アロハシャツキーホルダー", "Hapidanbui aloha shirt keychain"),
    ("はぴだんぶい エコバッグ", "Hapidanbui eco bag"),
    ("みんなのレモネード", "Minna no Lemonade"),
    ("キラぷるステッカーしずくちゃん", "Kirapuru sticker Shizuku-chan"),
    ("サンリオキャラクターズカードソフトクッキー", "Sanrio Characters card soft cookie"),
    ("ストロベリーフラッペ", "strawberry frappe"),
    ("レモンどら焼き", "lemon dorayaki"),
    ("井村屋 アンナミラーズアイス ダッチアップルパイ", "Imuraya Annamillers Dutch apple pie ice cream"),
    ("井村屋 アンナミラーズアイス ブルーベリーチーズケーキ", "Imuraya Annamillers blueberry cheesecake ice cream"),
    ("海老の寿司", "shrimp sushi"),
    ("天タレまぶしおむすび", "tempura sauce tossed rice ball"),
    ("直巻おむすび 広島菜", "hand-rolled omusubi with Hiroshima greens"),
]

PHRASE_TRANSLATIONS = {
    "セブンプレミアム": "Seven Premium",
    "ファミマル": "Famimaru",
    "ウチカフェ": "Uchi Cafe",
    "丸永製菓": "Marunaga",
    "春日井": "Kasugai",
    "なとり": "Natori",
    "明治": "Meiji",
    "ローソン標準価格": "Lawson standard price",
    "北海道産": "Hokkaido-grown",
    "北海道": "Hokkaido",
    "東北": "Tohoku",
    "関東": "Kanto",
    "東海": "Tokai",
    "北陸": "Hokuriku",
    "関西": "Kansai",
    "中国・四国": "Chugoku/Shikoku",
    "九州": "Kyushu",
    "沖縄": "Okinawa",
    "全国": "Nationwide",
    "ゴディバ": "GODIVA",
    "森半": "Morihan",
    "八天堂": "Hattendo",
    "天下一品": "Tenkaippin",
    "雉虎亭": "Kijiko-tei",
    "キジ": "Kiji",
    "七宝麻辣湯": "Shippo Malatang",
    "札幌すみれ": "Sapporo Sumire",
    "mofusand": "mofusand",
    "監修": "supervised",
    "ぶっかけ": "broth-poured",
    "わかめ": "wakame",
    "ちく玉天": "chikuwa tempura",
    "たぬき": "tanuki toppings",
    "数量限定": "limited quantity",
    "期間限定": "limited-time",
    "地域限定": "regional-only",
    "限定": "limited",
    "復刻": "revival",
    "再販売": "returning",
    "リニューアル": "renewed",
    "新発売": "new release",
    "大きな": "large",
    "たっぷり": "extra",
    "どかっと満足": "big satisfaction",
    "もちもち": "chewy",
    "もちっと": "chewy",
    "ふわもち": "fluffy-chewy",
    "ふんわり": "fluffy",
    "とろける": "melting",
    "濃厚": "rich",
    "濃い": "rich",
    "濃密": "dense",
    "さっぱり": "refreshing",
    "香る": "aromatic",
    "だし": "dashi",
    "鰹だし": "bonito dashi",
    "生パスタ": "fresh pasta",
    "半熟玉子": "soft-boiled egg",
    "温・冷": "hot or cold",
    "気分で選べる": "choose by mood",
    "冷し": "chilled",
    "冷やし": "chilled",
    "おにぎり": "rice ball",
    "おむすび": "rice ball",
    "むすび": "rice ball",
    "御握り": "rice ball",
    "混ぜ飯": "mixed rice",
    "お茶漬け風": "ochazuke-style",
    "静岡茶": "Shizuoka tea",
    "とうもろこし御飯": "corn rice",
    "梅御飯": "ume rice",
    "焼き鯖": "grilled mackerel",
    "焼鯖": "grilled mackerel",
    "しそひじき": "shiso hijiki",
    "ひじき": "hijiki",
    "ビビンバ": "bibimbap",
    "手巻": "hand-rolled",
    "寿司": "sushi",
    "弁当": "bento",
    "ブリトー": "burrito",
    "タコスミート": "taco meat",
    "サルサ": "salsa",
    "チーズ": "cheese",
    "丼": "rice bowl",
    "ごはん": "rice",
    "もち麦": "mochi barley",
    "麦入り": "with barley",
    "サンド": "sandwich",
    "ロール": "roll",
    "バーガー": "burger",
    "パン": "bread",
    "蒸しぱん": "steamed bread",
    "チュロッキー": "churro-style donut",
    "パスタ": "pasta",
    "ラーメン": "ramen",
    "焼きそば": "yakisoba",
    "焼そば": "yakisoba",
    "ヤキソバ": "yakisoba",
    "豚玉": "pork and egg",
    "そば": "soba",
    "うどん": "udon",
    "サラダROLL": "vegetable roll",
    "サラダ": "salad",
    "惣菜": "side dish",
    "スープ": "soup",
    "生姜": "ginger",
    "具だくさん": "lots of ingredients",
    "グラタン": "gratin",
    "お好み焼き": "okonomiyaki",
    "チキン": "chicken",
    "鶏": "chicken",
    "豚": "pork",
    "牛": "beef",
    "まぐろ": "tuna",
    "鮪": "tuna",
    "鮭": "salmon",
    "紅鮭": "red salmon",
    "さば": "mackerel",
    "いか": "squid",
    "海鮮": "seafood",
    "たらこ": "cod roe",
    "明太子": "spicy cod roe",
    "たくあん": "pickled daikon",
    "ガリ": "pickled ginger",
    "ねぎ": "green onion",
    "オクラ": "okra",
    "ごぼう": "burdock",
    "キャベツ": "cabbage",
    "トマト": "tomato",
    "しいたけ": "shiitake mushroom",
    "椎茸": "shiitake mushroom",
    "味噌": "miso",
    "醤油": "soy sauce",
    "照焼": "teriyaki",
    "照り焼き": "teriyaki",
    "うま塩味": "savory salt flavor",
    "うま塩": "savory salt",
    "えび塩味": "shrimp salt flavor",
    "塩パインアメ": "salted pineapple candy",
    "パインアメ": "Pineame pineapple candy",
    "塩": "salt",
    "塩レモン": "salt lemon",
    "梅しそ": "plum and shiso",
    "梅おかか": "ume plum and bonito flakes",
    "おかか": "bonito flakes",
    "うめ": "ume plum",
    "梅干し": "pickled ume plum",
    "佃煮": "tsukudani simmered preserve",
    "のり佃煮": "nori tsukudani",
    "海苔佃煮": "nori tsukudani",
    "味付のり": "seasoned nori",
    "味付けのり": "seasoned nori",
    "おおきな": "large",
    "ランチ": "lunch",
    "和風": "Japanese-style",
    "ツナマヨネーズ": "tuna mayo",
    "ツナ": "tuna",
    "マヨネーズ": "mayonnaise",
    "すじこ": "sujiko salted salmon roe",
    "醤油麹仕立て": "soy sauce koji-style",
    "醤油麹": "soy sauce koji",
    "スパイスキーマカレー": "spiced keema curry",
    "キーマカレー": "keema curry",
    "キーマ": "keema",
    "五目おこわ": "five-ingredient okowa",
    "五目": "five-ingredient",
    "おこわ": "okowa glutinous rice",
    "あぶくまもち": "Abukuma mochi rice",
    "青森県産": "Aomori-grown",
    "だしむすび": "dashi-seasoned rice ball",
    "焼しゃけ": "grilled salmon",
    "しゃけ": "salmon",
    "焼おにぎり": "grilled rice ball",
    "炭火で焼いた": "charcoal-grilled",
    "ひしほ醤油": "Hishiho soy sauce",
    "焼きめし": "grilled seasoned rice",
    "舞茸": "maitake mushroom",
    "菜めし": "vegetable rice",
    "漬物": "pickles",
    "仙台味噌漬胡瓜": "Sendai miso pickled cucumber",
    "味噌漬": "miso-pickled",
    "胡瓜": "cucumber",
    "ピリ辛": "spicy",
    "高菜": "takana mustard greens",
    "山わさび": "mountain wasabi",
    "紀州南高梅": "Kishu Nanko ume",
    "南高梅": "Nanko ume",
    "カリカリ梅": "crunchy ume",
    "直火焼": "open-flame grilled",
    "ソーセージ": "sausage",
    "仕立て": "style",
    "味めし": "seasoned rice",
    "抹茶": "matcha",
    "ほうじ茶": "hojicha",
    "黒ごま": "black sesame",
    "きなこ": "kinako roasted soybean flour",
    "あずき": "azuki bean",
    "練乳": "condensed milk",
    "いちご": "strawberry",
    "苺": "strawberry",
    "桃": "peach",
    "メロン": "melon",
    "マンゴー": "mango",
    "みかん": "mandarin orange",
    "アイス": "ice cream",
    "氷": "shaved ice",
    "バーアイスクリーム": "ice cream bar",
    "白くまバー": "Shirokuma ice bar",
    "フルーツ盛りだくさん": "fruit-loaded",
    "フォンダンショコラ": "fondant chocolate",
    "チョコレート": "chocolate",
    "チョコ": "chocolate",
    "ゼリービーンズ": "jelly beans",
    "ジンジャーエールアップ": "Ginger Ale Up candy",
    "チータラ": "cheese-tara",
    "ピスタチオ風味": "pistachio flavor",
    "塩パイン": "salted pineapple",
    "パイン": "pineapple",
    "ミニ瀬戸しお": "mini Seto Shio shrimp chips",
    "瀬戸しお": "Seto Shio shrimp chips",
    "増量": "bonus size",
    "パフェ": "parfait",
    "大福": "daifuku",
    "クレープ": "crepe",
    "カフェラテ": "café latte",
    "ラテ": "latte",
    "ミルク": "milk",
    "バニラ": "vanilla",
    "スナック": "snack",
    "ファミマ味": "Famima-flavor",
    "ファミマ": "Famima",
    "ファミチキ": "Famichiki",
    "サッポロ一番": "Sapporo Ichiban",
    "サンヨー食品": "Sanyo Foods",
    "あさ利": "Asari",
    "吉野家": "Yoshinoya",
    "ゴーゴーカレー": "Go Go Curry",
    "サンコック": "Sancook",
    "黒酢からあげ": "black-vinegar karaage",
    "天津炒飯": "tenshin chahan",
    "ロースかつカレー": "loin katsu curry",
    "旨辛ネギラーメン": "spicy negi ramen",
    "ネギラーメン": "negi ramen",
    "チーズケーキ": "cheesecake",
    "バター餅": "butter mochi",
    "どらもっち": "Doramocchi",
    "アールグレイ": "Earl Grey",
    "ジャスミン茶": "jasmine tea",
    "無糖": "unsweetened",
    "ベーグル": "bagel",
    "カルパッチョ": "carpaccio",
    "レモンジュレ": "lemon jelly",
    "ポテトチップス": "potato chips",
    "お米": "rice",
    "にんにく": "garlic",
    "ニンニク": "garlic",
    "甘口": "mild",
    "しょうゆ味": "soy sauce flavor",
    "醤油味": "soy sauce flavor",
    "昆布": "kelp",
    "こもち昆布": "komochi kelp",
    "ソースカツ": "sauce katsu",
    "直巻": "hand-rolled",
    "海老天むす": "shrimp tempura temusu",
    "天むす": "tempura rice ball",
    "海老": "shrimp",
    "プラレール": "Plarail",
    "トミカ": "Tomica",
    "大盛": "large-serving",
    "ミートソース": "meat sauce",
    "そぼろ": "minced meat",
    "コク旨": "rich savory",
    "卵黄": "egg yolk",
    "ドライなし": "dried pear",
    "ごま油": "sesame oil",
    "旨しお": "savory salt",
    "ハイボール": "highball",
    "レジット": "Legit",
    "マルエス": "Maruesu",
    "壮関": "Sokan",
    "一番くじ": "Ichiban Kuji lottery",
    "ソックス": "socks",
    "ウエハース": "wafer snack",
    "わっふれーむ": "waffle-frame character snack",
    "ちょこぶろっくしーる": "Choco Block Seal",
    "サンエックスユニバース": "San-X Universe",
    "サンエックス": "San-X",
    "キャラポトレ": "Chara-Potre",
    "ディズニーキャラクター": "Disney Characters",
    "ブルーロック": "Blue Lock",
    "アクリルスタンド": "acrylic stand",
    "缶バッジ": "can badge",
    "おつまみ": "snack",
    "ごまドレ": "sesame dressing",
    "バンバンジー": "bang bang chicken",
    "バンバンジー風": "bang bang chicken-style",
    "ハム": "ham",
    "マカロニ": "macaroni",
    "パリパリ": "crispy",
    "パリパリ麺": "crispy noodles",
    "野菜": "vegetables",
    "食分": "serving",
    "で食べる": "to eat with",
}


class SourceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.events: list[dict[str, str]] = []
        self._link_href = ""
        self._link_text: list[str] = []
        self._heading_tag = ""
        self._heading_text: list[str] = []
        self.title = ""
        self._in_title = False
        self._title_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key: value or "" for key, value in attrs}
        if tag == "a":
            self._link_href = attr_map.get("href", "")
            self._link_text = []
        elif tag in {"h1", "h2", "h3", "h4"}:
            self._heading_tag = tag
            self._heading_text = []
        elif tag == "title":
            self._in_title = True
            self._title_text = []

    def handle_data(self, data: str) -> None:
        text = clean_text(data)
        if not text:
            return
        if self._in_title:
            self._title_text.append(text)
        if self._heading_tag:
            self._heading_text.append(text)
        if self._link_href:
            self._link_text.append(text)
        if not self._in_title and not self._link_href and not self._heading_tag:
            self.events.append({"type": "text", "text": text})

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._link_href:
            text = clean_text(" ".join(self._link_text))
            if text:
                self.events.append({"type": "link", "text": text, "href": self._link_href})
            self._link_href = ""
            self._link_text = []
        elif tag == self._heading_tag:
            text = clean_text(" ".join(self._heading_text))
            if text:
                self.events.append({"type": "heading", "tag": self._heading_tag, "text": text})
            self._heading_tag = ""
            self._heading_text = []
        elif tag == "title" and self._in_title:
            self.title = clean_text(" ".join(self._title_text))
            self._in_title = False
            self._title_text = []


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\u3000", " ")).strip()


def extract_og_title(html: str) -> str:
    match = OG_TITLE_RE.search(html or "")
    return clean_text(match.group(1)) if match else ""


def extract_og_image(html: str) -> str:
    match = OG_IMAGE_RE.search(html or "")
    return clean_text(unescape(match.group(1))) if match else ""


def fix_lawson_image_url(url: str, base: str = "https://www.lawson.co.jp") -> str:
    raw = clean_text(unescape(url or ""))
    if not raw:
        return ""
    raw = raw.replace("https://www.lawson.co.jphttps://", "https://")
    raw = raw.replace("http://www.lawson.co.jphttp://", "http://")
    if raw.startswith("//"):
        return f"https:{raw}"
    if raw.startswith("/"):
        return absolute_url(raw, base)
    return raw


def extract_lawson_detail_h2_title(html: str) -> str:
    match = re.search(
        r'<h2[^>]*class=(["\'])ttl\1[^>]*>\s*([^<]+?)\s*</h2>',
        html or "",
        re.I,
    )
    if not match:
        return ""
    return normalize_lawson_product_name(unescape(match.group(2)))


def extract_lawson_detail_hero_image(html: str) -> str:
    hero = LAWSON_DETAIL_HERO_IMG_RE.search(html or "")
    if hero:
        return fix_lawson_image_url(hero.group(3))
    fallback = re.search(
        r'src=(["\'])(/recommend/(?:original|new)/detail/img/[^"\']+\.(?:png|jpe?g|webp))\1',
        html or "",
        re.I,
    )
    return fix_lawson_image_url(fallback.group(2)) if fallback else ""


def lawson_detail_thumbnail_from_html(html: str) -> str:
    og = fix_lawson_image_url(extract_og_image(html))
    if og:
        return og
    return extract_lawson_detail_hero_image(html)


def is_lawson_disclaimer_text(text: str) -> bool:
    t = clean_text(text)
    if not t:
        return False
    return any(pattern.search(t) for pattern in LAWSON_DISCLAIMER_RES)


def normalize_lawson_product_name(name: str) -> str:
    t = clean_text(name)
    t = unicodedata.normalize("NFKC", t)
    t = re.sub(r"^※+\s*", "", t)
    # Trailing regional / footnote tails (e.g. "…※沖縄ではお取り扱いが～") are not part of the product name.
    t = re.sub(r"\s*※\s*沖縄[^※]*$", "", t, flags=re.DOTALL)
    t = re.sub(r"\s*※\s*(?:画像|店舗|店頭|パッケージ|表示|参考)[^※]*$", "", t)
    t = t.replace("\u3000", " ")
    t = re.sub(r"\s+", " ", t).strip(" ・、,，")
    return t


def is_weak_lawson_title(name: str) -> bool:
    t = normalize_lawson_product_name(name)
    if len(t) < 3:
        return True
    if is_lawson_disclaimer_text(t):
        return True
    if not JP_CHAR_RE.search(t) and len(t) < 12:
        return True
    if re.fullmatch(r"[\W_]+", t, flags=re.UNICODE):
        return True
    return False


def extract_lawson_lab_product_rows(html: str) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for match in LAWSON_LAB_PRODUCT_BLOCK_RE.finditer(html or ""):
        name = normalize_lawson_product_name(match.group(1))
        date_text = clean_text(match.group(2))
        price_text = clean_text(match.group(3))
        rows.append((name, date_text, price_text))
    return rows


def translate_regions(regions: list[str]) -> list[str]:
    translated = []
    for region in regions:
        translated.append(REGION_TRANSLATIONS.get(region, translate_japanese_text(region, "region")))
    return translated


def translate_category(category: str) -> str:
    if not category:
        return ""
    return CATEGORY_TRANSLATIONS.get(category, translate_japanese_text(category, "category"))


def translate_qualifier_text(text: str) -> str:
    """Translate bracketed qualifiers without creating "Region regional" tails."""
    if "極旨" in text or "冷し麺" in text:
        return "premium chilled noodle"
    qualifier = translate_japanese_text(text, "region").strip()
    if not qualifier or qualifier.lower() == "region":
        return "regional"
    if re.search(r"\bregional(?:-only)?\b", qualifier, re.IGNORECASE):
        return qualifier
    if "監修" in text:
        return qualifier
    # Campaign banners (bonus size, sales) are nationwide promotions, not regional limits.
    if re.search(r"増量|作戦|キャンペーン|セール|お値段", text):
        return qualifier
    return f"{qualifier} regional"


def translate_japanese_text(text: str, fallback: str = "item") -> str:
    """Best-effort glossary translation for public English feed fields."""
    if not text:
        return ""
    value = clean_text(text)
    value = unicodedata.normalize("NFKC", value)
    value = value.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
    value = re.sub(r"【([^】]+)】", lambda match: f" {translate_qualifier_text(match.group(1))} ", value)
    value = value.replace("＆", " and ").replace("&", " and ").replace("　", " ")
    value = value.replace("（", " (").replace("）", ") ")
    for japanese, english in sorted(PRIORITY_JP_PHRASES, key=lambda item: len(item[0]), reverse=True):
        jp_key = unicodedata.normalize("NFKC", japanese)
        value = re.sub(re.escape(jp_key), f" {english} ", value)
    for japanese, english in sorted(PHRASE_TRANSLATIONS.items(), key=lambda item: len(item[0]), reverse=True):
        jp_key = unicodedata.normalize("NFKC", japanese)
        value = re.sub(re.escape(jp_key), f" {english} ", value)
    value = value.replace("・", " ")
    value = re.sub(r"[\u3040-\u30ff\u3400-\u9fff]+", " ", value)
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"\bregional regional\b", "regional", value, flags=re.IGNORECASE)
    value = re.sub(r"\blimited limited\b", "limited", value, flags=re.IGNORECASE)
    value = re.sub(r"\bbonus size bonus size\b", "bonus size", value, flags=re.IGNORECASE)
    value = re.sub(r"\s+([),.!?])", r"\1", value)
    value = re.sub(r"([(])\s+", r"\1", value)
    value = value.strip(" -_/・、。:：")
    if not value:
        return fallback.title()
    return value[:1].upper() + value[1:]


def translate_price(price_text: str) -> str:
    if not price_text:
        return ""
    value = price_text
    value = value.replace("（税込", " (tax incl. ")
    value = value.replace("税込", "tax incl.")
    value = value.replace("）", ")")
    value = value.replace("円", " yen")
    value = value.replace("本体価格", "base price")
    return clean_text(value)


SANITIZE_ENGLISH_PATTERNS = [
    # Whole phrase first (modifiers like "egg bukkake udon").
    (re.compile(r"\bbukkake\s+(udon|soba)\b", re.I), r"broth-poured \1"),
    (re.compile(r"\bbukkake\b", re.I), "broth-poured"),
    (re.compile(r"\b([a-z][a-z-]+)\s+\(\1\)", re.I), r"\1"),
    (re.compile(r"\bpork and egg and yakisoba\b", re.I), "pork and egg & yakisoba"),
    (re.compile(r"\bbread\s+bread\b", re.I), "bread"),
    (re.compile(r"\bsushi\s+sushi\b", re.I), "sushi"),
    (re.compile(r"\bice cream\s+ice cream\b", re.I), "ice cream"),
    (re.compile(r"\brice\s+rice ball\b", re.I), "rice ball"),
    (re.compile(r"\bregion\s+regional\b", re.I), "regional"),
    (re.compile(r"\bregional\s+regional\b", re.I), "regional"),
    (re.compile(r"^\d{4}\s+\d{1,2}\s+\d{1,2}\s+regional\b.*\bregional$", re.I), "Regional konbini ranking"),
    # Half-width / broken tokenizer cases where "latte" drops out.
    (re.compile(r"\bsalt vanilla\b(?!\s+latte\b)", re.I), "salted vanilla latte"),
    (re.compile(r"\bsalted vanilla\b(?!\s+latte\b)(?=\s|$|\d)", re.I), "salted vanilla latte"),
]


def sanitize_english_output(text: str) -> str:
    if not text:
        return ""
    value = clean_text(text)
    for pattern, replacement in SANITIZE_ENGLISH_PATTERNS:
        value = pattern.sub(replacement, value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


MAX_PRODUCT_TITLE_CHARS = 60

# Product names that are category-sized English tokens (misleading when JP title is specific).
_GENERIC_TITLE_BODY_RE = re.compile(
    r"^(?:salad|snack|desserts?|bread|item|sandwich|pasta|ramen|udon|soba|donuts?|coffee|cake|curry|noodles?|noodle|bento|sushi|drinks?|rice ball|salt)$",
    re.IGNORECASE,
)
_GENERIC_TITLE_WITH_NUMBER_RE = re.compile(
    r"^\d+\s+(?:salad|snack|desserts?|bread|item)$",
    re.IGNORECASE,
)

PRODUCT_SPECIFIC_NOTES = {
    "Afternoon Tea監修 ピーチ香るティーソーダ 500ml": (
        "A peach-scented sparkling tea developed under the Afternoon Tea brand, in a 500ml bottle."
    ),
    "【北海道・東北・関東】LabQ監修 かつお香るコク旨チャーシューおむすび～爽快生姜煮入り～": (
        "A LabQ-supervised rice ball with bonito-scented chashu and a bright ginger accent."
    ),
    "【北海道・東北・関東】LabQ監修 至高の一杯冷製煮干し醤油らぁ麺": (
        "A cold ramen from LabQ built around dried-sardine shoyu broth; sold only in Hokkaido, Tohoku and Kanto."
    ),
    "ほたて日和監修 帆立味塩そば～すだち仕上げ～": (
        "Hotate Biyori-supervised salt noodles with scallop flavor and a sudachi citrus finish."
    ),
    "銀座デリー監修 カシミールカレー": (
        "Ginza Delhi supervises this Kashmir-style curry, part of 7-Eleven's summer curry lineup."
    ),
    "大きなふわもち生大福（いちごホイップ&練乳）": (
        "A large soft-chewy daifuku filled with strawberry whipped cream and condensed milk."
    ),
    "明治 辻利 抹茶ティラミス": (
        "Meiji ice cream pairing Tsujiri matcha with a tiramisu-style format."
    ),
    "エリックサウス監修 ２種スパイスカレー": (
        "A two-curry spice plate supervised by South Indian restaurant Eric South."
    ),
    "銀座デリー監修ドライカレーおむすび": (
        "A dry-curry rice ball supervised by Ginza Delhi."
    ),
    "いちごカスタードタルト": (
        "A strawberry custard tart from Lawson's chilled dessert range."
    ),
    "いちごミルク杏仁": (
        "An almond-jelly dessert paired with strawberry milk."
    ),
    "ゆずポン酢仕立て 夏野菜のネバネバご飯(麦入りご飯)": (
        "Barley-mixed rice with sticky summer vegetables, dressed with yuzu ponzu."
    ),
    "純水仕立て しゃきっと果実 オレンジ&マンゴー": (
        "A chilled orange-and-mango fruit cup packed in purified water."
    ),
    "じゅーしー２個入り": (
        "Jushi is an Okinawan seasoned rice; this two-piece pack is sold in Okinawa only."
    ),
    "チーズキンパ ５巻": (
        "Gimbap is Korean-style rolled rice; this five-piece pack is Hokkaido only."
    ),
    "とろけるわらび餅": (
        "Warabimochi is a soft, jelly-like mochi made from bracken starch rather than rice."
    ),
    "アイスゆずシトラスティー": (
        "A chilled yuzu citrus tea, not an ice cream, despite the Japanese アイス prefix."
    ),
    "【お値段そのまま おかわり45％増量作戦】甘栗むいちゃいました": (
        "Pre-peeled sweet chestnuts sold at the usual price with 45% more in the bag."
    ),
    "日本のフルーツ 北海道産メロン 70ml": (
        "A single 70ml frozen fruit bar from Lawson's Japanese Fruit range."
    ),
    "おおきなおむすび ゆかり": (
        "Yukari is a dried red-shiso furikake seasoning mixed through the rice."
    ),
    "【九州】ばくだんむすび（唐揚げ・高菜・マヨネーズ）": (
        "Bakudan musubi is an oversized rice ball; takana is pickled mustard greens."
    ),
    "【中国・四国】広島お好み焼 肉玉そば": (
        "Hiroshima-style okonomiyaki layers the savory pancake over fried soba noodles."
    ),
    # Week of 2026-08-24
    "なべやき屋キンレイ ナガラ食品監修 和風だし香るホルモン鍋焼うどん": (
        "Nabeyaki udon served hotpot-style; horumon here means stewed offal, not hormones."
    ),
    "ぼんご監修 大きなおむすび 生たらこと漬けまぐろ入りまぐろたたき": (
        "A large Bongo rice ball pairing fresh tarako with tuna tataki."
    ),
    "麺屋極鶏 鶏だく だく郎": (
        "Packaged ramen from Menya Gokukei, loaded with extra chicken."
    ),
}

PRODUCT_SPECIFIC_TITLES = {
    "Afternoon Tea監修 ピーチ香るティーソーダ 500ml": "Afternoon Tea peach-scented tea soda 500ml",
    "【北海道・東北・関東】LabQ監修 かつお香るコク旨チャーシューおむすび～爽快生姜煮入り～": (
        "LabQ bonito-chashu rice ball with ginger"
    ),
    "【北海道・東北・関東】LabQ監修 至高の一杯冷製煮干し醤油らぁ麺": (
        "LabQ cold niboshi-shoyu ramen"
    ),
    "ほたて日和監修 帆立味塩そば～すだち仕上げ～": (
        "Hotate Biyori scallop salt noodles with sudachi"
    ),
    "銀座デリー監修 カシミールカレー": "Ginza Delhi Kashmir curry",
    "大きなふわもち生大福（いちごホイップ&練乳）": (
        "Large daifuku with strawberry cream and condensed milk"
    ),
    "明治 辻利 抹茶ティラミス": "Meiji x Tsujiri matcha tiramisu ice cream",
    "エリックサウス監修 ２種スパイスカレー": "Eric South two-spice curry plate",
    "銀座デリー監修ドライカレーおむすび": "Ginza Delhi dry-curry rice ball",
    "いちごカスタードタルト": "Strawberry custard tart",
    "いちごミルク杏仁": "Strawberry-milk almond jelly",
    "ゆずポン酢仕立て 夏野菜のネバネバご飯(麦入りご飯)": (
        "Yuzu-ponzu summer vegetable rice with barley"
    ),
    "純水仕立て しゃきっと果実 オレンジ&マンゴー": "Orange and mango fruit cup",
    # Week of 2026-08-10 — Lawson
    "ご褒美スティックケーキ パリっとふわとろショコラ(ベルギーチョコ使用)": (
        "Belgian chocolate stick cake"
    ),
    "カカオ香るショコラクレープ(ベルギーチョコ使用)": "Belgian chocolate crepe",
    "バニラムースをのせたコーヒーゼリー": "Coffee jelly topped with vanilla mousse",
    "ビッグピート クレイジースモーキーエディション 200ml": "Big Peat Crazy Smoky Edition 200ml",
    "ビッグピート クレイジースモーキーハイボール 350ml": "Big Peat Crazy Smoky highball 350ml",
    "ビッグピート スーパースモーキーハイボール 350ml": "Big Peat Super Smoky highball 350ml",
    "ジンクス ジンソーダ 350ml": "Jinx gin soda 350ml",
    "アイスゆずシトラスティー": "Iced yuzu citrus tea",
    "メガアイスゆずシトラスティー": "Mega iced yuzu citrus tea",
    "とろけるわらび餅": "Melt-in-the-mouth warabimochi",
    "まんまる鶏&ハンバーグ弁当": "Round chicken and hamburg steak bento",
    "ごはん大盛!まんまる鶏&ハンバーグ弁当": (
        "Round chicken and hamburg steak bento, extra rice"
    ),
    "手巻寿司 たっぷりコーンマヨ": "Hand-rolled sushi with corn mayo",
    "日本ルナ株式会社 アサイーボウルヨーグルト&ハニーグラノーラ": (
        "Nippon Luna acai bowl yogurt with honey granola"
    ),
    "日本のフルーツ 北海道産メロン 70ml": "Japanese Fruit bar: Hokkaido melon 70ml",
    "日本のフルーツ 栃木県産幸水 70ml": "Japanese Fruit bar: Tochigi Kosui pear 70ml",
    # Week of 2026-08-10 — 7-Eleven
    "じゅーしー２個入り": "Jushi Okinawan seasoned rice, 2 pieces",
    "鶏釜めし仕立て": "Chicken kamameshi-style rice",
    "チーズキンパ ５巻": "Cheese gimbap, 5 pieces",
    "味付海苔 徳島ラーメン風 豚肉煮": "Tokushima ramen-style simmered pork rice ball",
    "味付海苔 生姜焼き": "Ginger-pork rice ball with seasoned nori",
    "照焼チキンわさびマヨ 静岡県産本わさび使用": (
        "Teriyaki chicken with Shizuoka wasabi mayo"
    ),
    "熟成だれの牛カルビ弁当": "Beef kalbi bento in aged tare sauce",
    "ＣＡＦＥ ＢＯＸ プルドポーク": "CAFE BOX pulled pork",
    "よくばりサンド チョコミント": "Yokubari dessert sandwich, choco mint",
    "３種のフルーツサンド": "Three-fruit sandwich",
    # Week of 2026-08-10 — FamilyMart
    "一番くじ ナルミヤキャラクターズ ～あの頃のときめきメモリーズ～": (
        "Ichiban Kuji: Narumiya Characters lottery"
    ),
    "Happyくじ/ MARVEL『スパイダーマン：ブランド・ニュー・デイ』": (
        "Happy Kuji: Marvel Spider-Man Brand New Day"
    ),
    "【お値段そのまま おかわり45％増量作戦】UHA味覚糖 コロロ清水白桃45%増量": (
        "UHA Kororo white peach gummies, 45% bonus size"
    ),
    "【お値段そのまま おかわり45％増量作戦】増量 ファミマ・ザ・クレープ 生チョコ": (
        "Famima The Crepe nama chocolate, 45% bonus size"
    ),
    "【お値段そのまま おかわり45％増量作戦】増量ファミチキ": "Famichiki, 45% bonus size",
    "【お値段そのまま おかわり45％増量作戦】甘栗むいちゃいました": (
        "Peeled sweet chestnuts, 45% bonus size"
    ),
    "ラインソックス 砂漠と青空/ブラック": "Line socks, desert and blue sky (black)",
    "ラインソックス 砂漠と青空/ホワイト": "Line socks, desert and blue sky (white)",
    "きゃらねいるぱーつ マイメロディ&クロミ": (
        "Character nail parts: My Melody and Kuromi"
    ),
    "にじさんじポップコーンvol.3 うすしお味": (
        "Nijisanji popcorn vol.3, lightly salted"
    ),
    "文豪ストレイドッグス んまほっぺ ミニアクリルスタンド": (
        "Bungo Stray Dogs mini acrylic stand"
    ),
    "もっちり食感の明太マヨ焼うどん": "Chewy mentaiko-mayo yaki udon",
    "カルビー じゃがりこ まじカルパス味bits": (
        "Calbee Jagarico bits, Kalpas sausage flavor"
    ),
    "ソーセージバジルフランス6個入": "Sausage and basil French rolls, 6 pieces",
    "トリプルチョコのホイップデニッシュ": "Triple chocolate whipped-cream danish",
    "ピザ&チーズ": "Pizza and cheese bread",
    "塩バターパン（つぶあん）": "Salted butter bread with chunky red bean paste",
    "大盛！直火炒めの黒炒飯": "Wok-fired black fried rice, large serving",
    "明治 ザクット チョコバナナ味": "Meiji Zakutto choco banana",
    # Week of 2026-08-10 — FamilyMart regional items (region badge already carries the limit)
    "【九州】6種具材の冷しぶっかけ手延素麺": (
        "Chilled broth-poured somen with six toppings"
    ),
    "【関西】たんぱく質が摂れる！豚ロースの冷しゃぶサラダ": (
        "Chilled pork loin shabu salad, high protein"
    ),
    "【中国・四国】広島お好み焼 肉玉そば": (
        "Hiroshima okonomiyaki with pork, egg and soba"
    ),
    "【九州】ばくだんむすび（唐揚げ・高菜・マヨネーズ）": (
        "Bakudan rice ball: karaage, takana and mayo"
    ),
    "【九州】ばくだんむすび（海老・ツナ・鮭マヨネーズ）": (
        "Bakudan rice ball: shrimp, tuna and salmon mayo"
    ),
    "【北海道・東北】大盛！豚肉のせお好み焼&焼そば": (
        "Large okonomiyaki topped with pork, plus yakisoba"
    ),
    "【東京都の一部・神奈川県の一部】国産鶏むね肉と厚切りトマトゆで玉子のクラブハウスサンド": (
        "Clubhouse sandwich with chicken, tomato and egg"
    ),
    "【東北】背脂煮干し焼そば（にんにく入り）": (
        "Back-fat niboshi yakisoba with garlic"
    ),
    "【東海】手巻 甘辛から揚げマヨネーズ": (
        "Hand-rolled sushi with sweet-spicy karaage mayo"
    ),
    "【東海・北陸】ロメインレタス使用 シーザーサラダ": "Caesar salad with romaine lettuce",
    "【関東】いか明太子と卵黄醤油だれおむすび": (
        "Squid mentaiko rice ball with egg-yolk soy tare"
    ),
    "【関東】お味噌で食べるおつまみ野菜": "Snack vegetables served with miso dip",
    "【静岡県の一部】豚焼肉&焼そば弁当": "Grilled pork and yakisoba bento",
    # Week of 2026-08-10 — 7-Eleven large rice balls
    "おおきなおむすび ゆかり": "Large rice ball with yukari shiso furikake",
    "おおきなおむすび 鶏唐揚げマヨネーズ": "Large rice ball with karaage and mayo",
    "おおきなおむすび上伊那産アスパラとベーコン": (
        "Large rice ball with Kami-Ina asparagus and bacon"
    ),
    # Week of 2026-08-24 — Lawson
    "なべやき屋キンレイ ナガラ食品監修 和風だし香るホルモン鍋焼うどん": (
        "Kinrei x Nagara horumon nabeyaki udon"
    ),
    "ティラミスパフェ": "Tiramisu parfait",
    "おかズドン!黒胡椒にんにくだれ鶏唐揚弁当": (
        "Okazu Don black-pepper garlic karaage bento"
    ),
    "くるみパン 4個入": "Walnut bread, 4 pieces",
    "チョコバナナ": "Chocolate banana",
    "フィッシュバーガー タルタルソース": "Fish burger with tartar sauce",
    "大きなおにぎり 辛旨キムチチャーハン": (
        "Large rice ball, spicy kimchi fried rice"
    ),
    "白いティラミスクレープ": "White tiramisu crepe",
    "魏さんの本格よだれ鶏": "Wei's Sichuan chili chicken",
    "鶏肉とザーサイの湯葉巻き": "Chicken and zha cai yuba rolls",
    # Week of 2026-08-24 — FamilyMart
    "ぼんご監修 大きなおむすび 煮たまごと肉そぼろマヨ": (
        "Bongo large rice ball with egg and meat soboro mayo"
    ),
    "ぼんご監修 大きなおむすび 生たらこと漬けまぐろ入りまぐろたたき": (
        "Bongo large rice ball with tarako and tuna tataki"
    ),
    "【東京都の一部・神奈川県の一部】国産鶏むね肉と小松菜の豆乳担担春雨スープ": (
        "Soy-milk tantan harusame soup with chicken and komatsuna"
    ),
    "【東海】冷しうどん弁当": "Chilled udon bento",
    "【関東】ピリ辛仕立ての冷しラー油ねぎそば": (
        "Chilled spicy chili-oil negi soba"
    ),
    "【関東・関西、中国・四国】鶏の旨みと白髪ねぎの香り 冷し鶏ねぎうどん": (
        "Chilled chicken and shredded-negi udon"
    ),
    "【関西】冷し肉ぶっかけうどん": "Chilled broth-poured meat udon",
    "ねぎ盛り！チャーシューの冷しまぜそば": (
        "Chilled maze-soba with extra negi and chashu"
    ),
    "大盛冷しぶっかけうどん": "Large chilled broth-poured udon",
    "お手軽！明太子パスタ": "Easy mentaiko pasta",
    "こしあんまん（ごま風味）": "Koshian bun with sesame",
    "シルバニアファミリー キラキラくじ～ほしぞらパジャマパーティ～": (
        "Sylvanian Families glitter lottery: starry pajama party"
    ),
    "麺屋極鶏 鶏だく だく郎": "Menya Gokukei extra-chicken Dakuro ramen",
    # Week of 2026-08-24 — 7-Eleven
    "あじとや監修 黒糖キーマチキンカレー": "Ajitoya brown-sugar keema chicken curry",
    "おおきなおむすび チャーシューわさび": "Large rice ball with chashu and wasabi",
    "焼肉＆唐揚げごはん": "Yakiniku and karaage rice",
    "ROLLサンド バジルチキンとトマト": "ROLL sandwich with basil chicken and tomato",
}


def is_obviously_generic_product_title(name: str) -> bool:
    t = sanitize_english_output(name).strip().lower()
    if not t:
        return True
    if _GENERIC_TITLE_BODY_RE.fullmatch(t):
        return True
    if _GENERIC_TITLE_WITH_NUMBER_RE.fullmatch(t):
        return True
    return False


def cap_english_product_title(text: str, max_len: int = MAX_PRODUCT_TITLE_CHARS) -> str:
    t = sanitize_english_output(text)
    if len(t) <= max_len:
        return t
    cut = t[:max_len].rsplit(" ", 1)[0].strip()
    if len(cut) < 12:
        cut = t[:max_len].strip()
    return cut + "…"


def enrich_generic_product_title(product: dict[str, Any]) -> None:
    """Promote vague English names using JP title/category when glossary leaves only a category word."""
    name = product.get("name") or ""
    name_ja = (product.get("nameJa") or "").strip()
    if not is_obviously_generic_product_title(name):
        return
    if len(name_ja) < 4:
        return

    candidate = sanitize_english_output(translate_japanese_text(name_ja))
    if not candidate or candidate.lower() == name.lower():
        candidate = ""

    if not candidate or is_obviously_generic_product_title(candidate):
        cat_ja = (product.get("categoryJa") or "").strip()
        if cat_ja and cat_ja.replace(" ", "") != name_ja.replace(" ", ""):
            alt = sanitize_english_output(translate_japanese_text(cat_ja))
            if alt and not is_obviously_generic_product_title(alt):
                candidate = alt

    if not candidate or is_obviously_generic_product_title(candidate):
        return

    product["name"] = cap_english_product_title(candidate)


def infer_english_context(product: dict[str, Any]) -> None:
    name_ja = (product.get("nameJa") or "").strip()
    curated_title = PRODUCT_SPECIFIC_TITLES.get(name_ja)
    if curated_title:
        product["name"] = curated_title
    curated = PRODUCT_SPECIFIC_NOTES.get(name_ja)
    if curated:
        product["englishContext"] = curated
        return

    if "deal" in product.get("tags", []):
        product["englishContext"] = sanitize_english_output(product.get("englishContext", ""))
        return

    hints: list[str] = []
    if "ぶっかけうどん" in name_ja:
        hints.append(
            "Chilled udon served with savory broth poured over the noodles."
        )
    elif "ぶっかけ" in name_ja:
        hints.append(
            "Chilled noodles served with savory broth poured over."
        )
    if re.search(r"焼きそば|焼そば|ヤキソバ", name_ja):
        hints.append(
            "Yakisoba is a savory fried wheat-noodle dish, not buckwheat soba."
        )
    if "増量" in name_ja:
        hints.append("This is a bonus-size promotion sold at the regular listed price.")
    product["englishContext"] = "; ".join(dict.fromkeys(hints))


def finalize_product_copy(product: dict[str, Any]) -> None:
    for key in ("name", "category"):
        if product.get(key):
            product[key] = sanitize_english_output(product[key])
    enrich_generic_product_title(product)
    if product.get("name"):
        product["name"] = sanitize_english_output(product["name"])
    if product.get("category"):
        product["category"] = sanitize_english_output(product["category"])
    if product.get("englishContext"):
        product["englishContext"] = sanitize_english_output(product["englishContext"])
    infer_english_context(product)
    product["englishContext"] = sanitize_english_output(product.get("englishContext", ""))
    for signal in product.get("localSignals", []):
        for key in ("matchedText", "snippet"):
            if signal.get(key):
                signal[key] = sanitize_english_output(signal[key])
    summarize_product(product)
    product["summary"] = sanitize_english_output(product["summary"])


def english_source_name(name: str) -> str:
    return SOURCE_NAME_TRANSLATIONS.get(name, translate_japanese_text(name, "source"))


def decode_html(raw_path: pathlib.Path) -> str:
    data = raw_path.read_bytes()
    for encoding in ("utf-8", "cp932", "euc-jp"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def parse_source(raw_path: pathlib.Path) -> SourceParser:
    parser = SourceParser()
    parser.feed(decode_html(raw_path))
    return parser


def absolute_url(url: str, source_url: str) -> str:
    if url.startswith("http"):
        return url
    if url.startswith("//"):
        return f"https:{url}"
    origin = re.match(r"^(https?://[^/]+)", source_url)
    if not origin:
        return url
    if url.startswith("/"):
        return f"{origin.group(1)}{url}"
    return f"{source_url.rstrip('/')}/{url}"


def parse_japanese_date(text: str, fallback_year: int | None = None) -> str | None:
    match = re.search(r"(?:(\d{4})年)?\s*(\d{1,2})月\s*(\d{1,2})日", text)
    if not match:
        return None
    year = int(match.group(1) or fallback_year or dt.date.today().year)
    month = int(match.group(2))
    day = int(match.group(3))
    try:
        return dt.date(year, month, day).isoformat()
    except ValueError:
        return None


def parse_lawson_list_date(text: str, fallback_year: int | None = None) -> str | None:
    t = clean_text(text)
    dot = re.fullmatch(r"(\d{4})\.(\d{1,2})\.(\d{1,2})", t)
    if dot:
        year, month, day = int(dot.group(1)), int(dot.group(2)), int(dot.group(3))
        try:
            return dt.date(year, month, day).isoformat()
        except ValueError:
            return None
    return parse_japanese_date(t, fallback_year)


def extract_familymart_new_list_rows(html: str) -> list[tuple[str, str, str, str, str]]:
    """FamilyMart weekly cards: category, title, price, and region notes are separate nodes."""
    rows: list[tuple[str, str, str, str, str]] = []
    for match in FAMILYMART_NEW_CARD_RE.finditer(html or ""):
        href, block, notes = match.group(1), match.group(2), match.group(3) or ""
        cate_match = re.search(r'ly-mod-infoset3-cate">([^<]+)', block, flags=re.IGNORECASE)
        ttl_match = re.search(r'ly-mod-infoset3-ttl">([^<]+)', block, flags=re.IGNORECASE)
        txt_match = re.search(r'ly-mod-infoset3-txt">\s*([\s\S]*?)\s*</p>', block, flags=re.IGNORECASE)
        if not ttl_match:
            continue
        rows.append(
            (
                href,
                clean_text(unescape(cate_match.group(1))) if cate_match else "",
                clean_text(unescape(ttl_match.group(1))),
                clean_text(unescape(txt_match.group(1))) if txt_match else "",
                clean_text(unescape(re.sub(r"<[^>]+>", " ", notes))),
            )
        )
    return rows


def extract_lawson_new_list_rows(html: str) -> list[tuple[str, str, str, str | None]]:
    """Lawson weekly new list: title from p.ttl, price/date from card HTML (not anchor text noise)."""
    rows: list[tuple[str, str, str, str | None]] = []
    for match in LAWSON_NEW_CARD_RE.finditer(html or ""):
        href_rel, block = match.group(1), match.group(2)
        ttl_match = re.search(r'<p[^>]*class=(["\'])ttl\1[^>]*>([^<]*)</p>', block, flags=re.IGNORECASE)
        if not ttl_match:
            continue
        raw_title = ttl_match.group(2)
        price_match = re.search(
            r'<p[^>]*class=(["\'])price\1[^>]*>\s*<span>([0-9,]+)</span>\s*<span>円',
            block,
            flags=re.IGNORECASE | re.DOTALL,
        )
        price_digits = price_match.group(2) if price_match else ""
        date_match = re.search(r'発売日\s*<span>([^<]+)</span>', block, flags=re.IGNORECASE)
        date_raw = date_match.group(1).strip() if date_match else None
        rows.append((href_rel, raw_title, price_digits, date_raw))
    return rows


def parse_price(texts: list[str]) -> str:
    for text in texts:
        if "円" in text and re.search(r"\d", text):
            return clean_text(text)
    return ""


def parse_regions(texts: list[str], fallback: str = "") -> list[str]:
    for text in texts:
        if "販売地域" in text or "発売地域" in text:
            region_text = re.sub(r"^(販売地域|発売地域)：?", "", text).strip()
            return [part.strip() for part in re.split(r"[、,]", region_text) if part.strip()]
    return [fallback] if fallback else []


def week_start_from_familymart(events: list[dict[str, str]], today: dt.date) -> str | None:
    for event in events:
        text = event.get("text", "")
        match = re.search(r"今週の新商品\s*\((\d{1,2})/(\d{1,2})", text)
        if match:
            try:
                return dt.date(today.year, int(match.group(1)), int(match.group(2))).isoformat()
            except ValueError:
                return None
    return None


def item_id(chain: str, name: str, release_date: str | None) -> str:
    base = f"{chain}|{name}|{release_date or ''}"
    digest = hashlib.sha1(base.encode("utf-8")).hexdigest()[:10]
    slug = re.sub(r"[^a-z0-9]+", "-", chain.lower()).strip("-")
    return f"{slug}-{digest}"


def new_product(chain: str, name: str, source: dict[str, Any], source_url: str) -> dict[str, Any]:
    return {
        "id": "",
        "chain": chain,
        "name": translate_japanese_text(name),
        "nameJa": name,
        "category": "",
        "categoryJa": "",
        "priceText": "",
        "priceTextJa": "",
        "releaseDate": None,
        "regions": [],
        "regionsJa": [],
        "sourceUrls": [source_url],
        "sourceTiers": [source["tier"]],
        "imageUrl": "",
        "tags": ["new"],
        "timeGate": None,
        "score": 0,
        "scoreReasons": [],
        "summary": "",
        "englishContext": "",
        "localSignals": [],
    }


def parse_seven(events: list[dict[str, str]], source: dict[str, Any], today: dt.date) -> tuple[list[dict[str, Any]], list[str]]:
    products: list[dict[str, Any]] = []
    warnings: list[str] = []
    current_region = ""
    for index, event in enumerate(events):
        text = event.get("text", "")
        if event["type"] == "heading" and text in REGION_NAMES:
            current_region = text
            continue
        if event["type"] != "link" or "/products/a/item/" not in event.get("href", ""):
            continue
        if "ラインナップを見る" in text:
            continue

        following: list[str] = []
        for next_event in events[index + 1 : index + 10]:
            if next_event["type"] == "link" and "/products/a/item/" in next_event.get("href", ""):
                break
            following.append(next_event.get("text", ""))

        product = new_product("7-Eleven", text, source, absolute_url(event["href"], source["url"]))
        product["priceTextJa"] = parse_price(following)
        product["priceText"] = translate_price(product["priceTextJa"])
        product["releaseDate"] = next((parse_japanese_date(piece, today.year) for piece in following if parse_japanese_date(piece, today.year)), None)
        product["regionsJa"] = parse_regions(following, current_region)
        product["regions"] = translate_regions(product["regionsJa"])
        products.append(product)

    if not products:
        warnings.append("No 7-Eleven products parsed from official source.")
    return products, warnings


def parse_familymart(
    html: str, events: list[dict[str, str]], source: dict[str, Any], today: dt.date
) -> tuple[list[dict[str, Any]], list[str]]:
    products: list[dict[str, Any]] = []
    warnings: list[str] = []
    week_start = week_start_from_familymart(events, today)
    card_rows = extract_familymart_new_list_rows(html)
    if card_rows:
        for href, category_ja, name, price_text_ja, notes_text in card_rows:
            if len(name) < 2:
                continue
            product = new_product("FamilyMart", name, source, href)
            if category_ja:
                product["categoryJa"] = category_ja
                product["category"] = translate_category(category_ja)
            if price_text_ja:
                product["priceTextJa"] = price_text_ja
                product["priceText"] = translate_price(price_text_ja)
            product["releaseDate"] = week_start
            product["regionsJa"] = parse_regions([notes_text])
            product["regions"] = translate_regions(product["regionsJa"])
            products.append(product)
        if products:
            return products, warnings

    ignored_headings = {"今週のおすすめ情報", "セール商品・価格について", "商品情報"}

    for index, event in enumerate(events):
        if event["type"] != "heading" or event.get("tag") != "h3":
            continue
        name = event["text"]
        if name in ignored_headings or len(name) < 2:
            continue

        following = events[index + 1 : index + 10]
        link_event = next((item for item in following if item["type"] == "link" and "/goods/" in item.get("href", "")), None)
        if not link_event:
            continue

        text_pieces = [item.get("text", "") for item in following]
        category_price = link_event["text"]
        product = new_product("FamilyMart", name, source, absolute_url(link_event["href"], source["url"]))
        price_match = re.search(r"(.+?)\s+(\d[\d,]*円.*)", category_price)
        if price_match:
            product["categoryJa"] = clean_text(price_match.group(1))
            product["category"] = translate_category(product["categoryJa"])
            product["priceTextJa"] = clean_text(price_match.group(2))
            product["priceText"] = translate_price(product["priceTextJa"])
        else:
            product["categoryJa"] = category_price
            product["category"] = translate_category(category_price)
        product["releaseDate"] = week_start
        product["regionsJa"] = parse_regions(text_pieces)
        product["regions"] = translate_regions(product["regionsJa"])
        products.append(product)

    if not products:
        warnings.append("No FamilyMart products parsed from official source.")
    return products, warnings


def parse_lawson(
    html: str, events: list[dict[str, str]], source: dict[str, Any], today: dt.date
) -> tuple[list[dict[str, Any]], list[str]]:
    products: list[dict[str, Any]] = []
    warnings: list[str] = []
    release_date = None
    for event in events[:20]:
        release_date = parse_japanese_date(event.get("text", ""), today.year)
        if release_date:
            break

    seen_names: set[str] = set()
    card_rows = extract_lawson_new_list_rows(html)
    if card_rows:
        for href_rel, raw_title, price_digits, date_raw in card_rows:
            name = normalize_lawson_product_name(unescape(raw_title))
            if is_weak_lawson_title(name):
                continue
            if len(name) < 3 or name in seen_names or "ローソン" in name:
                continue
            product = new_product("Lawson", name, source, absolute_url(href_rel, source["url"]))
            if price_digits:
                product["priceTextJa"] = f"{price_digits}円(税込)"
                product["priceText"] = translate_price(product["priceTextJa"])
            parsed_d = parse_lawson_list_date(date_raw, today.year) if date_raw else None
            product["releaseDate"] = parsed_d or release_date
            product["regionsJa"] = parse_regions([], "全国")
            product["regions"] = translate_regions(product["regionsJa"])
            products.append(product)
            seen_names.add(name)
        if products:
            return products[:80], warnings

    for index, event in enumerate(events):
        if event["type"] != "link":
            continue
        href = event.get("href", "")
        name = normalize_lawson_product_name(event["text"])
        if is_lawson_disclaimer_text(event["text"]) or is_weak_lawson_title(name):
            continue
        if "/recommend/original/detail/" not in href and "/recommend/new/detail/" not in href:
            continue
        if len(name) < 3 or name in seen_names or "ローソン" in name:
            continue

        following = [item.get("text", "") for item in events[index + 1 : index + 8]]
        product = new_product("Lawson", name, source, absolute_url(href, source["url"]))
        product["priceTextJa"] = parse_price(following)
        product["priceText"] = translate_price(product["priceTextJa"])
        product["releaseDate"] = next(
            (parse_japanese_date(piece, today.year) for piece in following if parse_japanese_date(piece, today.year)),
            release_date,
        )
        product["regionsJa"] = parse_regions(following, "全国")
        product["regions"] = translate_regions(product["regionsJa"])
        products.append(product)
        seen_names.add(name)

    if not products:
        warnings.append("No Lawson products parsed from official source; page may require parser tuning.")
    return products[:80], warnings


def _parse_lawson_lab_events_legacy(
    events: list[dict[str, str]], source: dict[str, Any], today: dt.date
) -> tuple[list[dict[str, Any]], list[str]]:
    """Previous event-stream parser, kept as fallback if the article HTML layout changes."""
    products: list[dict[str, Any]] = []
    for index, event in enumerate(events):
        text = event.get("text", "")
        if is_lawson_disclaimer_text(text):
            continue
        match = re.search(
            r"(.{3,80}?)\s+(20\d{2}年\d{1,2}月\d{1,2}日[^ ]{0,12})\s*発売[！!]?\s*ローソン標準価格\s*([0-9,]+円\(税込\))",
            text,
        )
        if match:
            name = clean_text(match.group(1))
            date_text = match.group(2)
            price_text = match.group(3)
        else:
            if event.get("type") == "heading":
                continue
            lookahead = [item.get("text", "") for item in events[index + 1 : index + 5]]
            date_text = next((piece for piece in lookahead if "発売" in piece and parse_japanese_date(piece, today.year)), "")
            price_text = next((piece for piece in lookahead if "ローソン標準価格" in piece and "円" in piece), "")
            name = text
            if not date_text or not price_text:
                continue

        name = re.split(r"[。！？]", clean_text(name))[-1].strip()
        name = normalize_lawson_product_name(name)
        if is_weak_lawson_title(name):
            continue
        if len(name) < 3 or any(skip in name for skip in ("ローソン研究所", "新商品", "おすすめ", "商品・おトク情報")):
            continue
        product = new_product("Lawson", name, source, source["url"])
        product["releaseDate"] = parse_japanese_date(date_text, today.year)
        product["priceTextJa"] = clean_text(price_text.replace("ローソン標準価格", "").strip())
        product["priceText"] = translate_price(product["priceTextJa"])
        product["regionsJa"] = ["全国"]
        product["regions"] = ["Nationwide"]
        product["sourceTiers"] = [source["tier"], "featured"]
        products.append(product)

    return products, []


def parse_lawson_lab(
    html: str, events: list[dict[str, str]], source: dict[str, Any], today: dt.date
) -> tuple[list[dict[str, Any]], list[str]]:
    products: list[dict[str, Any]] = []
    warnings: list[str] = []
    seen_keys: set[str] = set()
    rows = extract_lawson_lab_product_rows(html)
    for name_ja, date_text, price_text in rows:
        if is_weak_lawson_title(name_ja):
            continue
        dedupe = f"{name_ja}|{date_text}|{price_text}"
        if dedupe in seen_keys:
            continue
        seen_keys.add(dedupe)
        product = new_product("Lawson", name_ja, source, source["url"])
        product["releaseDate"] = parse_japanese_date(date_text, today.year)
        product["priceTextJa"] = clean_text(price_text)
        product["priceText"] = translate_price(product["priceTextJa"])
        product["regionsJa"] = ["全国"]
        product["regions"] = ["Nationwide"]
        product["sourceTiers"] = [source["tier"], "featured"]
        products.append(product)

    if not products:
        warnings.append("Lawson Lab: no HTML product blocks matched; trying legacy event parse.")
        legacy_products, _legacy_warnings = _parse_lawson_lab_events_legacy(events, source, today)
        products.extend(legacy_products)
    if not products:
        og = extract_og_title(html)
        if og:
            warnings.append(f"No Lawson Lab rows; og:title is “{og[:120]}”.")
        warnings.append("No Lawson Lab products parsed from weekly article.")
    return products, warnings


def visible_text(parser: SourceParser) -> str:
    pieces = [parser.title]
    pieces.extend(event.get("text", "") for event in parser.events)
    return clean_text(" ".join(piece for piece in pieces if piece))


def setusoku_offer_window(text: str, today: dt.date) -> tuple[str | None, str | None]:
    explicit = re.search(r"(\d{1,2}/\d{1,2})\s*[～〜~-]\s*(\d{1,2}/\d{1,2})", text)
    if explicit:
        start_month, start_day = (int(part) for part in explicit.group(1).split("/"))
        end_month, end_day = (int(part) for part in explicit.group(2).split("/"))
        try:
            return (
                dt.date(today.year, start_month, start_day).isoformat(),
                dt.date(today.year, end_month, end_day).isoformat(),
            )
        except ValueError:
            return None, None

    end_only = re.search(r"[～〜~-]\s*(\d{1,2})/(\d{1,2})", text)
    if end_only:
        try:
            return None, dt.date(today.year, int(end_only.group(1)), int(end_only.group(2))).isoformat()
        except ValueError:
            return None, None
    return None, None


def setusoku_offer_name(offer: str) -> str:
    text = clean_text(offer.lstrip("・-● "))
    text = re.sub(r"。?\s*(?:\d{1,2}/\d{1,2}\s*)?[～〜~-]\s*\d{1,2}/\d{1,2}。?$", "", text).strip()
    return f"プライチキャンペーン: {text}"


def parse_setusoku_bogo_context(
    events: list[dict[str, str]], source: dict[str, Any], today: dt.date
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    """Extract only the chain-scoped BOGO offer bullets from Setusoku's broad sale page."""
    offers_by_chain: dict[str, list[dict[str, Any]]] = {}
    current_chain = ""
    for event in events:
        text = clean_text(event.get("text", "")).strip("：:；;")
        if not text:
            continue
        if event.get("type") == "heading":
            normalized = text.replace(" ", "")
            current_chain = SETUSOKU_CHAIN_HEADINGS.get(normalized, "")
            continue
        if not current_chain:
            continue
        if "買うと" not in text or "無料" not in text:
            continue
        if event.get("type") != "text" or not text.startswith("・"):
            continue
        offer = clean_text(text.lstrip("・-● "))
        if len(offer) < 8:
            continue
        start_date, end_date = setusoku_offer_window(offer, today)
        offers_by_chain.setdefault(current_chain, []).append(
            {
                "chain": current_chain,
                "text": offer,
                "nameJa": setusoku_offer_name(offer),
                "releaseDate": start_date,
                "endDate": end_date,
                "source": source,
            }
        )

    context_entries: list[dict[str, Any]] = []
    offer_entries: list[dict[str, Any]] = []
    for chain, offers in offers_by_chain.items():
        aliases = " ".join(CHAIN_NAMES.get(chain, [chain]))
        offer_texts = [offer["text"] for offer in offers]
        offer_entries.extend(offers)
        context_entries.append(
            {
                "id": source["id"],
                "name": source["name"],
                "tier": source["tier"],
                "language": source.get("language", "ja"),
                "url": source["url"],
                "chain": chain,
                "dealTag": "bogo",
                "dealLabel": "buy-one-get-one/free-item offer",
                "text": clean_text(f"{chain} {aliases} " + " ".join(offer_texts)),
            }
        )

    warnings = []
    if not context_entries:
        warnings.append("Setusoku BOGO source fetched but no chain-scoped offer bullets matched.")
    return context_entries, offer_entries, warnings


def tag_product(product: dict[str, Any], _keyword_contexts: dict[str, str]) -> None:
    text = f"{product['nameJa']} {product.get('categoryJa', '')} {' '.join(product.get('regionsJa', []))}"
    tags = set(product.get("tags", []))
    if any(token in text for token in ("コラボ", "×", "監修", "GODIVA", "ゴディバ", "mofusand", "森半", "八天堂", "ICHIBIKO")):
        tags.add("collab")
    if any(token in text for token in ("限定", "数量限定", "期間限定")):
        tags.add("limited")
    if any(token in text for token in ("抹茶", "いちご", "苺", "桃", "マンゴー", "桜", "春", "夏", "ほうじ茶", "冷し", "氷")):
        tags.add("seasonal")
    if any(token in text for token in ("復刻", "再販売")):
        tags.add("returning")
    if any(token in text for token in ("リニューアル", "刷新")):
        tags.add("renewal")
    if any(token in text for token in ("一番くじ", "ソックス", "ウエハース", "玩具", "グッズ", "イタジャガ", "わっふれーむ")):
        tags.add("merch")
    if product.get("regionsJa") and "全国" not in product["regionsJa"]:
        tags.add("regional")
    for signal in product.get("localSignals", []):
        if signal.get("dealTag"):
            tags.add(signal["dealTag"])

    if any(signal.get("dealTag") == "bogo" for signal in product.get("localSignals", [])):
        product["englishContext"] = "Matched to a current buy-one-get-one campaign listing."
    if "deal" in tags and "bogo" in tags:
        product["englishContext"] = "A campaign offer rather than a standalone new-product listing."
    product["tags"] = sorted(tags)


def add_local_signals(products: list[dict[str, Any]], context_sources: list[dict[str, Any]]) -> None:
    for product in products:
        product_name = product["nameJa"]
        chain_aliases = CHAIN_NAMES.get(product["chain"], [])
        candidates = [product_name]
        if len(product_name) > 8:
            candidates.extend(re.split(r"[ 　（）()【】]", product_name)[:2])
        candidates = [candidate for candidate in candidates if len(candidate) >= 4]

        for source in context_sources:
            body = source["text"]
            if not any(alias in body for alias in chain_aliases):
                continue
            matched = next((candidate for candidate in candidates if candidate and candidate in body), "")
            if not matched:
                continue
            position = body.find(matched)
            snippet = clean_text(body[max(0, position - 60) : position + 120])
            product["localSignals"].append(
                signal := {
                    "sourceId": source["id"],
                    "sourceName": english_source_name(source["name"]),
                    "tier": source["tier"],
                    "language": source.get("language", "ja"),
                    "url": source["url"],
                    "matchedText": translate_japanese_text(matched),
                    "matchedTextJa": matched,
                    "snippet": translate_japanese_text(snippet, "local source mention"),
                    "snippetJa": snippet,
                }
            )
            if source.get("dealTag"):
                signal["dealTag"] = source["dealTag"]
                signal["dealLabel"] = source.get("dealLabel", "")


def official_product_matches_offer(product: dict[str, Any], offer: dict[str, Any]) -> bool:
    if product["chain"] != offer["chain"]:
        return False
    product_name = product["nameJa"]
    candidates = [product_name]
    if len(product_name) > 8:
        candidates.extend(re.split(r"[ 　（）()【】]", product_name)[:2])
    candidates = [candidate for candidate in candidates if len(candidate) >= 4]
    return any(candidate in offer["text"] for candidate in candidates)


def deal_product_from_setusoku_offer(offer: dict[str, Any]) -> dict[str, Any]:
    source = offer["source"]
    product = new_product(offer["chain"], offer["nameJa"], source, source["url"])
    product["category"] = "Deal"
    product["categoryJa"] = "キャンペーン"
    product["releaseDate"] = offer.get("releaseDate")
    product["sourceTiers"] = [source["tier"], "deal"]
    product["tags"] = ["bogo", "deal", "new"]
    product["englishContext"] = "buy-one-get-one/free-item campaign listed by Setusoku; exact SKU detail may be broad"
    if offer.get("endDate"):
        product["timeGate"] = {"type": "deal", "label": f"Deal through {offer['endDate']}"}
    product["localSignals"] = [
        {
            "sourceId": source["id"],
            "sourceName": english_source_name(source["name"]),
            "tier": source["tier"],
            "language": source.get("language", "ja"),
            "url": source["url"],
            "matchedText": "BOGO campaign",
            "matchedTextJa": "プライチキャンペーン",
            "snippet": translate_japanese_text(offer["text"], "BOGO campaign"),
            "snippetJa": offer["text"],
            "dealTag": "bogo",
            "dealLabel": "buy-one-get-one/free-item offer",
        }
    ]
    return product


def create_unmatched_setusoku_deal_products(
    products: list[dict[str, Any]], offers: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    deal_products = []
    seen: set[tuple[str, str]] = set()
    for offer in offers:
        key = (offer["chain"], offer["text"])
        if key in seen:
            continue
        seen.add(key)
        if any(official_product_matches_offer(product, offer) for product in products):
            continue
        deal_products.append(deal_product_from_setusoku_offer(offer))
    return deal_products


def score_product(product: dict[str, Any], today: dt.date) -> None:
    is_deal_item = "deal" in product.get("tags", [])
    score = 30 if is_deal_item else 35
    reasons: list[str] = ["Setusoku campaign listing"] if is_deal_item else ["official product listing"]
    release_date = None
    if product.get("releaseDate"):
        try:
            release_date = dt.date.fromisoformat(product["releaseDate"])
        except ValueError:
            release_date = None

    if release_date:
        age = (today - release_date).days
        if age <= 2:
            score += 25
            reasons.append("released in the last few days")
        elif age <= 7:
            score += 18
            reasons.append("released this week")
        elif age < 0:
            score += 15
            reasons.append("upcoming release")
    for tag, points, reason in (
        ("collab", 15, "collaboration or supervised item"),
        ("limited", 14, "limited/time-gated language"),
        ("seasonal", 8, "seasonal flavor or format"),
        ("regional", 5, "regional availability makes it harder to find"),
        ("merch", 5, "character goods or merch-adjacent item"),
        ("returning", 4, "returning item"),
        ("bogo", 10, "matched buy-one-get-one/free-item campaign source"),
        ("deal", 5, "deal/campaign item"),
    ):
        if tag in product["tags"]:
            score += points
            reasons.append(reason)

    if product["localSignals"]:
        score += min(12, 4 * len(product["localSignals"]))
        reasons.append("mentioned by Japanese local/context source")

    if product.get("regionsJa") == ["全国"]:
        score += 4
        reasons.append("national availability")

    product["score"] = min(score, 100)
    product["scoreReasons"] = reasons[:6]
    if "limited" in product["tags"]:
        product["timeGate"] = {"type": "limited", "label": "Limited or short-window release"}
    elif "deal" in product["tags"]:
        product["timeGate"] = product.get("timeGate") or {"type": "deal", "label": "Deal/campaign item"}
    elif "regional" in product["tags"]:
        product["timeGate"] = {"type": "regional", "label": "Regional availability"}
    else:
        product["timeGate"] = None


def extract_familymart_thumb_map(html: str) -> dict[str, str]:
    base = "https://www.family.co.jp"
    mapping: dict[str, str] = {}
    if not html:
        return mapping
    pattern = re.compile(
        r'<a\s+href="(https://www\.family\.co\.jp/goods/[^"]+\.html)"[^>]*>[\s\S]{0,2600}?<img[^>]+src="([^"]+)"',
        re.IGNORECASE,
    )
    for match in pattern.finditer(html):
        href, src = match.group(1), match.group(2)
        key = url_canonical(href)
        mapping.setdefault(key, absolute_url(src, base))
    return mapping


def extract_seven_thumb_map(html: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    if not html:
        return mapping
    base = "https://www.sej.co.jp"
    pattern = re.compile(
        r'<figure>\s*<a\s+href="(/products/a/item/[^"]+)">\s*<img\b[^>]*>',
        re.IGNORECASE,
    )
    for match in pattern.finditer(html):
        href_rel = match.group(1)
        block_end = html.find("</figure>", match.start())
        snippet = html[match.start() : block_end + 9] if block_end != -1 else match.group(0)
        img_match = re.search(r'data-original="([^"]+)"', snippet) or re.search(r'\bsrc="([^"]+)"', snippet)
        if not img_match:
            continue
        thumb = img_match.group(1).strip()
        if thumb.startswith("//"):
            thumb = f"https:{thumb}"
        elif thumb.startswith("/"):
            thumb = absolute_url(thumb, base)
        full_item_url = url_canonical(absolute_url(href_rel, base))
        mapping.setdefault(full_item_url, thumb)
    return mapping


def url_canonical(url: str) -> str:
    return url.split("#")[0].rstrip("/")


def enrich_product_thumbnails(products: list[dict[str, Any]], seven_html: str, family_html: str) -> None:
    fm_map = extract_familymart_thumb_map(family_html)
    sj_map = extract_seven_thumb_map(seven_html)
    for product in products:
        urls = product.get("sourceUrls", [])
        if product["chain"] == "FamilyMart":
            detail = next((url for url in urls if "family.co.jp/goods/" in url), "")
            thumb = fm_map.get(url_canonical(detail), "")
            if thumb:
                product["imageUrl"] = thumb
        elif product["chain"] == "7-Eleven":
            detail = next((url for url in urls if "sej.co.jp/products/a/item/" in url), "")
            thumb = sj_map.get(url_canonical(detail), "")
            if thumb:
                product["imageUrl"] = thumb


def enrich_lawson_from_detail_snapshots(products: list[dict[str, Any]], snapshots: list[dict[str, Any]]) -> None:
    """Fill Lawson imageUrl (and longer Japanese titles when present) from fetched detail HTML."""
    if not snapshots:
        return
    detail_map: dict[str, dict[str, str]] = {}
    for snap in snapshots:
        if not snap.get("ok"):
            continue
        rel = snap.get("rawPath") or ""
        path = ROOT / rel
        if not path.is_file():
            continue
        html = decode_html(path)
        key = url_canonical(snap.get("url", ""))
        if not key:
            continue
        detail_map[key] = {
            "thumb": lawson_detail_thumbnail_from_html(html),
            "nameJaDetail": extract_lawson_detail_h2_title(html),
        }

    for product in products:
        if product["chain"] != "Lawson":
            continue
        for src_url in product.get("sourceUrls", []):
            if "/recommend/" not in src_url or "/detail/" not in src_url:
                continue
            meta = detail_map.get(url_canonical(src_url))
            if not meta:
                continue
            if meta.get("thumb") and not (product.get("imageUrl") or "").strip():
                product["imageUrl"] = meta["thumb"]
            detail_name = meta.get("nameJaDetail") or ""
            if detail_name:
                current = normalize_lawson_product_name(product.get("nameJa") or "")
                if len(detail_name) > len(current) + 2:
                    product["nameJa"] = detail_name
                    product["name"] = translate_japanese_text(detail_name)


def assign_product_ids(products: list[dict[str, Any]]) -> None:
    for product in products:
        product["id"] = item_id(product["chain"], product["nameJa"], product.get("releaseDate"))


def summarize_product(product: dict[str, Any]) -> None:
    pieces = [product["chain"]]
    if product.get("category"):
        pieces.append(product["category"])
    if product.get("priceText"):
        pieces.append(product["priceText"])
    if product.get("regions"):
        pieces.append(f"Regions: {', '.join(product['regions'][:4])}")
    product["summary"] = " · ".join(pieces)


def merge_products(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[tuple[str, str, str | None], dict[str, Any]] = {}
    for product in products:
        key = (product["chain"], product["nameJa"], product.get("releaseDate"))
        if key not in merged:
            merged[key] = product
            continue
        existing = merged[key]
        existing["regions"] = sorted(set(existing.get("regions", [])) | set(product.get("regions", [])))
        existing["sourceUrls"] = sorted(set(existing["sourceUrls"]) | set(product["sourceUrls"]))
        existing["sourceTiers"] = sorted(set(existing["sourceTiers"]) | set(product["sourceTiers"]))
        if not existing.get("priceText") and product.get("priceText"):
            existing["priceText"] = product["priceText"]
        if not existing.get("priceTextJa") and product.get("priceTextJa"):
            existing["priceTextJa"] = product["priceTextJa"]
        if not existing.get("category") and product.get("category"):
            existing["category"] = product["category"]
        if not existing.get("categoryJa") and product.get("categoryJa"):
            existing["categoryJa"] = product["categoryJa"]
        if not existing.get("imageUrl") and product.get("imageUrl"):
            existing["imageUrl"] = product["imageUrl"]
    for product in merged.values():
        product["id"] = item_id(product["chain"], product["nameJa"], product.get("releaseDate"))
    return list(merged.values())


def build_intro(products: list[dict[str, Any]], week_label: str) -> str:
    top = products[:5]
    if not top:
        return f"{week_label}: no products were parsed from the configured sources."
    chain_leaders: list[dict[str, Any]] = []
    for chain in ("7-Eleven", "FamilyMart", "Lawson"):
        leader = next((product for product in products if product["chain"] == chain), None)
        if leader:
            chain_leaders.append(leader)
    leaders_for_intro = chain_leaders or top[:3]
    chains = sorted({product["chain"] for product in leaders_for_intro})
    themes = []
    for tag in ("collab", "limited", "seasonal", "regional", "merch"):
        if any(tag in product["tags"] for product in top):
            themes.append(tag)
    leaders = ", ".join(f"{product['chain']} {product['name']}" for product in leaders_for_intro[:4])
    theme_text = f" Themes: {', '.join(themes)}." if themes else ""
    return f"{week_label}: the board is led by {leaders}. Coverage spans {', '.join(chains)}.{theme_text} Check limited and regional badges before planning a store run."


def latest_draft_dir(draft_root: pathlib.Path) -> pathlib.Path:
    candidates = [path for path in draft_root.iterdir() if path.is_dir()]
    if not candidates:
        raise SystemExit(f"No draft folders found under {draft_root}")
    return sorted(candidates)[-1]


def int_config_value(value: Any, *, field_name: str, source_id: str = "") -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as error:
        label = f"{source_id} {field_name}".strip()
        raise SystemExit(f"Invalid sanity config for {label}: expected integer, got {value!r}") from error
    if parsed < 0:
        label = f"{source_id} {field_name}".strip()
        raise SystemExit(f"Invalid sanity config for {label}: expected non-negative integer, got {parsed}")
    return parsed


def format_source_sanity_failure(summary: dict[str, Any], min_products: int) -> str:
    return (
        f"Required source {summary['id']} parsed {summary.get('productCount', 0)} products "
        f"(minimum {min_products}). "
        f"parser={summary.get('parser')}; ok={summary.get('ok')}; status={summary.get('status')}; "
        f"bytes={summary.get('bytes')}; resolvedUrl={summary.get('resolvedUrl')}. "
        "Suggested action: inspect the fetched raw HTML and update the parser or source URL. "
        "Use --allow-empty-required-source or --skip-source-sanity only after manually verifying the source."
    )


def collect_source_sanity_failures(source_summaries: list[dict[str, Any]], source_by_id: dict[str, dict[str, Any]]) -> list[str]:
    failures: list[str] = []
    for summary in source_summaries:
        source = source_by_id[summary["id"]]
        sanity = source.get("sanity") or {}
        if not sanity.get("required") and "minProducts" not in sanity:
            continue
        if source.get("parser") not in PRODUCT_SOURCE_PARSERS:
            continue
        min_products = int_config_value(sanity.get("minProducts", 1), field_name="sanity.minProducts", source_id=source["id"])
        if int(summary.get("productCount", 0)) < min_products:
            failures.append(format_source_sanity_failure(summary, min_products))
    return failures


def collect_feed_sanity_failures(config: dict[str, Any], products: list[dict[str, Any]]) -> list[str]:
    sanity = config.get("feedSanity") or {}
    failures: list[str] = []
    if "minTotalProducts" in sanity:
        min_total = int_config_value(sanity["minTotalProducts"], field_name="feedSanity.minTotalProducts")
        if len(products) < min_total:
            failures.append(
                f"Generated feed has {len(products)} products (minimum {min_total}). "
                "Suggested action: inspect source sanity failures and fetched raw HTML before publishing."
            )
    chain_minimums = sanity.get("minChainProducts") or {}
    if chain_minimums:
        counts = Counter(product.get("chain") for product in products)
        for chain, raw_minimum in chain_minimums.items():
            min_count = int_config_value(raw_minimum, field_name=f"feedSanity.minChainProducts.{chain}")
            if counts.get(chain, 0) < min_count:
                failures.append(
                    f"Generated feed has {counts.get(chain, 0)} {chain} products (minimum {min_count}). "
                    "Suggested action: inspect that chain's official source parser and fetched raw HTML before publishing."
                )
    return failures


CONTENT_QUALITY_PRODUCT_FIELDS = ("name", "summary", "englishContext", "category")
CONTENT_QUALITY_SOURCE_FIELDS = ("title",)
CONTENT_QUALITY_BLOCKED_PATTERNS = [
    ("Region regional.Region regional", re.compile(r"\bregion\s+regional\s*\.\s*region\s+regional\b", re.I)),
    ("Region regional", re.compile(r"\bregion\s+regional\b", re.I)),
    ("regional regional", re.compile(r"\bregional\s+regional\b", re.I)),
]
CONTENT_QUALITY_REPEAT_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9'-]*", re.I)


def content_quality_excerpt(text: str, start: int = 0, end: int = 0, max_len: int = 120) -> str:
    value = clean_text(text)
    if not value:
        return ""
    if start or end:
        pad = 36
        left = max(0, start - pad)
        right = min(len(value), max(end + pad, start + max_len))
        excerpt = value[left:right].strip()
        if left:
            excerpt = f"...{excerpt}"
        if right < len(value):
            excerpt = f"{excerpt}..."
        return excerpt
    if len(value) <= max_len:
        return value
    return f"{value[: max_len - 3].rstrip()}..."


def format_product_content_quality_failure(
    product: dict[str, Any], index: int, field: str, reason: str, offending: str, text: str
) -> str:
    product_id = product.get("id") or "(missing id)"
    chain = product.get("chain") or "(unknown chain)"
    return (
        f"Content quality failure in product index {index} id={product_id} chain={chain} "
        f"field={field}: {reason}; offending={offending!r}; text={content_quality_excerpt(text)!r}."
    )


def format_source_content_quality_failure(summary: dict[str, Any], field: str, reason: str, offending: str, text: str) -> str:
    return (
        f"Content quality failure in source id={summary.get('id')} field={field}: "
        f"{reason}; offending={offending!r}; text={content_quality_excerpt(text)!r}."
    )


def collect_text_quality_issues(text: str) -> list[tuple[str, str]]:
    value = clean_text(text)
    if not value:
        return []
    issues: list[tuple[str, str]] = []
    for label, pattern in CONTENT_QUALITY_BLOCKED_PATTERNS:
        match = pattern.search(value)
        if match:
            issues.append((f"blocked phrase/pattern {label}", content_quality_excerpt(value, match.start(), match.end())))

    tokens = CONTENT_QUALITY_REPEAT_TOKEN_RE.findall(value.lower())
    for index in range(len(tokens) - 1):
        if tokens[index] == tokens[index + 1] and len(tokens[index]) >= 3:
            issues.append(("adjacent repeated word", " ".join(tokens[index : index + 2])))
            break

    for phrase_len in range(2, 5):
        for index in range(0, len(tokens) - (phrase_len * 2) + 1):
            first = tokens[index : index + phrase_len]
            second = tokens[index + phrase_len : index + (phrase_len * 2)]
            if first == second:
                phrase = " ".join(first)
                issues.append(("adjacent repeated short phrase", f"{phrase} {phrase}"))
                return issues

    sentence_fragments = [
        " ".join(CONTENT_QUALITY_REPEAT_TOKEN_RE.findall(fragment.lower()))
        for fragment in re.split(r"[.!?。！？]+", value)
    ]
    sentence_fragments = [fragment for fragment in sentence_fragments if len(fragment) >= 12 or len(fragment.split()) >= 2]
    fragment_counts = Counter(sentence_fragments)
    repeated_fragment = next((fragment for fragment, count in fragment_counts.items() if count >= 2), "")
    if repeated_fragment:
        issues.append(("repeated sentence fragment", repeated_fragment))

    shingle_counts: Counter[str] = Counter()
    for phrase_len in range(2, 5):
        for index in range(0, len(tokens) - phrase_len + 1):
            shingle = " ".join(tokens[index : index + phrase_len])
            shingle_counts[shingle] += 1
    repeated_shingle = next(
        (
            shingle
            for shingle, count in shingle_counts.items()
            if count >= 3 and re.search(r"\bregion(?:al)?\b", shingle, re.I)
        ),
        "",
    )
    if not repeated_shingle:
        repeated_shingle = next((shingle for shingle, count in shingle_counts.items() if count >= 4), "")
    if repeated_shingle:
        issues.append(("suspicious repeated phrase", repeated_shingle))

    return issues


def collect_content_quality_failures(
    products: list[dict[str, Any]], source_summaries: list[dict[str, Any]] | None = None
) -> list[str]:
    failures: list[str] = []
    for index, product in enumerate(products):
        if is_obviously_generic_product_title(product.get("name") or ""):
            failures.append(
                format_product_content_quality_failure(
                    product,
                    index,
                    "name",
                    "generic product name",
                    product.get("name") or "",
                    product.get("name") or "",
                )
            )
        for field in CONTENT_QUALITY_PRODUCT_FIELDS:
            text = product.get(field)
            if not isinstance(text, str) or not text:
                continue
            for reason, offending in collect_text_quality_issues(text):
                failures.append(format_product_content_quality_failure(product, index, field, reason, offending, text))

    for summary in source_summaries or []:
        for field in CONTENT_QUALITY_SOURCE_FIELDS:
            text = summary.get(field)
            if not isinstance(text, str) or not text:
                continue
            for reason, offending in collect_text_quality_issues(text):
                failures.append(format_source_content_quality_failure(summary, field, reason, offending, text))
    return failures


def format_major_three_counts(config: dict[str, Any], products: list[dict[str, Any]]) -> str:
    sanity = config.get("feedSanity") or {}
    chain_minimums = sanity.get("minChainProducts") or {}
    counts = Counter(product.get("chain") for product in products)
    pieces = []
    for chain in MAJOR_THREE_CHAINS:
        threshold = int_config_value(
            chain_minimums.get(chain, 0),
            field_name=f"feedSanity.minChainProducts.{chain}",
        )
        pieces.append(f"{chain} {counts.get(chain, 0)}/{threshold}")
    total_threshold = int_config_value(sanity.get("minTotalProducts", 0), field_name="feedSanity.minTotalProducts")
    return f"Major-three counts/thresholds: {', '.join(pieces)}; total {len(products)}/{total_threshold}."


def fail_sanity(failures: list[str], *, config: dict[str, Any], products: list[dict[str, Any]], published: bool = False) -> int:
    print("Konbini feed sanity check failed:", file=sys.stderr)
    print(format_major_three_counts(config, products), file=sys.stderr)
    for failure in failures:
        print(f"- {failure}", file=sys.stderr)
    if not published:
        print("Public feed was not modified.", file=sys.stderr)
    return 2


def atomic_write_text(path: pathlib.Path, text: str) -> None:
    tmp_path = path.with_name(f".{path.name}.tmp")
    tmp_path.write_text(text, encoding="utf-8")
    tmp_path.replace(path)


def main() -> int:
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument("--config", default=str(CONFIG_PATH))
    arg_parser.add_argument("--date", help="Draft date folder to build from.")
    arg_parser.add_argument("--publish", action="store_true", help="Write the public utility feed.")
    arg_parser.add_argument(
        "--force-publish",
        action="store_true",
        help=(
            "Emergency override: publish even when source/feed/content sanity checks fail. "
            "Use only after manual verification; the warning and failing counts will be printed."
        ),
    )
    arg_parser.add_argument(
        "--allow-empty-required-source",
        action="store_true",
        help="Bypass required source product-count sanity failures after manual verification.",
    )
    arg_parser.add_argument(
        "--skip-source-sanity",
        action="store_true",
        help="Bypass source and generated feed product-count sanity checks.",
    )
    args = arg_parser.parse_args()

    config_path = pathlib.Path(args.config)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    draft_root = ROOT / config.get("draftRoot", "private/konbini-radar")
    draft_dir = draft_root / args.date if args.date else latest_draft_dir(draft_root)
    manifest_path = draft_dir / "fetch-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source_by_id = {source["id"]: source for source in config["sources"]}
    today = dt.date.today()
    products: list[dict[str, Any]] = []
    context_sources: list[dict[str, Any]] = []
    setusoku_bogo_offers: list[dict[str, Any]] = []
    warnings: list[str] = []
    source_summaries: list[dict[str, Any]] = []

    for fetched in manifest["sources"]:
        source = source_by_id[fetched["id"]]
        raw_path = ROOT / fetched["rawPath"]
        parser = parse_source(raw_path)
        source_summary = {
            "id": source["id"],
            "name": english_source_name(source["name"]),
            "nameJa": source["name"],
            "tier": source["tier"],
            "chain": source.get("chain"),
            "url": source["url"],
            "resolvedUrl": fetched.get("resolvedUrl") or source["url"],
            "parser": source["parser"],
            "ok": fetched["ok"],
            "status": fetched["status"],
            "bytes": fetched.get("bytes", 0),
            "title": sanitize_english_output(translate_japanese_text(parser.title, "source page")),
            "titleJa": parser.title,
            "productCount": 0,
        }
        source_summaries.append(source_summary)
        if not fetched["ok"]:
            warnings.append(f"{source['id']} fetch status {fetched['status']}; skipped parser confidence.")
            continue

        if source["parser"] == "seven_weekly":
            parsed, parser_warnings = parse_seven(parser.events, source, today)
            source_summary["productCount"] = len(parsed)
            products.extend(parsed)
            warnings.extend(parser_warnings)
        elif source["parser"] == "familymart_weekly":
            familymart_html = decode_html(raw_path)
            parsed, parser_warnings = parse_familymart(familymart_html, parser.events, source, today)
            source_summary["productCount"] = len(parsed)
            products.extend(parsed)
            warnings.extend(parser_warnings)
        elif source["parser"] == "lawson_weekly":
            lawson_weekly_html = decode_html(raw_path)
            parsed, parser_warnings = parse_lawson(lawson_weekly_html, parser.events, source, today)
            source_summary["productCount"] = len(parsed)
            products.extend(parsed)
            warnings.extend(parser_warnings)
        elif source["parser"] == "lawson_lab_weekly":
            lawson_html = decode_html(raw_path)
            parsed, parser_warnings = parse_lawson_lab(lawson_html, parser.events, source, today)
            source_summary["productCount"] = len(parsed)
            products.extend(parsed)
            warnings.extend(parser_warnings)
        elif source["parser"] == "setusoku_bogo":
            parsed_contexts, parsed_offers, parser_warnings = parse_setusoku_bogo_context(parser.events, source, today)
            context_sources.extend(parsed_contexts)
            setusoku_bogo_offers.extend(parsed_offers)
            warnings.extend(parser_warnings)
        else:
            context_sources.append(
                {
                    "id": source["id"],
                    "name": source["name"],
                    "tier": source["tier"],
                    "language": source.get("language", "ja"),
                    "url": source["url"],
                    "text": visible_text(parser),
                }
            )

    products = merge_products(products)

    source_sanity_failures = collect_source_sanity_failures(source_summaries, source_by_id)

    enrich_lawson_from_detail_snapshots(products, manifest.get("lawsonDetailSnapshots") or [])
    seven_html = ""
    family_html = ""
    for fetched in manifest["sources"]:
        if not fetched["ok"]:
            continue
        if fetched["id"] == "seven_this_week":
            seven_html = decode_html(ROOT / fetched["rawPath"])
        elif fetched["id"] == "familymart_newgoods":
            family_html = decode_html(ROOT / fetched["rawPath"])
    enrich_product_thumbnails(products, seven_html, family_html)

    add_local_signals(products, context_sources)
    products.extend(create_unmatched_setusoku_deal_products(products, setusoku_bogo_offers))
    assign_product_ids(products)
    for product in products:
        tag_product(product, config.get("keywordContexts", {}))
        score_product(product, today)
        finalize_product_copy(product)

    generic_counts = Counter(
        product["chain"] for product in products if is_obviously_generic_product_title(product.get("name") or "")
    )
    if generic_counts:
        products = [
            product for product in products if not is_obviously_generic_product_title(product.get("name") or "")
        ]
        dropped = ", ".join(f"{chain} {count}" for chain, count in sorted(generic_counts.items()))
        warnings.append(f"Dropped products whose Japanese titles could not produce specific English names: {dropped}.")

    products.sort(key=lambda item: (-item["score"], item.get("releaseDate") or "", item["chain"], item["nameJa"]))

    feed_sanity_failures = collect_feed_sanity_failures(config, products)
    content_quality_failures = collect_content_quality_failures(products, source_summaries)

    week_label = f"Week of {today.isoformat()}"
    feed = {
        "schemaVersion": 1,
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "weekLabel": week_label,
        "intro": build_intro(products, week_label),
        "sources": source_summaries,
        "products": products,
        "warnings": warnings,
    }

    draft_feed = draft_dir / "feed.draft.json"
    feed_json = json.dumps(feed, ensure_ascii=False, indent=2) + "\n"
    draft_feed.write_text(feed_json, encoding="utf-8")
    print(f"Wrote {draft_feed.relative_to(ROOT)} with {len(products)} products")
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")

    active_sanity_failures: list[str] = []
    if not (args.allow_empty_required_source or args.skip_source_sanity):
        active_sanity_failures.extend(source_sanity_failures)
    if not args.skip_source_sanity:
        active_sanity_failures.extend(feed_sanity_failures)
    active_sanity_failures.extend(content_quality_failures)

    publish_blockers = source_sanity_failures + feed_sanity_failures + content_quality_failures
    if active_sanity_failures and not args.publish:
        return fail_sanity(active_sanity_failures, config=config, products=products)

    if args.publish:
        if publish_blockers and not args.force_publish:
            return fail_sanity(publish_blockers, config=config, products=products)
        if publish_blockers and args.force_publish:
            print("WARNING: --force-publish used despite sanity failures.", file=sys.stderr)
            print(format_major_three_counts(config, products), file=sys.stderr)
            for failure in publish_blockers:
                print(f"- {failure}", file=sys.stderr)
        public_path = ROOT / config["publicFeedPath"]
        public_path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(public_path, feed_json)
        print(f"Published {public_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
