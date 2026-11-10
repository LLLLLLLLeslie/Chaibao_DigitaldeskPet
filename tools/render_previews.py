"""Render previews using only exact cells from the final encoded v2 atlas."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw


SKILL_SCRIPTS = Path(__file__).resolve().parent / 'vendor'
RUN_DIR = Path(__file__).resolve().parent
WORKSPACE = RUN_DIR.parent
ROWS = [('idle', 6), ('running-right', 8), ('running-left', 8), ('waving', 4),
        ('jumping', 5), ('failed', 8), ('waiting', 6), ('running', 6), ('review', 6),
        ('look-row-9', 8), ('look-row-10', 8)]


def panel(frame, title, footer=''):
    # Native 192x208 sprite pixels; decoration is outside the sprite cell.
    canvas = Image.new('RGB', (256, 272), '#e9e8e5')
    canvas.paste(frame, (32, 32), frame)
    draw = ImageDraw.Draw(canvas)
    draw.text((12, 10), title, fill='#202020')
    draw.text((12, 250), footer, fill='#505050')
    return canvas


def save_gif(frames, durations, path):
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=durations,
                   loop=0, disposal=2, optimize=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--atlas', type=Path, default=WORKSPACE/'assets/pet/spritesheet.png')
    parser.add_argument('--output-dir', type=Path, default=WORKSPACE/'build/previews')
    args = parser.parse_args()
    atlas_path = args.atlas.resolve()
    if not atlas_path.is_file():
        raise SystemExit(f'Final encoded atlas does not exist: {atlas_path}')
    raw = atlas_path.read_bytes()
    with Image.open(atlas_path) as image:
        if image.size != (1536, 2288):
            raise SystemExit(f'Expected v2 atlas 1536x2288, got {image.size}')
        atlas = image.convert('RGBA')
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    frames_root = output/'exact-frames'
    cells = {}
    for row, (state, count) in enumerate(ROWS):
        state_dir = frames_root/state
        state_dir.mkdir(parents=True, exist_ok=True)
        cells[state] = []
        for index in range(count):
            frame = atlas.crop((index*192, row*208, (index+1)*192, (row+1)*208))
            frame.save(state_dir/f'{index:02}.png')
            cells[state].append(frame)

    renderer_path = SKILL_SCRIPTS/'render_animation_previews.py'
    subprocess.run([sys.executable, str(renderer_path), '--frames-root', str(frames_root),
                    '--output-dir', str(output/'states')], check=True)
    spec = importlib.util.spec_from_file_location('bundled_renderer', renderer_path)
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)

    all_frames, all_durations = [], []
    for state, count in ROWS[:9]:
        for index, frame in enumerate(cells[state]):
            all_frames.append(panel(frame, state, f'Frame {index+1} / {count}'))
            all_durations.append(renderer.ROW_DURATIONS[state][index])
    save_gif(all_frames, all_durations, output/'all-states.gif')

    transition = cells['idle'] + cells['jumping'] + cells['idle']
    transition_durations = renderer.ROW_DURATIONS['idle'] + renderer.ROW_DURATIONS['jumping'] + renderer.ROW_DURATIONS['idle']
    # Preserve literal native cell bounds for jump and landing inspection.
    save_gif(transition, transition_durations, output/'idle-jump-idle.gif')

    looks = cells['look-row-9'] + cells['look-row-10']
    look_panels = [panel(frame, 'Look direction', f'{index*22.5:g} degrees clockwise')
                   for index, frame in enumerate(looks)]
    save_gif(look_panels, [200]*16, output/'look-loop.gif')

    still_choices = [('idle', 0), ('running-right', 3), ('jumping', 2), ('review', 3)]
    still_paths = []
    still_strip = Image.new('RGB', (256*4, 272), '#e9e8e5')
    for number, (state, index) in enumerate(still_choices):
        row_number = [name for name, _ in ROWS].index(state)
        still = panel(cells[state][index], state, f'Atlas row {row_number}, frame {index}')
        path = output/f'still-{number+1:02}-{state}.png'
        still.save(path)
        still_paths.append(str(path))
        still_strip.paste(still, (256*number, 0))
    still_strip.save(output/'four-labeled-stills.png')

    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', '-i', str(output/'all-states.gif'),
                    '-an', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                    str(output/'all-states.mp4')], check=True)
    report = {'ok': True, 'atlas': str(atlas_path), 'atlas_sha256': hashlib.sha256(raw).hexdigest(),
              'atlas_bytes': len(raw), 'exact_cell_size': [192, 208], 'extracted_cells': 73,
              'sprite_resizing': False, 'output_dir': str(output), 'still_paths': still_paths,
              'bundled_state_renderer': str(renderer_path)}
    (output/'preview-provenance.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

