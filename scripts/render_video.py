import json
import math
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1280, 720
FPS = 15
FONT_PATH_BOLD = "C:/Windows/Fonts/meiryob.ttc"
FONT_PATH_REG = "C:/Windows/Fonts/meiryo.ttc"

with open("assets/audio/dialogue_metadata.json", "r", encoding="utf-8") as f:
    META = json.load(f)

TOTAL_DURATION = META["total_duration"]
SLIDES = {s["id"]: s for s in META["slides"]}
DIALOGUE = META["dialogue"]

font_title = ImageFont.truetype(FONT_PATH_BOLD, 24)
font_tag = ImageFont.truetype(FONT_PATH_BOLD, 14)
font_card_title = ImageFont.truetype(FONT_PATH_BOLD, 23)
font_card_sub = ImageFont.truetype(FONT_PATH_REG, 15)
font_highlight = ImageFont.truetype(FONT_PATH_REG, 17)
font_highlight_bold = ImageFont.truetype(FONT_PATH_BOLD, 17)
font_speaker_name = ImageFont.truetype(FONT_PATH_BOLD, 19)
font_speaker_role = ImageFont.truetype(FONT_PATH_REG, 13)
font_caption = ImageFont.truetype(FONT_PATH_BOLD, 20)
font_small = ImageFont.truetype(FONT_PATH_REG, 13)
font_time = ImageFont.truetype(FONT_PATH_BOLD, 14)

def draw_rounded_rect(draw, bbox, radius, fill=None, outline=None, width=1):
    x0, y0, x1, y1 = bbox
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)

# 各ダイアログ（10パート）ごとのベース静止画を事前作成
PART_BACKGROUNDS = {}

for dlg in DIALOGUE:
    speaker = dlg["speaker"]
    current_slide = SLIDES[dlg["slide"]]
    
    img = Image.new("RGB", (WIDTH, HEIGHT), (11, 17, 32))
    draw = ImageDraw.Draw(img)
    
    # Header
    draw_rounded_rect(draw, (30, 20, WIDTH - 30, 75), 14, fill=(20, 29, 47), outline=(40, 53, 79), width=1)
    draw_rounded_rect(draw, (45, 33, 210, 62), 8, fill=(2, 136, 209))
    draw.text((58, 38), "NotebookLM AI", font=font_tag, fill=(255, 255, 255))
    draw.text((225, 36), "伊豆2泊3日 家族旅行のしおり - 音声対談解説", font=font_title, fill=(241, 245, 249))
    
    # Host A (Nanami)
    is_nanami = (speaker == "nanami")
    box_a_fill = (20, 29, 47) if not is_nanami else (15, 38, 64)
    box_a_border = (40, 53, 79) if not is_nanami else (56, 189, 248)
    draw_rounded_rect(draw, (30, 95, 360, 235), 16, fill=box_a_fill, outline=box_a_border, width=2 if is_nanami else 1)
    
    avatar_a_fill = (2, 136, 209) if is_nanami else (51, 65, 85)
    draw.ellipse((50, 115, 120, 185), fill=avatar_a_fill, outline=(255, 255, 255) if is_nanami else (100, 116, 139), width=2)
    draw.text((71, 133), "N", font=ImageFont.truetype(FONT_PATH_BOLD, 30), fill=(255, 255, 255))
    
    draw.text((135, 120), "Nanami", font=font_speaker_name, fill=(255, 255, 255))
    draw.text((135, 147), "AI ナビゲーター (進行・案内)", font=font_speaker_role, fill=(148, 163, 184))
    status_a_text = "● SPEAKING" if is_nanami else "○ LISTENING"
    status_a_color = (56, 189, 248) if is_nanami else (100, 116, 139)
    draw.text((135, 172), status_a_text, font=font_small, fill=status_a_color)
    
    # Host B (Keita)
    is_keita = (speaker == "keita")
    box_b_fill = (20, 29, 47) if not is_keita else (52, 28, 20)
    box_b_border = (40, 53, 79) if not is_keita else (251, 146, 60)
    draw_rounded_rect(draw, (30, 250, 360, 390), 16, fill=box_b_fill, outline=box_b_border, width=2 if is_keita else 1)
    
    avatar_b_fill = (234, 88, 12) if is_keita else (51, 65, 85)
    draw.ellipse((50, 270, 120, 340), fill=avatar_b_fill, outline=(255, 255, 255) if is_keita else (100, 116, 139), width=2)
    draw.text((71, 288), "K", font=ImageFont.truetype(FONT_PATH_BOLD, 30), fill=(255, 255, 255))
    
    draw.text((135, 275), "Keita", font=font_speaker_name, fill=(255, 255, 255))
    draw.text((135, 302), "AI コメンテーター (解説・見所)", font=font_speaker_role, fill=(148, 163, 184))
    status_b_text = "● SPEAKING" if is_keita else "○ LISTENING"
    status_b_color = (251, 146, 60) if is_keita else (100, 116, 139)
    draw.text((135, 327), status_b_text, font=font_small, fill=status_b_color)
    
    # Route list (left bottom)
    draw_rounded_rect(draw, (30, 405, 360, 525), 14, fill=(18, 25, 41), outline=(40, 53, 79), width=1)
    draw.text((45, 418), "◆ 旅程ルート概要", font=font_speaker_name, fill=(226, 232, 240))
    routes = [
        ("1日目", "伊東温泉 サンハトヤ（海底温泉）", current_slide["id"] == 1),
        ("2日目", "ぐらんぱる公園 ➔ きらの里", current_slide["id"] == 2),
        ("3日目", "橋立つり橋 ➔ 特急踊り子62号", current_slide["id"] == 3),
    ]
    for idx, (day_lbl, route_txt, is_curr) in enumerate(routes):
        ry = 448 + idx * 24
        bullet_col = (56, 189, 248) if is_curr else (100, 116, 139)
        draw.text((45, ry), "▶" if is_curr else "・", font=font_small, fill=bullet_col)
        draw.text((62, ry), f"{day_lbl}: {route_txt}", font=font_small, fill=(255, 255, 255) if is_curr else (148, 163, 184))

    # Right Slide Card
    draw_rounded_rect(draw, (380, 95, WIDTH - 30, 525), 18, fill=(18, 25, 41), outline=(40, 53, 79), width=1)
    tag_bg = (2, 136, 209)
    if current_slide["id"] == 1: tag_bg = (0, 137, 123)
    elif current_slide["id"] == 2: tag_bg = (234, 88, 12)
    elif current_slide["id"] == 3: tag_bg = (126, 34, 206)
    
    draw_rounded_rect(draw, (405, 115, 525, 147), 8, fill=tag_bg)
    draw.text((420, 122), current_slide["tag"], font=font_tag, fill=(255, 255, 255))
    draw.text((405, 158), current_slide["title"], font=font_card_title, fill=(248, 250, 252))
    draw.text((405, 194), current_slide["subtitle"], font=font_card_sub, fill=(148, 163, 184))
    draw.line([(405, 226), (WIDTH - 55, 226)], fill=(40, 53, 79), width=1)
    
    draw.text((405, 240), "★ スポットの注目ポイント & 魅力", font=font_speaker_name, fill=(226, 232, 240))
    for h_idx, hl_text in enumerate(current_slide["highlights"]):
        hy = 280 + h_idx * 75
        draw_rounded_rect(draw, (405, hy, WIDTH - 55, hy + 62), 12, fill=(24, 34, 53), outline=(51, 65, 85), width=1)
        draw.ellipse((420, hy + 13, 456, hy + 49), fill=tag_bg)
        draw.text((433, hy + 19), str(h_idx + 1), font=font_highlight_bold, fill=(255, 255, 255))
        draw.text((470, hy + 19), hl_text, font=font_highlight, fill=(241, 245, 249))

    # Bottom caption box
    draw_rounded_rect(draw, (30, 540, WIDTH - 30, 700), 16, fill=(14, 20, 36), outline=(40, 53, 79), width=1)
    spk_tag_col = (2, 136, 209) if speaker == "nanami" else (234, 88, 12)
    spk_tag_name = "Nanami" if speaker == "nanami" else "Keita"
    draw_rounded_rect(draw, (50, 555, 140, 587), 6, fill=spk_tag_col)
    draw.text((62, 560), spk_tag_name, font=font_tag, fill=(255, 255, 255))
    
    text = dlg["text"]
    if len(text) > 42:
        draw.text((155, 555), text[:42], font=font_caption, fill=(255, 255, 255))
        draw.text((155, 587), text[42:], font=font_caption, fill=(255, 255, 255))
    else:
        draw.text((155, 563), text, font=font_caption, fill=(255, 255, 255))
        
    PART_BACKGROUNDS[dlg["index"]] = img

def draw_wave_bars(draw, cx, cy, count, active, t, color):
    if not active:
        for i in range(count):
            bx = cx + (i - count//2) * 6
            h = 3
            draw.rectangle([bx-1.5, cy-h, bx+1.5, cy+h], fill=(71, 85, 105))
    else:
        for i in range(count):
            bx = cx + (i - count//2) * 6
            phase = t * 12 + i * 0.85
            h = int(6 + math.sin(phase) * 11 + math.cos(phase * 1.6) * 6)
            h = max(3, min(24, h))
            draw.rectangle([bx-1.5, cy-h, bx+1.5, cy+h], fill=color)

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
    
    draw_wave_bars(draw, 290, 180, 10, is_nanami, t, (56, 189, 248))
    draw_wave_bars(draw, 290, 335, 10, is_keita, t, (251, 146, 60))
    
    # Progress bar
    bar_x0, bar_y = 50, 645
    bar_w = WIDTH - 260
    progress = min(1.0, max(0.0, t / TOTAL_DURATION))
    
    draw.rounded_rectangle([bar_x0, bar_y, bar_x0 + bar_w, bar_y + 8], radius=4, fill=(40, 53, 79))
    if progress > 0:
        draw.rounded_rectangle([bar_x0, bar_y, bar_x0 + int(bar_w * progress), bar_y + 8], radius=4, fill=(56, 189, 248))
        draw.ellipse((bar_x0 + int(bar_w * progress) - 6, bar_y - 3, bar_x0 + int(bar_w * progress) + 6, bar_y + 11), fill=(255, 255, 255))
        
    cur_min, cur_sec = int(t // 60), int(t % 60)
    tot_min, tot_sec = int(TOTAL_DURATION // 60), int(TOTAL_DURATION % 60)
    time_str = f"{cur_min:02d}:{cur_sec:02d} / {tot_min:02d}:{tot_sec:02d}"
    draw.text((bar_x0 + bar_w + 20, bar_y - 4), time_str, font=font_time, fill=(148, 163, 184))
    
    return base

def main():
    output_video = "assets/video/izu_trip_audio_overview.mp4"
    audio_file = "assets/audio/notebooklm_overview.mp3"
    
    total_frames = int(TOTAL_DURATION * FPS)
    print(f"Fast rendering {total_frames} frames ({TOTAL_DURATION:.1f}s @ {FPS}fps)...")
    
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
    print(f"\nSuccessfully generated video: {output_video}")

if __name__ == "__main__":
    main()
