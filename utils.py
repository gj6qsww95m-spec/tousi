"""
日本株インデックス構成銘柄リスト
2026年1月時点の日経225、TOPIX主要銘柄
"""

def get_nikkei225_stocks():
    """
    日経225の全構成銘柄を取得
    
    Returns:
        list: (ティッカーシンボル, 銘柄名) のタプルのリスト
    """
    return [
        # 水産・農林業
        ("1332.T", "ニッスイ"),
        ("1333.T", "マルハニチロ"),
        
        # 鉱業
        ("1605.T", "INPEX"),
        
        # 建設業
        ("1721.T", "コムシスホールディングス"),
        ("1801.T", "大成建設"),
        ("1802.T", "大林組"),
        ("1803.T", "清水建設"),
        ("1808.T", "長谷工コーポレーション"),
        ("1812.T", "鹿島建設"),
        ("1925.T", "大和ハウス工業"),
        ("1928.T", "積水ハウス"),
        ("1963.T", "日揮ホールディングス"),
        
        # 食料品
        ("2002.T", "日清製粉グループ本社"),
        ("2269.T", "明治ホールディングス"),
        ("2282.T", "日本ハム"),
        ("2413.T", "エムスリー"),
        ("2432.T", "ディー・エヌ・エー"),
        ("2501.T", "サッポロホールディングス"),
        ("2502.T", "アサヒグループホールディングス"),
        ("2503.T", "キリンホールディングス"),
        ("2531.T", "宝ホールディングス"),
        ("2768.T", "双日"),
        ("2801.T", "キッコーマン"),
        ("2802.T", "味の素"),
        ("2871.T", "ニチレイ"),
        ("2914.T", "日本たばこ産業"),
        
        # 繊維製品
        ("3101.T", "東洋紡"),
        ("3103.T", "ユニチカ"),
        ("3401.T", "帝人"),
        ("3402.T", "東レ"),
        ("3405.T", "クラレ"),
        ("3407.T", "旭化成"),
        
        # パルプ・紙
        ("3861.T", "王子ホールディングス"),
        ("3863.T", "日本製紙"),
        
        # 化学
        ("3086.T", "J.フロント リテイリング"),
        ("3099.T", "三越伊勢丹ホールディングス"),
        ("3382.T", "セブン&アイ・ホールディングス"),
        ("4004.T", "レゾナック・ホールディングス"),
        ("4005.T", "住友化学"),
        ("4021.T", "日産化学"),
        ("4042.T", "東ソー"),
        ("4043.T", "トクヤマ"),
        ("4061.T", "デンカ"),
        ("4062.T", "イビデン"),
        ("4063.T", "信越化学工業"),
        ("4151.T", "協和キリン"),
        ("4183.T", "三井化学"),
        ("4188.T", "三菱ケミカルグループ"),
        ("4208.T", "UBE"),
        ("4272.T", "日本化薬"),
        ("4324.T", "電通グループ"),
        ("4452.T", "花王"),
        ("4502.T", "武田薬品工業"),
        ("4503.T", "アステラス製薬"),
        ("4506.T", "住友ファーマ"),
        ("4507.T", "塩野義製薬"),
        ("4519.T", "中外製薬"),
        ("4523.T", "エーザイ"),
        ("4543.T", "テルモ"),
        ("4568.T", "第一三共"),
        ("4578.T", "大塚ホールディングス"),
        ("4661.T", "オリエンタルランド"),
        ("4689.T", "LINEヤフー"),
        ("4704.T", "トレンドマイクロ"),
        ("4751.T", "サイバーエージェント"),
        ("4755.T", "楽天グループ"),
        ("4901.T", "富士フイルムホールディングス"),
        ("4911.T", "資生堂"),
        
        # 石油・石炭製品
        ("5019.T", "出光興産"),
        ("5020.T", "ENEOSホールディングス"),
        
        # ゴム製品
        ("5101.T", "横浜ゴム"),
        ("5108.T", "ブリヂストン"),
        
        # ガラス・土石製品
        ("5201.T", "AGC"),
        ("5202.T", "日本板硝子"),
        ("5214.T", "日本電気硝子"),
        ("5232.T", "住友大阪セメント"),
        ("5233.T", "太平洋セメント"),
        ("5332.T", "TOTO"),
        ("5333.T", "日本ガイシ"),
        
        # 鉄鋼
        ("5401.T", "日本製鉄"),
        ("5406.T", "神戸製鋼所"),
        ("5411.T", "JFEホールディングス"),
        
        # 非鉄金属
        ("5706.T", "三井金属鉱業"),
        ("5707.T", "東邦亜鉛"),
        ("5711.T", "三菱マテリアル"),
        ("5713.T", "住友金属鉱山"),
        ("5714.T", "DOWAホールディングス"),
        ("5801.T", "古河電気工業"),
        ("5802.T", "住友電気工業"),
        ("5803.T", "フジクラ"),
        ("5831.T", "しずおかフィナンシャルグループ"),
        
        # 金属製品
        ("5901.T", "東洋製罐グループホールディングス"),
        
        # 機械
        ("6103.T", "オークマ"),
        ("6113.T", "アマダ"),
        ("6273.T", "SMC"),
        ("6301.T", "小松製作所"),
        ("6302.T", "住友重機械工業"),
        ("6305.T", "日立建機"),
        ("6326.T", "クボタ"),
        ("6361.T", "荏原製作所"),
        ("6366.T", "千代田化工建設"),
        ("6367.T", "ダイキン工業"),
        ("6471.T", "日本精工"),
        ("6472.T", "NTN"),
        ("6473.T", "ジェイテクト"),
        
        # 電気機器
        ("6479.T", "ミネベアミツミ"),
        ("6501.T", "日立製作所"),
        ("6503.T", "三菱電機"),
        ("6504.T", "富士電機"),
        ("6506.T", "安川電機"),
        ("6526.T", "ソシオネクスト"),
        ("6594.T", "ニデック"),
        ("6645.T", "オムロン"),
        ("6674.T", "ジーエス・ユアサ コーポレーション"),
        ("6701.T", "NEC"),
        ("6702.T", "富士通"),
        ("6723.T", "ルネサスエレクトロニクス"),
        ("6724.T", "セイコーエプソン"),
        ("6752.T", "パナソニック ホールディングス"),
        ("6753.T", "シャープ"),
        ("6758.T", "ソニーグループ"),
        ("6762.T", "TDK"),
        ("6770.T", "アルプスアルパイン"),
        ("6806.T", "ヒロセ電機"),
        ("6841.T", "横河電機"),
        ("6857.T", "アドバンテスト"),
        ("6861.T", "キーエンス"),
        ("6902.T", "デンソー"),
        ("6920.T", "レーザーテック"),
        ("6952.T", "カシオ計算機"),
        ("6954.T", "ファナック"),
        ("6963.T", "ローム"),
        ("6971.T", "京セラ"),
        ("6976.T", "太陽誘電"),
        ("6981.T", "村田製作所"),
        ("6988.T", "日東電工"),
        
        # 輸送用機器
        ("7003.T", "三井E&S"),
        ("7004.T", "日立造船"),
        ("7011.T", "三菱重工業"),
        ("7012.T", "川崎重工業"),
        ("7013.T", "IHI"),
        ("7186.T", "コンコルディア・フィナンシャルグループ"),
        ("7201.T", "日産自動車"),
        ("7202.T", "いすゞ自動車"),
        ("7203.T", "トヨタ自動車"),
        ("7205.T", "日野自動車"),
        ("7211.T", "三菱自動車工業"),
        ("7261.T", "マツダ"),
        ("7267.T", "本田技研工業"),
        ("7269.T", "スズキ"),
        ("7270.T", "SUBARU"),
        ("7272.T", "ヤマハ発動機"),
        
        # 精密機器
        ("7731.T", "ニコン"),
        ("7733.T", "オリンパス"),
        ("7735.T", "SCREENホールディングス"),
        ("7741.T", "HOYA"),
        ("7751.T", "キヤノン"),
        ("7752.T", "リコー"),
        ("7762.T", "シチズン時計"),
        
        # その他製品
        ("7832.T", "バンダイナムコホールディングス"),
        ("7911.T", "凸版印刷"),
        ("7912.T", "大日本印刷"),
        ("7951.T", "ヤマハ"),
        ("7974.T", "任天堂"),
        
        # 電気・ガス業
        ("9501.T", "東京電力ホールディングス"),
        ("9502.T", "中部電力"),
        ("9503.T", "関西電力"),
        ("9531.T", "東京ガス"),
        ("9532.T", "大阪ガス"),
        
        # 陸運業
        ("9001.T", "東武鉄道"),
        ("9005.T", "東急"),
        ("9007.T", "小田急電鉄"),
        ("9008.T", "京王電鉄"),
        ("9009.T", "京成電鉄"),
        ("9020.T", "東日本旅客鉄道"),
        ("9021.T", "西日本旅客鉄道"),
        ("9022.T", "東海旅客鉄道"),
        ("9042.T", "阪急阪神ホールディングス"),
        ("9064.T", "ヤマトホールディングス"),
        
        # 海運業
        ("9101.T", "日本郵船"),
        ("9104.T", "商船三井"),
        ("9107.T", "川崎汽船"),
        
        # 空運業
        ("9201.T", "日本航空"),
        ("9202.T", "ANAホールディングス"),
        
        # 情報・通信業
        ("9432.T", "日本電信電話"),
        ("9433.T", "KDDI"),
        ("9434.T", "ソフトバンク"),
        ("9613.T", "NTTデータグループ"),
        ("9697.T", "カプコン"),
        ("9735.T", "セコム"),
        ("9766.T", "コナミグループ"),
        ("9984.T", "ソフトバンクグループ"),
        
        # 卸売業
        ("8001.T", "伊藤忠商事"),
        ("8002.T", "丸紅"),
        ("8015.T", "豊田通商"),
        ("8031.T", "三井物産"),
        ("8035.T", "東京エレクトロン"),
        ("8053.T", "住友商事"),
        ("8058.T", "三菱商事"),
        
        # 小売業
        ("3697.T", "SHIFT"),
        ("8233.T", "高島屋"),
        ("8252.T", "丸井グループ"),
        ("8267.T", "イオン"),
        
        # 銀行業
        ("8303.T", "新生銀行"),
        ("8304.T", "あおぞら銀行"),
        ("8306.T", "三菱UFJフィナンシャル・グループ"),
        ("8308.T", "りそなホールディングス"),
        ("8309.T", "三井住友トラスト・ホールディングス"),
        ("8316.T", "三井住友フィナンシャルグループ"),
        ("8331.T", "千葉銀行"),
        ("8354.T", "ふくおかフィナンシャルグループ"),
        ("8411.T", "みずほフィナンシャルグループ"),
        
        # 証券・商品先物取引業
        ("8601.T", "大和証券グループ本社"),
        ("8604.T", "野村ホールディングス"),
        
        # 保険業
        ("8725.T", "MS&ADインシュアランスグループホールディングス"),
        ("8750.T", "第一生命ホールディングス"),
        ("8766.T", "東京海上ホールディングス"),
        ("8795.T", "T&Dホールディングス"),
        
        # その他金融業
        ("8253.T", "クレディセゾン"),
        ("8591.T", "オリックス"),
        
        # 不動産業
        ("8801.T", "三井不動産"),
        ("8802.T", "三菱地所"),
        ("8804.T", "東京建物"),
        ("8830.T", "住友不動産"),
        
        # サービス業
        ("2809.T", "キユーピー"),
        ("6098.T", "リクルートホールディングス"),
        ("9602.T", "東宝"),
        ("9603.T", "エイチ・アイ・エス"),
        ("9843.T", "ニトリホールディングス"),
        ("9983.T", "ファーストリテイリング"),
    ]


def get_topix_core30_stocks():
    """
    TOPIX Core30の構成銘柄を取得
    時価総額・流動性が特に高い30銘柄
    
    Returns:
        list: (ティッカーシンボル, 銘柄名) のタプルのリスト
    """
    return [
        ("7203.T", "トヨタ自動車"),
        ("6758.T", "ソニーグループ"),
        ("9984.T", "ソフトバンクグループ"),
        ("6861.T", "キーエンス"),
        ("9983.T", "ファーストリテイリング"),
        ("8306.T", "三菱UFJフィナンシャル・グループ"),
        ("8316.T", "三井住友フィナンシャルグループ"),
        ("8411.T", "みずほフィナンシャルグループ"),
        ("6098.T", "リクルートホールディングス"),
        ("8035.T", "東京エレクトロン"),
        ("9432.T", "日本電信電話"),
        ("9433.T", "KDDI"),
        ("6501.T", "日立製作所"),
        ("8058.T", "三菱商事"),
        ("8001.T", "伊藤忠商事"),
        ("8031.T", "三井物産"),
        ("4063.T", "信越化学工業"),
        ("7974.T", "任天堂"),
        ("4502.T", "武田薬品工業"),
        ("4568.T", "第一三共"),
        ("6367.T", "ダイキン工業"),
        ("6902.T", "デンソー"),
        ("8766.T", "東京海上ホールディングス"),
        ("4543.T", "テルモ"),
        ("6954.T", "ファナック"),
        ("4911.T", "資生堂"),
        ("6981.T", "村田製作所"),
        ("8801.T", "三井不動産"),
        ("8802.T", "三菱地所"),
        ("5020.T", "ENEOSホールディングス"),
    ]


def get_topix_large70_stocks():
    """
    TOPIX Large70の追加銘柄を取得
    Core30に次ぐ大型株70銘柄（一部抜粋）
    
    Returns:
        list: (ティッカーシンボル, 銘柄名) のタプルのリスト
    """
    return [
        ("7267.T", "本田技研工業"),
        ("6752.T", "パナソニック ホールディングス"),
        ("9613.T", "エヌ・ティ・ティ・データ"),
        ("6702.T", "富士通"),
        ("8053.T", "住友商事"),
        ("8002.T", "丸紅"),
        ("4503.T", "アステラス製薬"),
        ("4519.T", "中外製薬"),
        ("4523.T", "エーザイ"),
        ("7741.T", "HOYA"),
        ("6920.T", "レーザーテック"),
        ("6857.T", "アドバンテスト"),
        ("6503.T", "三菱電機"),
        ("7751.T", "キヤノン"),
        ("4901.T", "富士フイルムホールディングス"),
        ("6971.T", "京セラ"),
        ("8591.T", "オリックス"),
        ("8604.T", "野村ホールディングス"),
        ("8750.T", "第一生命ホールディングス"),
        ("8725.T", "MS&ADインシュアランスグループホールディングス"),
        ("5401.T", "日本製鉄"),
        ("5411.T", "JFEホールディングス"),
        ("5108.T", "ブリヂストン"),
        ("9020.T", "東日本旅客鉄道"),
        ("9022.T", "東海旅客鉄道"),
        ("9021.T", "西日本旅客鉄道"),
        ("3382.T", "セブン&アイ・ホールディングス"),
        ("8267.T", "イオン"),
        ("2914.T", "日本たばこ産業"),
        ("2802.T", "味の素"),
        ("2503.T", "キリンホールディングス"),
        ("2502.T", "アサヒグループホールディングス"),
        ("9531.T", "東京ガス"),
        ("9502.T", "中部電力"),
        ("9503.T", "関西電力"),
        ("1925.T", "大和ハウス工業"),
        ("1928.T", "積水ハウス"),
        ("8830.T", "住友不動産"),
        ("7832.T", "バンダイナムコホールディングス"),
        ("4661.T", "オリエンタルランド"),
        ("9101.T", "日本郵船"),
        ("9104.T", "商船三井"),
        ("4324.T", "電通グループ"),
        ("6301.T", "小松製作所"),
        ("7011.T", "三菱重工業"),
        ("5713.T", "住友金属鉱山"),
        ("5802.T", "住友電気工業"),
        ("3407.T", "旭化成"),
        ("4005.T", "住友化学"),
        ("4188.T", "三菱ケミカルグループ"),
        ("5201.T", "AGC"),
        ("7201.T", "日産自動車"),
        ("7269.T", "スズキ"),
        ("7270.T", "SUBARU"),
        ("6645.T", "オムロン"),
        ("4452.T", "花王"),
        ("3861.T", "王子ホールディングス"),
        ("3402.T", "東レ"),
        ("9202.T", "ANAホールディングス"),
        ("9201.T", "日本航空"),
        ("4755.T", "楽天グループ"),
        ("2413.T", "エムスリー"),
        ("4704.T", "トレンドマイクロ"),
        ("9735.T", "セコム"),
        ("1801.T", "大成建設"),
        ("1802.T", "大林組"),
        ("1803.T", "清水建設"),
        ("1812.T", "鹿島建設"),
        ("9064.T", "ヤマトホールディングス"),
        ("4751.T", "サイバーエージェント"),
    ]


def get_stocks_by_index(index_name: str):
    """
    インデックス名に応じた銘柄リストを取得
    
    Args:
        index_name: インデックス名 ("日経225", "TOPIX Core30", "TOPIX 100", "全銘柄", "S&P 500",
                    "日本インデックスETF", "米国インデックスETF")
    
    Returns:
        list: (ティッカーシンボル, 銘柄名) のタプルのリスト
    """
    if index_name == "日経225":
        return get_nikkei225_stocks()
    elif index_name == "TOPIX Core30":
        return get_topix_core30_stocks()
    elif index_name == "TOPIX 100":
        # TOPIX Core30 + Large70の一部
        core30 = get_topix_core30_stocks()
        large70 = get_topix_large70_stocks()
        # 重複を削除
        combined = core30 + large70
        seen = set()
        unique_stocks = []
        for ticker, name in combined:
            if ticker not in seen:
                seen.add(ticker)
                unique_stocks.append((ticker, name))
        return unique_stocks
    elif index_name == "日本インデックスETF":
        return get_japan_index_etfs()
    elif index_name == "全銘柄":
        # 日経225 + TOPIX主要銘柄を統合
        nikkei = get_nikkei225_stocks()
        topix = get_topix_core30_stocks() + get_topix_large70_stocks()
        # 重複を削除
        combined = nikkei + topix
        seen = set()
        unique_stocks = []
        for ticker, name in combined:
            if ticker not in seen:
                seen.add(ticker)
                unique_stocks.append((ticker, name))
        return unique_stocks
    elif index_name == "S&P 500":
        return get_sp500_stocks()
    elif index_name == "米国インデックスETF":
        return get_us_index_etfs()
    else:
        return get_nikkei225_stocks()


def get_sp500_stocks():
    """
    S&P 500の主要100銘柄を取得
    
    Returns:
        list: (ティッカーシンボル, 銘柄名) のタプルのリスト
    """
    return [
        # テクノロジー
        ("AAPL", "Apple Inc."),
        ("MSFT", "Microsoft Corporation"),
        ("NVDA", "NVIDIA Corporation"),
        ("GOOGL", "Alphabet Inc. (Class A)"),
        ("GOOG", "Alphabet Inc. (Class C)"),
        ("META", "Meta Platforms Inc."),
        ("AMZN", "Amazon.com Inc."),
        ("TSLA", "Tesla Inc."),
        ("AVGO", "Broadcom Inc."),
        ("ORCL", "Oracle Corporation"),
        ("CRM", "Salesforce Inc."),
        ("AMD", "Advanced Micro Devices Inc."),
        ("ADBE", "Adobe Inc."),
        ("CSCO", "Cisco Systems Inc."),
        ("ACN", "Accenture plc"),
        ("IBM", "IBM Corporation"),
        ("INTC", "Intel Corporation"),
        ("QCOM", "Qualcomm Inc."),
        ("TXN", "Texas Instruments Inc."),
        ("NOW", "ServiceNow Inc."),
        
        # 金融
        ("JPM", "JPMorgan Chase & Co."),
        ("V", "Visa Inc."),
        ("MA", "Mastercard Inc."),
        ("BAC", "Bank of America Corp."),
        ("WFC", "Wells Fargo & Co."),
        ("GS", "Goldman Sachs Group Inc."),
        ("MS", "Morgan Stanley"),
        ("AXP", "American Express Co."),
        ("BLK", "BlackRock Inc."),
        ("C", "Citigroup Inc."),
        ("SCHW", "Charles Schwab Corp."),
        ("BX", "Blackstone Inc."),
        ("SPGI", "S&P Global Inc."),
        ("CB", "Chubb Limited"),
        ("MMC", "Marsh & McLennan Companies"),
        
        # ヘルスケア
        ("UNH", "UnitedHealth Group Inc."),
        ("JNJ", "Johnson & Johnson"),
        ("LLY", "Eli Lilly and Company"),
        ("PFE", "Pfizer Inc."),
        ("MRK", "Merck & Co. Inc."),
        ("ABBV", "AbbVie Inc."),
        ("TMO", "Thermo Fisher Scientific Inc."),
        ("ABT", "Abbott Laboratories"),
        ("DHR", "Danaher Corporation"),
        ("BMY", "Bristol-Myers Squibb Co."),
        ("AMGN", "Amgen Inc."),
        ("GILD", "Gilead Sciences Inc."),
        ("CVS", "CVS Health Corporation"),
        ("ISRG", "Intuitive Surgical Inc."),
        ("MDT", "Medtronic plc"),
        
        # 消費財・小売
        ("WMT", "Walmart Inc."),
        ("PG", "Procter & Gamble Co."),
        ("COST", "Costco Wholesale Corp."),
        ("KO", "Coca-Cola Company"),
        ("PEP", "PepsiCo Inc."),
        ("HD", "Home Depot Inc."),
        ("MCD", "McDonald's Corporation"),
        ("NKE", "Nike Inc."),
        ("SBUX", "Starbucks Corporation"),
        ("TGT", "Target Corporation"),
        ("LOW", "Lowe's Companies Inc."),
        ("EL", "Estée Lauder Companies Inc."),
        ("CL", "Colgate-Palmolive Co."),
        ("GIS", "General Mills Inc."),
        ("KHC", "Kraft Heinz Company"),
        
        # 通信
        ("VZ", "Verizon Communications Inc."),
        ("T", "AT&T Inc."),
        ("CMCSA", "Comcast Corporation"),
        ("TMUS", "T-Mobile US Inc."),
        ("DIS", "Walt Disney Company"),
        ("NFLX", "Netflix Inc."),
        
        # エネルギー
        ("XOM", "Exxon Mobil Corporation"),
        ("CVX", "Chevron Corporation"),
        ("COP", "ConocoPhillips"),
        ("SLB", "Schlumberger Limited"),
        ("EOG", "EOG Resources Inc."),
        ("MPC", "Marathon Petroleum Corp."),
        ("PSX", "Phillips 66"),
        ("VLO", "Valero Energy Corp."),
        
        # 工業
        ("CAT", "Caterpillar Inc."),
        ("BA", "Boeing Company"),
        ("HON", "Honeywell International Inc."),
        ("UPS", "United Parcel Service Inc."),
        ("GE", "General Electric Company"),
        ("RTX", "RTX Corporation"),
        ("DE", "Deere & Company"),
        ("LMT", "Lockheed Martin Corp."),
        ("UNP", "Union Pacific Corporation"),
        ("MMM", "3M Company"),
        
        # 素材
        ("LIN", "Linde plc"),
        ("APD", "Air Products and Chemicals Inc."),
        ("SHW", "Sherwin-Williams Company"),
        ("FCX", "Freeport-McMoRan Inc."),
        ("NEM", "Newmont Corporation"),
        
        # 不動産・公益
        ("NEE", "NextEra Energy Inc."),
        ("DUK", "Duke Energy Corporation"),
        ("SO", "Southern Company"),
        ("D", "Dominion Energy Inc."),
        ("AMT", "American Tower Corp."),
    ]


def get_japan_index_etfs():
    """
    日本の主要インデックスETFを取得
    
    Returns:
        list: (ティッカーシンボル, 銘柄名) のタプルのリスト
    """
    return [
        # 日経225連動ETF
        ("1321.T", "日経225連動型上場投資信託"),
        ("1346.T", "MAXIS 日経225上場投信"),
        ("1329.T", "iシェアーズ・コア 日経225 ETF"),
        ("1330.T", "上場インデックスファンド225"),
        ("1397.T", "SMDAM 日経225上場投信"),
        
        # TOPIX連動ETF
        ("1306.T", "TOPIX連動型上場投資信託"),
        ("1348.T", "MAXIS トピックス上場投信"),
        ("1308.T", "上場インデックスファンドTOPIX"),
        ("1473.T", "One ETF トピックス"),
        ("1475.T", "iシェアーズ・コア TOPIX ETF"),
        
        # JPX日経インデックス400
        ("1474.T", "One ETF JPX日経400"),
        ("1364.T", "iシェアーズ JPX日経400 ETF"),
        ("1592.T", "上場インデックスファンドJPX日経400"),
        ("1593.T", "MAXIS JPX日経インデックス400上場投信"),
        
        # 日経高配当株50
        ("1489.T", "NEXT FUNDS 日経平均高配当株50指数連動型上場投信"),
        
        # 東証REIT指数
        ("1343.T", "NEXT FUNDS 東証REIT指数連動型上場投信"),
        ("1345.T", "上場インデックスファンドJリート"),
        ("1398.T", "SMDAM 東証REIT指数上場投信"),
        
        # マザーズ指数（グロース市場）
        ("2516.T", "東証マザーズETF"),
        
        # 日経平均レバレッジ・インバース（参考）
        ("1570.T", "NEXT FUNDS 日経平均レバレッジ・インデックス連動型上場投信"),
        ("1357.T", "NEXT FUNDS 日経平均ダブルインバース・インデックス連動型上場投信"),
    ]


def get_us_index_etfs():
    """
    米国の主要インデックスETFを取得
    
    Returns:
        list: (ティッカーシンボル, 銘柄名) のタプルのリスト
    """
    return [
        # S&P 500連動ETF
        ("SPY", "SPDR S&P 500 ETF Trust"),
        ("VOO", "Vanguard S&P 500 ETF"),
        ("IVV", "iShares Core S&P 500 ETF"),
        ("SPLG", "SPDR Portfolio S&P 500 ETF"),
        
        # ダウ・ジョーンズ連動ETF
        ("DIA", "SPDR Dow Jones Industrial Average ETF"),
        
        # NASDAQ-100連動ETF
        ("QQQ", "Invesco QQQ Trust (NASDAQ-100)"),
        ("QQQM", "Invesco NASDAQ 100 ETF"),
        
        # 米国全体市場
        ("VTI", "Vanguard Total Stock Market ETF"),
        ("ITOT", "iShares Core S&P Total U.S. Stock Market ETF"),
        ("SPTM", "SPDR Portfolio S&P 1500 Composite Stock Market ETF"),
        
        # Russell 2000（小型株）
        ("IWM", "iShares Russell 2000 ETF"),
        ("VTWO", "Vanguard Russell 2000 ETF"),
        
        # Russell 1000（大型株）
        ("IWB", "iShares Russell 1000 ETF"),
        ("VONE", "Vanguard Russell 1000 ETF"),
        
        # セクターETF（参考）
        ("XLK", "Technology Select Sector SPDR Fund"),
        ("XLF", "Financial Select Sector SPDR Fund"),
        ("XLE", "Energy Select Sector SPDR Fund"),
        ("XLV", "Health Care Select Sector SPDR Fund"),
        ("XLY", "Consumer Discretionary Select Sector SPDR Fund"),
        ("XLP", "Consumer Staples Select Sector SPDR Fund"),
        ("XLI", "Industrial Select Sector SPDR Fund"),
        ("XLB", "Materials Select Sector SPDR Fund"),
        ("XLU", "Utilities Select Sector SPDR Fund"),
        ("XLRE", "Real Estate Select Sector SPDR Fund"),
        
        # 配当株ETF
        ("VYM", "Vanguard High Dividend Yield ETF"),
        ("SCHD", "Schwab U.S. Dividend Equity ETF"),
        ("DVY", "iShares Select Dividend ETF"),
        
        # グロース・バリューETF
        ("VUG", "Vanguard Growth ETF"),
        ("VTV", "Vanguard Value ETF"),
        ("IWF", "iShares Russell 1000 Growth ETF"),
        ("IWD", "iShares Russell 1000 Value ETF"),
        
        # レバレッジ・インバース（参考）
        ("TQQQ", "ProShares UltraPro QQQ (3x NASDAQ-100)"),
        ("SQQQ", "ProShares UltraPro Short QQQ (-3x NASDAQ-100)"),
        ("UPRO", "ProShares UltraPro S&P 500 (3x S&P 500)"),
        ("SPXU", "ProShares UltraPro Short S&P 500 (-3x S&P 500)"),
    ]
