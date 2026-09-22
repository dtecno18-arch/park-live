import time, requests, sqlite3, re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
app=FastAPI(title='Park LIVE')
PARKS={'LAND':'3cc919f1-d16d-43e0-8c3f-1dd269bd1a42','SEA':'67b290d5-3478-4f23-b601-2f8fb71ba803'}
cache={}
JP_NAMES={'Enchanted Tale of Beauty and the Beast': '美女と野獣“魔法のものがたり”', "Baymax's Happy Ride": 'ベイマックスのハッピーライド', 'The Happy Ride with Baymax': 'ベイマックスのハッピーライド', "Pooh's Hunny Hunt": 'プーさんのハニーハント', 'Monsters, Inc. Ride & Go Seek!': 'モンスターズ・インク“ライド＆ゴーシーク！”', 'Space Mountain': 'スペース・マウンテン', 'Big Thunder Mountain': 'ビッグサンダー・マウンテン', 'Splash Mountain': 'スプラッシュ・マウンテン', 'Haunted Mansion': 'ホーンテッドマンション', 'Pirates of the Caribbean': 'カリブの海賊', 'Jungle Cruise: Wildlife Expeditions': 'ジャングルクルーズ：ワイルドライフ・エクスペディション', 'Western River Railroad': 'ウエスタンリバー鉄道', 'Mark Twain Riverboat': '蒸気船マークトウェイン号', 'Tom Sawyer Island Rafts': 'トムソーヤ島いかだ', 'Country Bear Theater': 'カントリーベア・シアター', "Peter Pan's Flight": 'ピーターパン空の旅', "Snow White's Adventures": '白雪姫と七人のこびと', "Pinocchio's Daring Journey": 'ピノキオの冒険旅行', 'Dumbo The Flying Elephant': '空飛ぶダンボ', 'Castle Carrousel': 'キャッスルカルーセル', "Alice's Tea Party": 'アリスのティーパーティー', "It's a Small World": 'イッツ・ア・スモールワールド', "Roger Rabbit's Car Toon Spin": 'ロジャーラビットのカートゥーンスピン', "Goofy's Paint 'n' Play House": 'グーフィーのペイント＆プレイハウス', "Chip 'n Dale's Treehouse": 'チップとデールのツリーハウス', "Donald's Boat": 'ドナルドのボート', "Minnie's House": 'ミニーの家', 'Star Tours: The Adventures Continue': 'スター・ツアーズ：ザ・アドベンチャーズ・コンティニュー', "Buzz Lightyear's Astro Blasters": 'バズ・ライトイヤーのアストロブラスター', 'Stitch Encounter': 'スティッチ・エンカウンター', 'Omnibus': 'オムニバス', 'Penny Arcade': 'ペニーアーケード', 'Soaring: Fantastic Flight': 'ソアリン：ファンタスティック・フライト', 'Journey to the Center of the Earth': 'センター・オブ・ジ・アース', '20,000 Leagues Under the Sea': '海底2万マイル', 'Tower of Terror': 'タワー・オブ・テラー', 'Toy Story Mania!': 'トイ・ストーリー・マニア！', 'Indiana Jones Adventure: Temple of the Crystal Skull': 'インディ・ジョーンズ・アドベンチャー：クリスタルスカルの魔宮', 'Raging Spirits': 'レイジングスピリッツ', "Anna and Elsa's Frozen Journey": 'アナとエルサのフローズンジャーニー', "Peter Pan's Never Land Adventure": 'ピーターパンのネバーランドアドベンチャー', "Fairy Tinker Bell's Busy Buggies": 'フェアリー・ティンカーベルのビジーバギー', "Rapunzel's Lantern Festival": 'ラプンツェルのランタンフェスティバル', 'Nemo & Friends SeaRider': 'ニモ＆フレンズ・シーライダー', 'Aquatopia': 'アクアトピア', 'DisneySea Electric Railway': 'ディズニーシー・エレクトリックレールウェイ', 'Venetian Gondolas': 'ヴェネツィアン・ゴンドラ', 'Fortress Explorations': 'フォートレス・エクスプロレーション', 'Caravan Carousel': 'キャラバンカルーセル', "Jasmine's Flying Carpets": 'ジャスミンのフライングカーペット', "Sinbad's Storybook Voyage": 'シンドバッド・ストーリーブック・ヴォヤッジ', "Flounder's Flying Fish Coaster": 'フランダーのフライングフィッシュコースター', "Scuttle's Scooters": 'スカットルのスクーター', "Jumpin' Jellyfish": 'ジャンピン・ジェリーフィッシュ', 'Blowfish Balloon Race': 'ブローフィッシュ・バルーンレース', 'The Whirlpool': 'ワールプール', "Ariel's Playground": 'アリエルのプレイグラウンド', 'DisneySea Transit Steamer Line': 'ディズニーシー・トランジットスチーマーライン', "Magellan's": 'マゼランズ', 'Ristorante di Canaletto': 'リストランテ・ディ・カナレット', 'Restaurant Sakura': 'レストラン櫻', 'S.S. Columbia Dining Room': 'S.S.コロンビア・ダイニングルーム', 'New York Deli': 'ニューヨーク・デリ', "Zambini Brothers' Ristorante": 'ザンビーニ・ブラザーズ・リストランテ', 'Cape Cod Cook-Off': 'ケープコッド・クックオフ', 'Casbah Food Court': 'カスバ・フードコート', "Sebastian's Calypso Kitchen": 'セバスチャンのカリプソキッチン', 'Vulcania Restaurant': 'ヴォルケイニア・レストラン', 'Queen of Hearts Banquet Hall': 'クイーン・オブ・ハートのバンケットホール', 'Crystal Palace Restaurant': 'クリスタルパレス・レストラン', 'Eastside Cafe': 'イーストサイド・カフェ', 'Center Street Coffeehouse': 'センターストリート・コーヒーハウス', 'Restaurant Hokusai': 'れすとらん北齋', 'Blue Bayou Restaurant': 'ブルーバイユー・レストラン', 'Polynesian Terrace Restaurant': 'ポリネシアンテラス・レストラン', 'Plaza Pavilion Restaurant': 'プラザパビリオン・レストラン', "Grandma Sara's Kitchen": 'グランマ・サラのキッチン', 'Hungry Bear Restaurant': 'ハングリーベア・レストラン', 'Camp Woodchuck Kitchen': 'キャンプ・ウッドチャック・キッチン', 'Tomorrowland Terrace': 'トゥモローランド・テラス', 'Pan Galactic Pizza Port': 'パン・ギャラクティック・ピザ・ポート', "Plazma Ray's Diner": 'プラズマ・レイズ・ダイナー'}

def jp_name(name):
    if not name:
        return '名称不明'
    if name in JP_NAMES:
        return JP_NAMES[name]
    # ThemeParks.wiki側の表記揺れ（’ / '、エリア名の括弧付き等）を吸収
    normalized=name.replace('’', "'").strip()
    if normalized in JP_NAMES:
        return JP_NAMES[normalized]
    aliases=[
        ('Indiana Jones Adventure','インディ・ジョーンズ・アドベンチャー：クリスタルスカルの魔宮'),
        ('Mermaid Lagoon Theater','マーメイドラグーンシアター'),
        ('The Magic Lamp Theater','マジックランプシアター'),
        ('Magic Lamp Theater','マジックランプシアター'),
        ('Turtle Talk','タートル・トーク'),
        ('Big City Vehicles','ビッグシティ・ヴィークル'),
        ('Leonardo Challenge','フォートレス・エクスプロレーション“ザ・レオナルドチャレンジ”'),
        ("Sindbad's Storybook Voyage",'シンドバッド・ストーリーブック・ヴォヤッジ'),
        ('DisneySea Electric Railway','ディズニーシー・エレクトリックレールウェイ'),
        ('DisneySea Transit Steamer Line','ディズニーシー・トランジットスチーマーライン'),
        ('Turtle Talk','タートル・トーク'),
        ('The Magic Lamp Theater','マジックランプシアター'),
        ('Magic Lamp Theater','マジックランプシアター'),
        ('Indiana Jones Adventure','インディ・ジョーンズ・アドベンチャー：クリスタルスカルの魔宮'),
        ('Mermaid Lagoon Theater','マーメイドラグーンシアター'),
        ('Turtle Talk','タートル・トーク'),
    ]
    for key,jp in aliases:
        if key.lower() in normalized.lower():
            # 路線系は取得元の括弧内エリアを残して識別しやすくする
            if '(' in normalized and key.startswith('DisneySea'):
                area=normalized[normalized.find('(')+1:normalized.rfind(')')]
                areas={'American Waterfront':'アメリカンウォーターフロント','Port Discovery':'ポートディスカバリー',
                       'Mediterranean Harbor':'メディテレーニアンハーバー','Lost River Delta':'ロストリバーデルタ'}
                return jp+'（'+areas.get(area,area)+'）'
            return jp
    # 未登録の英語名をそのままUIへ漏らさない。名称マスター更新対象として表示。
    if any('A' <= c <= 'Z' or 'a' <= c <= 'z' for c in normalized):
        return '名称確認中'
    return normalized

CATALOG=[
 {'kind':'スーベニア','name':'スーベニアカップ','price':'+900円','parks':'ランド / シー','period':'2026/9/15〜10/31','menu':'パンプキンムース＆チョコプリン','shops':['スウィートハート・カフェ','ハングリーベア・レストラン','ヒューイ・デューイ・ルーイのグッドタイム・カフェ'],'source':'https://www.tokyodisneyresort.jp/food/4895/'},
 {'kind':'スーベニア','name':'スーベニアプレート','price':'+900円','parks':'ランド / シー','period':'2026/9/15〜10/31','menu':'チョコレートケーキ（ナッツ入り）','shops':['スウィートハート・カフェ','ハングリーベア・レストラン'],'source':'https://www.tokyodisneyresort.jp/food/4896/'},
 {'kind':'スーベニア','name':'スーベニアランチケース','price':'+1,500円','parks':'ランド / シー','period':'2026/9/15〜10/31','menu':'スペシャルセット / ホットドッグセット等','shops':['スウィートハート・カフェ','リフレッシュメントコーナー'],'source':'https://www.tokyodisneyresort.jp/food/4860/'},
 {'kind':'スーベニア','name':'スーベニアプレート','price':'+1,500円','parks':'シー','period':'2026/7/1〜','menu':'シェフのおすすめセット / スモーブローセット / ブラウンソースのミートボールライスセット / ベリーホイップパンケーキ','shops':['アレンデール・ロイヤルバンケット'],'source':'https://www.tokyodisneyresort.jp/food/4739/'},
 {'kind':'スーベニア','name':'スーベニアプレート','price':'+900円','parks':'シー','period':'2026/8/18〜','menu':'ヒュウガナツレアチーズケーキ','shops':['カフェ・ポルトフィーノ','マンマ・ビスコッティーズ・ベーカリー','ホライズンベイ・レストラン'],'source':'https://www.tokyodisneyresort.jp/food/4687/'},
 {'kind':'スーベニア','name':'スーベニアプレート','price':'+900円','parks':'シー','period':'2026/4/14〜2027/3/31','menu':'ミルクティーショートケーキ（ピスタチオ入り）','shops':['ケープコッド・クックオフ'],'source':'https://www.tokyodisneyresort.jp/food/4618/'},
]

GOODS_SEED=[
 {'kind':'グッズ','name':'ショルダーバッグ','price':'¥3,900〜','parks':'ランド / シー','period':'販売中 / 商品により異なる','menu':'バッグ・リュック・小物入れ','shops':['取扱店舗は商品ごとに確認'],'source':'https://www.tokyodisneyresort.jp/tds/goods/list/8084/'},
 {'kind':'グッズ','name':'ぬいぐるみ・ぬいぐるみバッジ','price':'商品により異なる','parks':'ランド / シー','period':'販売中 / 商品により異なる','menu':'ぬいぐるみ・おもちゃ','shops':['取扱店舗は商品ごとに確認'],'source':'https://www.tokyodisneyresort.jp/tds/goods/list/8097/'},
 {'kind':'グッズ','name':'チョコレート・チョコレートクランチ','price':'¥1,000〜','parks':'ランド / シー','period':'販売中 / 商品により異なる','menu':'お菓子・食品','shops':['取扱店舗は商品ごとに確認'],'source':'https://www.tokyodisneyresort.jp/tds/goods/list/8021/'},
 {'kind':'グッズ','name':'マグ・タンブラー・ドリンクボトル','price':'商品により異なる','parks':'ランド / シー','period':'販売中 / 商品により異なる','menu':'食器・生活雑貨','shops':['取扱店舗は商品ごとに確認'],'source':'https://www.tokyodisneyresort.jp/tds/goods/list/8038/'},
 {'kind':'グッズ','name':'ヘアアクセサリー','price':'¥950〜','parks':'ランド / シー','period':'販売中 / 商品により異なる','menu':'ファッションアイテム','shops':['取扱店舗は商品ごとに確認'],'source':'https://www.tokyodisneyresort.jp/tds/goods/list/8033/'},
 {'kind':'グッズ','name':'筆記具・ペンケース','price':'商品により異なる','parks':'ランド / シー','period':'販売中 / 商品により異なる','menu':'文具・ステーショナリー','shops':['取扱店舗は商品ごとに確認'],'source':'https://www.tokyodisneyresort.jp/tds/goods/list/8049/'},
 {'kind':'グッズ','name':'バスグッズ・トイレタリー','price':'¥900〜','parks':'ランド / シー','period':'販売中 / 商品により異なる','menu':'生活雑貨','shops':['取扱店舗は商品ごとに確認'],'source':'https://www.tokyodisneyresort.jp/tds/goods/list/8024/'},
 {'kind':'グッズ','name':'インテリア','price':'商品により異なる','parks':'ランド / シー','period':'販売中 / 商品により異なる','menu':'生活雑貨・インテリア','shops':['取扱店舗は商品ごとに確認'],'source':'https://www.tokyodisneyresort.jp/tds/goods/list/8009/'},
]
CATALOG.extend(GOODS_SEED)


DB='park_live.db'
TDR='https://www.tokyodisneyresort.jp'
refresh_state={'running':False,'last':0,'message':'未更新'}

def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
    c.execute("""create table if not exists local_catalog(
      url text primary key, kind text, park text, name text, price text, place text,
      category text, image text, detail text, updated integer)""")
    c.commit(); return c

def page(url):
    r=requests.get(url,timeout=20,headers={'User-Agent':'Mozilla/5.0 Park-LIVE-Local/1.0'})
    r.raise_for_status()
    return BeautifulSoup(r.text,'html.parser')

def clean_text(v): return re.sub(r'\s+',' ',v or '').strip()
def yen(v):
    m=re.search(r'(?:¥|￥)\s?[\d,]+',v or '')
    return m.group(0).replace(' ','') if m else ''

def save_catalog(x):
    c=db()
    c.execute("""insert into local_catalog(url,kind,park,name,price,place,category,image,detail,updated)
    values(:url,:kind,:park,:name,:price,:place,:category,:image,:detail,:updated)
    on conflict(url) do update set kind=excluded.kind,park=excluded.park,name=excluded.name,
    price=excluded.price,place=excluded.place,category=excluded.category,image=excluded.image,
    detail=excluded.detail,updated=excluded.updated""",x)
    c.commit(); c.close()

def detail(url,fallback=''):
    try:
        s=page(url); h=s.select_one('h1')
        name=clean_text(h.get_text(' ',strip=True)) if h else fallback
        body=clean_text(s.get_text(' ',strip=True))
        og=s.select_one('meta[property="og:image"]')
        image=urljoin(TDR,og.get('content')) if og and og.get('content') else ''
        return name,yen(body),image,body[:420]
    except Exception:
        return fallback,'','',''

def crawl_restaurant_menus(park):
    code='tdl' if park=='LAND' else 'tds'
    menu_pages=set()
    for root in (f'{TDR}/{code}/restaurant/',f'{TDR}/{code}/restaurant/list/'):
        try:
            s=page(root)
            for a in s.select('a[href]'):
                u=urljoin(TDR,a.get('href',''))
                if re.search(fr'/{code}/restaurant/food/\d+/?$',u): menu_pages.add(u)
        except Exception: pass
    for mp in menu_pages:
        try:
            s=page(mp); h=s.select_one('h1')
            restaurant=clean_text(h.get_text(' ',strip=True)) if h else ''
            found={}
            for a in s.select('a[href*="/food/"]'):
                u=urljoin(TDR,a.get('href',''))
                if re.search(r'/food/\d+/?$',u) and u!=mp:
                    t=clean_text(a.get_text(' ',strip=True))
                    if t: found[u]=t
            if found:
                for u,t in found.items():
                    n,p,img,d=detail(u,t.split('¥')[0].strip())
                    save_catalog(dict(url=u,kind='menu',park=park,name=n,price=p or yen(t),
                        place=restaurant,category='メニュー',image=img,detail=d,updated=int(time.time())))
            else:
                # HTML構造が変わっても、価格付きの可視メニュー行は保存する。
                for line in s.get_text('\n',strip=True).splitlines():
                    t=clean_text(line); p=yen(t)
                    if p and len(t)>3:
                        n=t.split('¥')[0].strip()
                        if n:
                            u=mp+'#'+str(abs(hash((restaurant,n))))
                            save_catalog(dict(url=u,kind='menu',park=park,name=n,price=p,
                                place=restaurant,category='メニュー',image='',detail='',updated=int(time.time())))
        except Exception: pass

def crawl_goods(park):
    code='tdl' if park=='LAND' else 'tds'
    roots={f'{TDR}/{code}/shop',f'{TDR}/{code}/goods/'}
    categories=set(roots)
    for root in list(roots):
        try:
            s=page(root)
            for a in s.select('a[href]'):
                u=urljoin(TDR,a.get('href',''))
                if re.search(fr'/{code}/goods/list/\d+/?$',u): categories.add(u)
        except Exception: pass
    products={}
    for cu in categories:
        try:
            s=page(cu)
            for a in s.select('a[href*="/goods/"]'):
                u=urljoin(TDR,a.get('href',''))
                if re.search(r'/goods/\d+/?$',u):
                    products[u]=clean_text(a.get_text(' ',strip=True))
        except Exception: pass
    for u,t in products.items():
        n,p,img,d=detail(u,t.split('¥')[0].strip())
        place=''
        if '販売店舗' in d: place=d.split('販売店舗',1)[1][:150]
        save_catalog(dict(url=u,kind='goods',park=park,name=n,price=p or yen(t),place=place,
            category='グッズ',image=img,detail=d,updated=int(time.time())))

def refresh_catalog():
    if refresh_state['running']: return
    refresh_state['running']=True; refresh_state['message']='更新中'
    try:
        for p in ('LAND','SEA'):
            crawl_restaurant_menus(p)
            crawl_goods(p)
        refresh_state['last']=int(time.time()); refresh_state['message']='更新完了'
    finally:
        refresh_state['running']=False

def fetch(url):
    h=cache.get(url); now=time.time()
    if h and now-h[0]<300:return h[1]
    r=requests.get(url,timeout=15,headers={'User-Agent':'Park-LIVE/1.0'});r.raise_for_status();d=r.json();cache[url]=(now,d);return d
@app.get('/api/{park}/live')
def live(park:str):
    try:
        d=fetch('https://api.themeparks.wiki/v1/entity/'+PARKS.get(park.upper(),PARKS['LAND'])+'/live')
        src=d if isinstance(d,list) else d.get('liveData',d.get('data',[])); out=[]
        for x in src:
            q=x.get('queue') or {}; s=q.get('STANDBY') or q.get('standby') or {}
            out.append({'id':x.get('id'),'name':jp_name(x.get('name','名称不明')),'type':x.get('entityType','ATTRACTION'),'status':x.get('status','UNKNOWN'),'wait':s.get('waitTime'),'updated':x.get('lastUpdated')})
        return {'ok':True,'items':out}
    except Exception as e:return {'ok':False,'items':[],'error':str(e)}
HTML="""<!doctype html><html lang=ja><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1,viewport-fit=cover'><title>Park LIVE</title><style>
*{box-sizing:border-box}body{margin:0;background:linear-gradient(180deg,#fff7fb 0,#f3f8ff 45%,#fffdf6 100%);color:#25304a;font-family:system-ui,-apple-system,sans-serif}.w{max-width:720px;margin:auto;padding:18px 16px 105px}.top{display:flex;justify-content:space-between;align-items:center;gap:12px}.brand{font-size:28px;font-weight:950;letter-spacing:-1px;background:linear-gradient(90deg,#ff5c9a,#7b61ff,#36b8ff);-webkit-background-clip:text;color:transparent}.sub,.meta{font-size:12px;color:#71809d}.seg{background:#fff;padding:4px;border-radius:16px;box-shadow:0 6px 20px #6574a21a}.seg button,.chip{border:0;border-radius:12px;padding:9px 12px;background:transparent;color:#71809d;font-weight:850}.seg .on,.chip.on{background:linear-gradient(135deg,#ff79ae,#8d7cff);color:white;box-shadow:0 5px 14px #8d7cff40}.hero{margin:17px 0;padding:19px;border-radius:25px;background:linear-gradient(135deg,#fff,#f4eaff 48%,#e5f6ff);box-shadow:0 10px 30px #6272a420;border:1px solid #ffffff}.hero h2{margin:0 0 5px;font-size:23px}.chips{display:flex;gap:8px;overflow:auto;margin:12px 0;padding-bottom:3px}.chip{background:#fff;border:1px solid #e4e9f4;white-space:nowrap;box-shadow:0 3px 10px #71809d12}.card{background:#ffffffd9;border:1px solid #fff;border-radius:22px;padding:15px;margin:11px 0;display:grid;grid-template-columns:1fr auto;box-shadow:0 8px 24px #6574a21a;backdrop-filter:blur(8px)}.name{font-weight:900}.wait{font-size:31px;font-weight:950;text-align:right;color:#6958e8}.fav{border:0;background:none;font-size:22px}.state{text-align:center;color:#71809d;padding:34px}.bar{position:fixed;bottom:0;left:0;right:0;background:#ffffffed;border-top:1px solid #e7ebf4;display:flex;justify-content:center;padding:8px 8px calc(8px + env(safe-area-inset-bottom));box-shadow:0 -8px 25px #6574a214;backdrop-filter:blur(12px)}.bar button{width:min(25%,180px);border:0;background:none;color:#8b96ad;padding:7px;font-weight:850;border-radius:15px}.bar .on{color:#735eea;background:#f2edff}.foot{text-align:center;color:#8b96ad;font-size:11px;margin:25px}a{color:#6d5ce7}.modal{display:none;position:fixed;inset:0;background:#f8f6fffa;z-index:20;overflow:auto}.modal.on{display:block}.maphead{position:sticky;top:0;background:#ffffffed;padding:14px 16px;border-bottom:1px solid #e8eaf2;display:flex;justify-content:space-between;align-items:center;z-index:2}.mapgrid{position:relative;width:min(92vw,620px);height:68vh;min-height:520px;margin:18px auto;background:radial-gradient(circle at center,#dff7ff,#f3e9ff 65%,#fff1f6);border:3px solid white;border-radius:34px;overflow:hidden;box-shadow:0 12px 35px #6574a22a}.zone{position:absolute;padding:10px;border:1px solid #ffffff;border-radius:19px;background:#ffffffdd;text-align:center;font-size:12px;font-weight:900;box-shadow:0 6px 16px #6574a226}.pin{display:inline-block;margin:4px 2px;padding:5px 7px;border-radius:999px;background:linear-gradient(135deg,#ff78aa,#8b78ff);color:white;font-size:10px}.close{border:0;background:#eee9ff;color:#6253d5;border-radius:12px;padding:9px 13px;font-weight:800}#q{width:100%;padding:14px 16px!important;border-radius:17px!important;border:1px solid #e4e8f2!important;background:white!important;color:#25304a!important;font-size:16px;box-shadow:0 7px 20px #6574a216;outline:none}#mapbtn{color:#6d5ce7!important;font-weight:850}.badge{display:inline-block;padding:4px 8px;border-radius:999px;background:#fff0f6;color:#e34f89;font-size:11px;font-weight:850;margin-bottom:7px}
.productrow{display:grid!important;grid-template-columns:105px 1fr!important;gap:13px}.productimg{width:105px;height:105px;border-radius:17px;object-fit:cover;background:#f1eaff}.imgph{display:grid;place-items:center;font-size:30px}</style></head><body><div class=w><div class=top><div><div class=brand>Park LIVE</div><div class=sub id=stamp>今日のパークを、もっと楽しく ✨</div></div><div><div class=seg><button id=LAND class=on>ランド</button><button id=SEA>シー</button></div><button id=mapbtn style='display:block;width:100%;margin-top:7px;border:0;background:none;color:#93c5fd;font-size:12px'>🗺️ パークマップ</button></div></div><div class=hero><h2 id=title>アトラクション</h2><div class=sub>待ち時間をサクッと比較して、次の行動を決めよう 🎡</div><div class=meta id=sum>取得中…</div></div><div id=searchbox style='display:none;margin:12px 0'><input id=q placeholder='料理・商品・店舗名で検索' style='width:100%;padding:13px;border-radius:12px;border:1px solid #334155;background:#111827;color:white;font-size:16px'></div><div id=catalogActions style='display:none;gap:8px;margin:10px 0'><button id=refreshCatalog class='chip on'>↻ 公式公開情報を端末内へ更新</button></div><div class=chips><button class='chip on' data-f=all>すべて</button><button class=chip data-f=30>30分以下</button><button class=chip data-f=fav>♥ お気に入り</button></div><div id=list class=state>読み込み中…</div><div class=foot>メニュー・スーベニア・グッズを横断検索できます。<br>非公式アプリです。<a href='https://www.themeparks.wiki/' target=_blank>Powered by ThemeParks.wiki</a></div></div><div id=mapmodal class=modal><div class=maphead><b id=maptitle>Park LIVE マップ</b><button id=mapclose class=close>閉じる</button></div><div id=mapgrid class=mapgrid></div><div class=foot>位置関係を把握するためのPark LIVE簡易マップです。正確な現在地ナビではありません。</div></div><div class=bar><button class=on data-tab=PLAY>🎢<br>遊ぶ</button><button data-tab=EAT>🍽️<br>食べる</button><button data-tab=SHOP>🎁<br>買う</button><button data-tab=HOME>🏠<br>ホーム</button></div><script>
let park='LAND',tab='PLAY',filter='all',items=[],catalog=[],favs=new Set(JSON.parse(localStorage.getItem('plf')||'[]'));const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];function ok(x){let t=(x.type||'').toUpperCase();return tab==='HOME'||t===(tab==='PLAY'?'ATTRACTION':tab==='EAT'?'RESTAURANT':'SHOP')}function esc(s){let d=document.createElement('div');d.textContent=s;return d.innerHTML}function jpStatus(s){return ({OPERATING:'運営中',DOWN:'一時休止',CLOSED:'休止中',REFURBISHMENT:'休止中',UNKNOWN:'状況不明'})[String(s||'UNKNOWN').toUpperCase()]||'状況不明'}function render(){let a=items.filter(ok);if(tab==='HOME')a=a.filter(x=>favs.has(x.id));if(filter==='30')a=a.filter(x=>x.wait!=null&&x.wait<=30);if(filter==='fav')a=a.filter(x=>favs.has(x.id));a.sort((x,y)=>(x.wait??9999)-(y.wait??9999));$('#title').textContent=tab==='HOME'?'お気に入り':tab==='PLAY'?'アトラクション':tab==='EAT'?'レストラン':'ショップ';$('#sum').textContent=(park==='LAND'?'ランド':'シー')+'・'+a.length+'件 / 約5分ごとに更新';if(!a.length){$('#list').className='state';$('#list').textContent=tab==='SHOP'?'ショップのライブ情報は取得元にありません。推測表示はしません。':'表示できる情報がありません。';return}$('#list').className='';$('#list').innerHTML=a.map(x=>`<div class=card><div><div class=name><button class=fav data-id='${x.id}'>${favs.has(x.id)?'♥':'♡'}</button> ${esc(x.name)}</div><div class=meta>${jpStatus(x.status)} ・ ${x.updated?new Date(x.updated).toLocaleTimeString('ja-JP',{hour:'2-digit',minute:'2-digit'}):'時刻不明'}</div></div><div><div class=wait>${x.wait??'–'}</div><div class=meta>${x.wait==null?'待ち時間不明':'分'}</div></div></div>`).join('');$$('.fav').forEach(b=>b.onclick=()=>{favs.has(b.dataset.id)?favs.delete(b.dataset.id):favs.add(b.dataset.id);localStorage.setItem('plf',JSON.stringify([...favs]));render()})}const STORE_AREAS={"スウィートハート・カフェ": "ワールドバザール", "ハングリーベア・レストラン": "ウエスタンランド", "ヒューイ・デューイ・ルーイのグッドタイム・カフェ": "トゥーンタウン", "リフレッシュメントコーナー": "ワールドバザール", "アレンデール・ロイヤルバンケット": "ファンタジースプリングス", "カフェ・ポルトフィーノ": "メディテレーニアンハーバー", "マンマ・ビスコッティーズ・ベーカリー": "メディテレーニアンハーバー", "ホライズンベイ・レストラン": "ポートディスカバリー", "ケープコッド・クックオフ": "アメリカンウォーターフロント"};
const ZONES={
LAND:[['ワールドバザール',40,8],['アドベンチャーランド',8,28],['ウエスタンランド',10,50],['クリッターカントリー',20,72],['ファンタジーランド',48,54],['トゥーンタウン',72,38],['トゥモローランド',72,14]],
SEA:[['メディテレーニアンハーバー',38,8],['アメリカンウォーターフロント',8,27],['ポートディスカバリー',8,55],['ロストリバーデルタ',25,73],['ファンタジースプリングス',52,70],['アラビアンコースト',72,54],['マーメイドラグーン',68,35],['ミステリアスアイランド',43,35]]
};
function showMap(focus=''){let z=ZONES[park];$('#maptitle').textContent=(park==='LAND'?'東京ディズニーランド':'東京ディズニーシー')+'｜Park LIVEマップ';let stores=[...new Set(catalog.flatMap(x=>x.shops||[]))];$('#mapgrid').innerHTML=z.map(([n,x,y])=>{let ss=stores.filter(v=>STORE_AREAS[v]===n);return `<div class=zone style="left:${x}%;top:${y}%;${focus&&ss.includes(focus)?'outline:3px solid white':''}"><div>${n}</div>${ss.map(v=>`<span class=pin>${esc(v)}</span>`).join('')}</div>`}).join('');$('#mapmodal').classList.add('on')}
function renderCatalog(){let q=($('#q')?.value||'').trim().toLowerCase();let a=catalog.filter(x=>tab==='SHOP'?(x.kind==='goods'||x.kind==='グッズ'):(x.kind==='menu'||x.kind==='スーベニア')).filter(x=>!q||([x.kind,x.name,x.parks,x.period,x.menu,x.place,x.detail,...(x.shops||[])].join(' ').toLowerCase().includes(q)));$('#title').textContent=tab==='EAT'?'🍴 メニューを探す':'🎁 グッズを探す';$('#sum').textContent=a.length+'件 / 公式公開情報ベース';if(!a.length){$('#list').className='state';$('#list').textContent='該当する公開情報がありません。';return}$('#list').className='';$('#list').innerHTML=a.map(x=>{let isdb=!!x.url;let name=x.name||'';let price=x.price||'';let place=x.place||(x.shops||[]).join(' / ');let url=x.url||x.source||'';let image=x.image||'';return `<div class="card productrow">${image?`<img class=productimg loading=lazy src="${esc(image)}">`:`<div class="productimg imgph">${tab==='SHOP'?'🎁':'🍴'}</div>`}<div><div class=badge>${tab==='SHOP'?'グッズ':'メニュー'}</div><div class=name>${esc(name)}</div><div style="font-weight:900;margin-top:5px">${esc(price)}</div><div class=meta style="margin-top:6px">${esc(place)}</div>${x.detail?`<div class=meta>${esc(x.detail.slice(0,120))}</div>`:''}<div style="margin-top:8px">${url?`<a href="${esc(url.split('#')[0])}" target=_blank>公式詳細</a>`:''}</div></div></div>`}).join('')}
async function loadCatalog(){try{let d=await(await fetch('/api/catalog?park='+park)).json();catalog=d.items||[];$('#sum').textContent=(d.refresh&&d.refresh.running?'更新中… ': '')+catalog.length+'件';renderCatalog()}catch(e){$('#list').textContent='検索データを取得できませんでした。'}}
async function load(){$('#list').className='state';$('#list').textContent='読み込み中…';try{let d=await(await fetch('/api/'+park+'/live')).json();items=d.items||[];$('#stamp').textContent=d.ok?'更新 '+new Date().toLocaleTimeString('ja-JP',{hour:'2-digit',minute:'2-digit'}):'取得エラー';render()}catch(e){$('#list').textContent='データを取得できませんでした。'}}$$('.seg button').forEach(b=>b.onclick=()=>{park=b.id;$$('.seg button').forEach(x=>x.classList.toggle('on',x.id===park));load()});$$('.chip').forEach(b=>b.onclick=()=>{filter=b.dataset.f;$$('.chip').forEach(x=>x.classList.toggle('on',x===b));render()});$$('.bar button').forEach(b=>b.onclick=()=>{tab=b.dataset.tab;$$('.bar button').forEach(x=>x.classList.toggle('on',x===b));let cat=tab==='EAT'||tab==='SHOP';$('#searchbox').style.display=cat?'block':'none';$('#catalogActions').style.display=cat?'flex':'none';$('.chips').style.display=cat?'none':'flex';cat?loadCatalog():render()});$('#q').oninput=()=>renderCatalog();$('#refreshCatalog').onclick=async()=>{if(!confirm('公式Webで公開されているメニュー・グッズを、この端末用カタログへ更新します。よろしいですか？'))return;await fetch('/api/catalog/refresh',{method:'POST'});$('#refreshCatalog').textContent='更新中…';let t=setInterval(async()=>{let d=await(await fetch('/api/catalog?park='+park)).json();if(!d.refresh?.running){clearInterval(t);$('#refreshCatalog').textContent='↻ 公式公開情報を端末内へ更新';catalog=d.items||[];renderCatalog()}},2500)};$('#mapbtn').onclick=()=>showMap();$('#mapclose').onclick=()=>$('#mapmodal').classList.remove('on');load();
</script></body></html>"""

@app.get('/api/catalog')
def get_catalog(q:str='',park:str='',kind:str=''):
    c=db(); sql='select * from local_catalog where 1=1'; args=[]
    if park: sql+=' and park=?'; args.append(park)
    if kind: sql+=' and kind=?'; args.append(kind)
    if q:
        sql+=' and (name like ? or place like ? or detail like ?)'
        args += ['%'+q+'%']*3
    sql+=' order by updated desc,name limit 2000'
    rows=[dict(x) for x in c.execute(sql,args).fetchall()]; c.close()
    # Until first local refresh, retain the existing seed so the screen is never empty.
    if not rows and not q:
        rows=CATALOG
    return {'ok':True,'items':rows,'refresh':refresh_state}

@app.post('/api/catalog/refresh')
def start_refresh():
    import threading
    if not refresh_state['running']:
        threading.Thread(target=refresh_catalog,daemon=True).start()
    return {'ok':True,'refresh':refresh_state}

@app.get('/',response_class=HTMLResponse)
def home():return HTML
