import asyncio
import os
import json
import edge_tts
import subprocess

# 対談スクリプト定義 (Host A: Nanami, Host B: Keita)
DIALOGUE = [
    {
        "speaker": "nanami",
        "name": "Nanami (ナビゲーター)",
        "voice": "ja-JP-NanamiNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "slide": 0,
        "text": "さあ、今回は2026年シルバーウィークの『伊豆2泊3日 家族旅行のしおり』をじっくり読み解いていきましょう！"
    },
    {
        "speaker": "keita",
        "name": "Keita (コメンテーター)",
        "voice": "ja-JP-KeitaNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "slide": 0,
        "text": "いやー、この旅のしおり、隅々まで計画されていて本当に素晴らしいですね！伊東から伊豆高原まで、温泉に絶景にアクティビティと、家族みんなが楽しめる黄金ルートになってます。"
    },
    {
        "speaker": "nanami",
        "name": "Nanami (ナビゲーター)",
        "voice": "ja-JP-NanamiNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "slide": 1,
        "text": "まずは1日目！伊東の『サンハトヤ』に宿泊ですね。『伊東に行くならハトヤ』でおなじみですが、注目はなんといっても海底温泉です！"
    },
    {
        "speaker": "keita",
        "name": "Keita (コメンテーター)",
        "voice": "ja-JP-KeitaNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "slide": 1,
        "text": "そうなんですよ！巨大水槽でお魚やウミガメが泳ぐ姿を見ながら温泉に入れるという、まるで水族館のようなお風呂。子どもたちも大興奮間違いなしですし、オーシャンビューの海鮮ディナーバイキングも楽しみですね。"
    },
    {
        "speaker": "nanami",
        "name": "Nanami (ナビゲーター)",
        "voice": "ja-JP-NanamiNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "slide": 2,
        "text": "そして2日目は伊豆高原へ移動して、『伊豆ぐらんぱる公園』を大満喫！ジップラインや実物大の動く恐竜エリア『ディノエイジウォーク』など、思いっきり体を動かせます。"
    },
    {
        "speaker": "keita",
        "name": "Keita (コメンテーター)",
        "voice": "ja-JP-KeitaNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "slide": 2,
        "text": "遊び疲れたあとの2泊目がまた最高で、『杜の湯 きらの里』。日本の原風景のような里山が広がるお宿で、3つの無料貸切露天風呂や、夜のお楽しみ『夜泣きそば』の無料サービスまであるんです。"
    },
    {
        "speaker": "nanami",
        "name": "Nanami (ナビゲーター)",
        "voice": "ja-JP-NanamiNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "slide": 3,
        "text": "そして最終日の3日目は、城ヶ崎海岸の『橋立つり橋』へ！高さ18メートルの吊り橋から見下ろす断崖絶壁と太平洋の大パノラマは、スリルと感動の絶景ですね！"
    },
    {
        "speaker": "keita",
        "name": "Keita (コメンテーター)",
        "voice": "ja-JP-KeitaNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "slide": 3,
        "text": "散策のあとは伊豆高原駅から『特急踊り子62号』で新宿まで直通！16時09分発、全席指定席で予約番号E80864もバッチリ確保済み。シルバーウィークの渋滞知らずで、座ったままゆったり帰れるのが完璧です。"
    },
    {
        "speaker": "nanami",
        "name": "Nanami (ナビゲーター)",
        "voice": "ja-JP-NanamiNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "slide": 4,
        "text": "まさに移動も宿も遊びも抜かりのない、パーフェクトな2泊3日プランですね！"
    },
    {
        "speaker": "keita",
        "name": "Keita (コメンテーター)",
        "voice": "ja-JP-KeitaNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "slide": 4,
        "text": "家族みんなの最高の思い出になること間違いなしです。それでは皆さん、気をつけて最高の伊豆旅行に行ってらっしゃい！"
    }
]

SLIDES_DATA = [
    {
        "id": 0,
        "tag": "OVERVIEW",
        "title": "2026年 シルバーウィーク 伊豆家族旅行 2泊3日",
        "subtitle": "NotebookLM スタイル AIディープダイブ解説",
        "highlights": [
            "伊東〜伊豆高原を巡るファミリー黄金ルート",
            "温泉・テーマパーク・大自然・グルメを網羅",
            "往復快適アクセス＆全席指定席確保済み"
        ],
        "color": "#0288d1"
    },
    {
        "id": 1,
        "tag": "DAY 1",
        "title": "1日目：伊東温泉 サンハトヤ & 海底温泉",
        "subtitle": "お魚が泳ぐ水族館のような海底大浴場とお魚ディナー",
        "highlights": [
            "『伊東に行くならハトヤ』名物の海底温泉千石風呂",
            "ウミガメや色とりどりの魚が泳ぐ巨大水槽",
            "相模湾を望むオーシャンビュー＆海鮮バイキング"
        ],
        "color": "#00897b"
    },
    {
        "id": 2,
        "tag": "DAY 2",
        "title": "2日目：伊豆ぐらんぱる公園 & 杜の湯 きらの里",
        "subtitle": "大迫力恐竜アクティビティと里山の癒やし温泉",
        "highlights": [
            "ぐらんぱる公園：実物大恐竜ディノエイジ＆ジップライン",
            "きらの里：里山風情が広がる広大な敷地と源泉かけ流し",
            "3つの無料貸切露天風呂＆名物『夜泣きそば』"
        ],
        "color": "#ea580c"
    },
    {
        "id": 3,
        "tag": "DAY 3",
        "title": "3日目：橋立つり橋 & 特急踊り子62号",
        "subtitle": "城ヶ崎海岸の絶景スリルと渋滞知らずの特急帰路",
        "highlights": [
            "高さ18m！海の上に架かる『橋立つり橋』と断崖絶壁",
            "伊豆高原駅 16:09発 特急踊り子62号（新宿行）",
            "全席指定席（予約番号: E80864）でゆったり快適帰宅"
        ],
        "color": "#7e22ce"
    },
    {
        "id": 4,
        "tag": "SUMMARY",
        "title": "旅のまとめ：家族みんなが笑顔になる完璧な旅程",
        "subtitle": "最高の2026年シルバーウィークをお過ごしください！",
        "highlights": [
            "子供も大人も大満足のバランス抜群プラン",
            "移動ストレスを最小限に抑えたスマートな設計",
            "準備万端！最高の伊豆家族旅行へ出発！"
        ],
        "color": "#0288d1"
    }
]

async def generate_speech_files():
    os.makedirs("assets/audio", exist_ok=True)
    os.makedirs("assets/video", exist_ok=True)
    
    metadata = []
    current_time = 0.0
    
    for i, item in enumerate(DIALOGUE):
        filename = f"assets/audio/part_{i:02d}_{item['speaker']}.mp3"
        print(f"Generating [{i+1}/{len(DIALOGUE)}] {item['name']}: {item['text'][:20]}...")
        
        communicate = edge_tts.Communicate(
            text=item['text'],
            voice=item['voice'],
            rate=item['rate'],
            pitch=item['pitch']
        )
        await communicate.save(filename)
        
        # 音声の長さを ffprobe で取得
        cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{filename}"'
        res = subprocess.check_output(cmd, shell=True).decode().strip()
        duration = float(res)
        
        metadata.append({
            "index": i,
            "speaker": item["speaker"],
            "name": item["name"],
            "text": item["text"],
            "slide": item["slide"],
            "filename": filename,
            "start": round(current_time, 2),
            "duration": round(duration, 2),
            "end": round(current_time + duration + 0.35, 2)
        })
        current_time += duration + 0.35

    # メタデータを保存
    with open("assets/audio/dialogue_metadata.json", "w", encoding="utf-8") as f:
        json.dump({
            "total_duration": round(current_time, 2),
            "slides": SLIDES_DATA,
            "dialogue": metadata
        }, f, ensure_ascii=False, indent=2)
        
    print(f"\nAll {len(DIALOGUE)} parts generated! Total duration: {current_time:.1f}s")
    
    # 音声の結合
    # 各クリップの間に0.35秒の無音を入れて結合するために、wav変換またはフィルターグラフ結合を行う
    filter_complex = []
    inputs = []
    for i, m in enumerate(metadata):
        inputs.extend(["-i", m["filename"]])
    
    output_mp3 = "assets/audio/notebooklm_overview.mp3"
    
    # concat demuxer用のリストファイル作成
    # 0.35sの無音mp3を作成
    silence_file = "assets/audio/silence.mp3"
    subprocess.run(f'ffmpeg -y -f lavfi -i anullsrc=r=24000:cl=mono -t 0.35 -q:a 9 -acodec libmp3lame "{silence_file}"', shell=True, check=True)
    
    concat_list_path = "assets/audio/concat_list.txt"
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for m in metadata:
            abs_audio = os.path.abspath(m["filename"]).replace("\\", "/")
            abs_silence = os.path.abspath(silence_file).replace("\\", "/")
            f.write(f"file '{abs_audio}'\n")
            f.write(f"file '{abs_silence}'\n")
            
    cmd_concat = f'ffmpeg -y -f concat -safe 0 -i "{concat_list_path}" -c:a libmp3lame -b:a 192k "{output_mp3}"'
    subprocess.run(cmd_concat, shell=True, check=True)
    print(f"Full audio combined into {output_mp3}")

if __name__ == "__main__":
    asyncio.run(generate_speech_files())
