import json
import math
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

WIDTH, HEIGHT = 1280, 720
FPS = 15
FONT_PATH_BOLD = "C:/Windows/Fonts/meiryob.ttc"
FONT_PATH_REG = "C:/Windows/Fonts/meiryo.ttc"

with open("assets/audio/dialogue_metadata.json", "r", encoding="utf-8") as f:
    META = json.load(f)

TOTAL_DURATION = META["total_duration"]
SLIDES = {s["id"]: s for s in META["slides"]}
DIALOGUE = META["dialogue"]

font_title = ImageFont.truetype(FONT_PATH_BOLD, 22)
font_tag = ImageFont.truetype(FONT_PATH_BOLD, 13)
font_photo_title = ImageFont.truetype(FONT_PATH_BOLD, 22)
font_photo_sub = ImageFont.truetype(FONT_PATH_REG, 14)
font_highlight = ImageFont.truetype(FONT_PATH_REG, 15)
font_highlight_bold = ImageFont.truetype(FONT_PATH_BOLD, 15)
font_speaker_name = ImageFont.truetype(FONT_PATH_BOLD, 17)
font_speaker_role = ImageFont.truetype(FONT_PATH_REG, 12)
font_caption = ImageFont.truetype(FONT_PATH_BOLD, 20)
font_small = ImageFont.truetype(FONT_PATH_REG, 13)
font_time = ImageFont.truetype(FONT_PATH_BOLD, 14)

# アバター画像の読み込み & 円形クリップ
def load_circular_avatar(path, size):
    if not os.path.exists(path):
        return None
    raw = Image.open(path).convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, size, size), fill=255)
    output = ImageOps.fit(raw, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    return output

avatar_nanami_img = load_circular_avatar("assets/images/avatar_nanami.jpg", 66)
avatar_keita_img = load_circular_avatar("assets/images/avatar_keita.jpg", 66)

# スポット写真マップ
SPOT_IMAGES = {
    0: "assets/images/spot_odoriko.jpg",
    1: "assets/images/spot_sunhatoya.jpg",
    2: "assets/images/spot_granpal.jpg",
    3: "assets/images/spot_tsuribashi.jpg",
    4: "assets/images/spot_kiranosato.jpg"
}

# 各パート（10ダイアログ）ごとのベース静止画を事前作成
PART_BACKGROUNDS = {}

def draw_rounded_rect(draw, bbox, radius, fill=None, outline=None, width=1):
    x0, y0, x1, y1 = bbox
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)

for dlg in DIALOGUE:
    speaker = dlg["speaker"]
    current_slide = SLIDES[dlg["slide"]]
    photo_path = SPOT_IMAGES.get(current_slide["id"], "assets/images/spot_odoriko.jpg")
    
    # 1. アンビエントぼかし背景
    if os.path.exists(photo_path):
        bg_raw = Image.open(photo_path).convert("RGB").resize((WIDTH, HEIGHT), Image.Resampling.BILINEAR)
        bg_blurred = bg_raw.filter(ImageFilter.GaussianBlur(35))
        # 暗くする (暗色レイヤーを乗算)
        darkener = Image.new("RGB", (WIDTH, HEIGHT), (12, 18, 32))
        img = Image.blend(bg_blurred, darkener, 0.72)
    else:
        img = Image.new("RGB", (WIDTH, HEIGHT), (12, 18, 32))
        
    draw = ImageDraw.Draw(img)
    
    # 2. Header Bar
    draw_rounded_rect(draw, (24, 16, WIDTH - 24, 68), 12, fill=(15, 23, 42, 220), outline=(51, 65, 85), width=1)
    draw_rounded_rect(draw, (36, 26, 185, 56), 6, fill=(2, 136, 209))
    draw.text((46, 32), "NOTEBOOKLM AI", font=font_tag, fill=(255, 255, 255))
    draw.text((200, 29), "伊豆2泊3日 家族旅行のしおり - ビジュアル音声解説", font=font_title, fill=(241, 245, 249))
    
    # 3. 左側: ホストカード
    # Host A: Nanami
    is_nanami = (speaker == "nanami")
    box_a_fill = (15, 23, 42) if not is_nanami else (12, 38, 68)
    box_a_border = (51, 65, 85) if not is_nanami else (56, 189, 248)
    draw_rounded_rect(draw, (24, 82, 340, 222), 14, fill=box_a_fill, outline=box_a_border, width=2 if is_nanami else 1)
    
    if avatar_nanami_img:
        # アバター描画
        img.paste(avatar_nanami_img, (40, 100), avatar_nanami_img)
        # 外枠
        draw.ellipse((40, 100, 106, 166), outline=(56, 189, 248) if is_nanami else (100, 116, 139), width=2)
    
    draw.text((120, 102), "Nanami", font=font_speaker_name, fill=(255, 255, 255))
    draw.text((120, 126), "AI ナビゲーター", font=font_speaker_role, fill=(148, 163, 184))
    status_a_text = "● SPEAKING" if is_nanami else "○ LISTENING"
    status_a_color = (56, 189, 248) if is_nanami else (100, 116, 139)
    draw.text((120, 146), status_a_text, font=font_small, fill=status_a_color)
    
    # Host B: Keita
    is_keita = (speaker == "keita")
    box_b_fill = (15, 23, 42) if not is_keita else (48, 25, 18)
    box_b_border = (51, 65, 85) if not is_keita else (251, 146, 60)
    draw_rounded_rect(draw, (24, 234, 340, 374), 14, fill=box_b_fill, outline=box_b_border, width=2 if is_keita else 1)
    
    if avatar_keita_img:
        img.paste(avatar_keita_img, (40, 252), avatar_keita_img)
        draw.ellipse((40, 252, 106, 318), outline=(251, 146, 60) if is_keita else (100, 116, 139), width=2)
        
    draw.text((120, 254), "Keita", font=font_speaker_name, fill=(255, 255, 255))
    draw.text((120, 278), "AI コメンテーター", font=font_speaker_role, fill=(148, 163, 184))
    status_b_text = "● SPEAKING" if is_keita else "○ LISTENING"
    status_b_color = (251, 146, 60) if is_keita else (100, 116, 139)
    draw.text((120, 298), status_b_text, font=font_small, fill=status_b_color)
    
    # 左下ミニ進行ルート
    draw_rounded_rect(draw, (24, 386, 340, 526), 12, fill=(15, 23, 42), outline=(51, 65, 85), width=1)
    draw.text((38, 396), "◆ 旅程ハイライト", font=font_speaker_name, fill=(226, 232, 240))
    routes = [
        ("1日目", "サンハトヤ（海底温泉）", current_slide["id"] == 1),
        ("2日目", "ぐらんぱる ➔ きらの里", current_slide["id"] == 2),
        ("3日目", "橋立つり橋 ➔ 踊り子62号", current_slide["id"] == 3),
    ]
    for idx, (day_lbl, route_txt, is_curr) in enumerate(routes):
        ry = 428 + idx * 30
        bullet_col = (56, 189, 248) if is_curr else (100, 116, 139)
        draw.text((38, ry), "▶" if is_curr else "・", font=font_small, fill=bullet_col)
        draw.text((54, ry), f"{day_lbl}: {route_txt}", font=font_small, fill=(255, 255, 255) if is_curr else (148, 163, 184))

    # 4. 右側: スライドエリア (大画面フォトフレーム + ハイライト)
    draw_rounded_rect(draw, (358, 82, WIDTH - 24, 526), 16, fill=(15, 23, 42), outline=(51, 65, 85), width=1)
    
    # 写真の配置 (横 870 x 縦 260)
    photo_w, photo_h = 874, 255
    photo_x, photo_y = 370, 94
    
    if os.path.exists(photo_path):
        photo_raw = Image.open(photo_path).convert("RGB")
        photo_fitted = ImageOps.fit(photo_raw, (photo_w, photo_h), centering=(0.5, 0.5))
        
        # 角丸マスク
        photo_mask = Image.new("L", (photo_w, photo_h), 0)
        draw_pmask = ImageDraw.Draw(photo_mask)
        draw_pmask.rounded_rectangle([0, 0, photo_w, photo_h], radius=12, fill=255)
        
        # 写真の上に下部グラデーションオーバーレイを作成（文字を読みやすく）
        grad = Image.new("RGBA", (photo_w, photo_h), (0, 0, 0, 0))
        draw_grad = ImageDraw.Draw(grad)
        for gy in range(photo_h - 100, photo_h):
            alpha = int(((gy - (photo_h - 100)) / 100) * 210)
            draw_grad.line([(0, gy), (photo_w, gy)], fill=(15, 23, 42, alpha))
            
        photo_composite = Image.alpha_composite(photo_fitted.convert("RGBA"), grad)
        img.paste(photo_composite, (photo_x, photo_y), photo_mask)
        
        # 写真枠線
        draw.rounded_rectangle([photo_x, photo_y, photo_x + photo_w, photo_y + photo_h], radius=12, outline=(71, 85, 105), width=1)
    
    # 写真上のタグバッジ
    tag_bg = (2, 136, 209)
    if current_slide["id"] == 1: tag_bg = (0, 137, 123)
    elif current_slide["id"] == 2: tag_bg = (234, 88, 12)
    elif current_slide["id"] == 3: tag_bg = (126, 34, 206)
    
    draw_rounded_rect(draw, (photo_x + 16, photo_y + 16, photo_x + 110, photo_y + 44), 6, fill=tag_bg)
    draw.text((photo_x + 28, photo_y + 22), current_slide["tag"], font=font_tag, fill=(255, 255, 255))
    
    # 写真下のタイトル & サブタイトル
    draw.text((photo_x + 18, photo_y + photo_h - 68), current_slide["title"], font=font_photo_title, fill=(255, 255, 255))
    draw.text((photo_x + 18, photo_y + photo_h - 36), current_slide["subtitle"], font=font_photo_sub, fill=(203, 213, 225))
    
    # スライド下部: 3つのハイライトポイント（3分割カード）
    card_y = photo_y + photo_h + 14
    card_w = (photo_w - 20) // 3
    card_h = 135
    
    for h_idx, hl_text in enumerate(current_slide["highlights"]):
        cx = photo_x + h_idx * (card_w + 10)
        draw_rounded_rect(draw, (cx, card_y, cx + card_w, card_y + card_h), 10, fill=(24, 34, 53), outline=(51, 65, 85), width=1)
        
        # 丸番号
        draw.ellipse((cx + 12, card_y + 12, cx + 38, card_y + 38), fill=tag_bg)
        draw.text((cx + 20, card_y + 14), str(h_idx + 1), font=font_highlight_bold, fill=(255, 255, 255))
        
        # テキスト（折り返し）
        words = hl_text
        if len(words) > 13:
            draw.text((cx + 12, card_y + 48), words[:13], font=font_highlight, fill=(241, 245, 249))
            draw.text((cx + 12, card_y + 72), words[13:26], font=font_highlight, fill=(241, 245, 249))
            if len(words) > 26:
                draw.text((cx + 12, card_y + 96), words[26:], font=font_highlight, fill=(241, 245, 249))
        else:
            draw.text((cx + 12, card_y + 54), words, font=font_highlight, fill=(241, 245, 249))

    # 5. 下部: 字幕テロップボックス
    draw_rounded_rect(draw, (24, 540, WIDTH - 24, 700), 14, fill=(15, 23, 42), outline=(51, 65, 85), width=1)
    
    spk_tag_col = (2, 136, 209) if speaker == "nanami" else (234, 88, 12)
    spk_tag_name = "Nanami" if speaker == "nanami" else "Keita"
    draw_rounded_rect(draw, (42, 555, 128, 587), 6, fill=spk_tag_col)
    draw.text((54, 560), spk_tag_name, font=font_tag, fill=(255, 255, 255))
    
    text = dlg["text"]
    if len(text) > 42:
        draw.text((142, 555), text[:42], font=font_caption, fill=(255, 255, 255))
        draw.text((142, 587), text[42:], font=font_caption, fill=(255, 255, 255))
    else:
        draw.text((142, 563), text, font=font_caption, fill=(255, 255, 255))
        
    PART_BACKGROUNDS[dlg["index"]] = img

def draw_wave_bars(draw, cx, cy, count, active, t, color):
    if not active:
        for i in range(count):
            bx = cx + (i - count//2) * 5
            h = 3
            draw.rectangle([bx-1, cy-h, bx+1, cy+h], fill=(71, 85, 105))
    else:
        for i in range(count):
            bx = cx + (i - count//2) * 5
            phase = t * 12 + i * 0.85
            h = int(5 + math.sin(phase) * 9 + math.cos(phase * 1.6) * 5)
            h = max(2, min(20, h))
            draw.rectangle([bx-1, cy-h, bx+1, cy+h], fill=color)

def get_dlg_at(t):
    for d in DIALOGUE:
        if d["start"] <= t <= d["end"]:
            return d
    for d in reversed(DIALOGUE):
        if t >= d["start"]:
            return d
    return DIALOGUE[0]

def render_frame_fast(t):
    dlg = get_dlg_at(t)
    base = PART_BACKGROUNDS[dlg["index"]].copy()
    draw = ImageDraw.Draw(base)
    
    is_nanami = (dlg["speaker"] == "nanami")
    is_keita = (dlg["speaker"] == "keita")
    
    draw_wave_bars(draw, 280, 154, 8, is_nanami, t, (56, 189, 248))
    draw_wave_bars(draw, 280, 306, 8, is_keita, t, (251, 146, 60))
    
    # Progress bar
    bar_x0, bar_y = 42, 648
    bar_w = WIDTH - 240
    progress = min(1.0, max(0.0, t / TOTAL_DURATION))
    
    draw.rounded_rectangle([bar_x0, bar_y, bar_x0 + bar_w, bar_y + 8], radius=4, fill=(40, 53, 79))
    if progress > 0:
        draw.rounded_rectangle([bar_x0, bar_y, bar_x0 + int(bar_w * progress), bar_y + 8], radius=4, fill=(56, 189, 248))
        draw.ellipse((bar_x0 + int(bar_w * progress) - 6, bar_y - 3, bar_x0 + int(bar_w * progress) + 6, bar_y + 11), fill=(255, 255, 255))
        
    cur_min, cur_sec = int(t // 60), int(t % 60)
    tot_min, tot_sec = int(TOTAL_DURATION // 60), int(TOTAL_DURATION % 60)
    time_str = f"{cur_min:02d}:{cur_sec:02d} / {tot_min:02d}:{tot_sec:02d}"
    draw.text((bar_x0 + bar_w + 18, bar_y - 4), time_str, font=font_time, fill=(148, 163, 184))
    
    return base

def main():
    output_video = "assets/video/izu_trip_audio_overview.mp4"
    audio_file = "assets/audio/notebooklm_overview.mp3"
    
    total_frames = int(TOTAL_DURATION * FPS)
    print(f"Fast rendering visual video: {total_frames} frames ({TOTAL_DURATION:.1f}s @ {FPS}fps)...")
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-i", audio_file,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_video
    ]
    
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    
    for f in range(total_frames):
        t = f / FPS
        img = render_frame_fast(t)
        process.stdin.write(img.tobytes())
        
        if f % (FPS * 15) == 0 or f == total_frames - 1:
            print(f"Rendered frame {f}/{total_frames} ({f/total_frames*100:.1f}%)")
            
    process.stdin.close()
    process.wait()
    print(f"\nSuccessfully generated visual video: {output_video}")

if __name__ == "__main__":
    main()
