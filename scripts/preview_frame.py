import os
from render_video import render_frame, TOTAL_DURATION

os.makedirs("assets/preview", exist_ok=True)
timestamps = [5.0, 30.0, 65.0, 95.0, 128.0]

for idx, t in enumerate(timestamps):
    img = render_frame(t, int(t * 20))
    out_path = f"assets/preview/preview_scene_{idx}.jpg"
    img.save(out_path, quality=90)
    print(f"Saved preview at t={t}s -> {out_path}")
