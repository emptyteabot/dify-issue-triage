"""Combine candidate-recorded audio with captured Dify execution visuals.

Inputs: ordered clip-01.m4a ... clip-10.m4a, timestamped speech-recognition
JSON, and a reviewed English narration-reference.json. No voice synthesis is
performed. Input audio stays outside the repository.
"""
import argparse
import difflib
import json
import math
import re
import subprocess
import textwrap
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
BG = '#101E2A'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
MONO = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'


def run(args):
    subprocess.run(args, check=True)


def duration(path):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', str(path)]))


def normalized(word):
    return re.sub(r'[^a-z0-9]', '', word.lower())


def align_words(text, recognized, speech_end):
    """Align reviewed caption wording to recognized words, with gap interpolation."""
    tokens = text.split()
    expected = [normalized(w) for w in tokens]
    observed = [normalized(w['word']) for w in recognized]
    matched = {}
    for block in difflib.SequenceMatcher(None, expected, observed, autojunk=False).get_matching_blocks():
        for delta in range(block.size):
            matched[block.a + delta] = recognized[block.b + delta]
    anchors = {-1: (0.0, 0.0), len(tokens): (speech_end, speech_end)}
    for i, word in matched.items():
        anchors[i] = (float(word['start']), float(word['end']))
    positions = sorted(anchors)
    aligned = []
    for i, token in enumerate(tokens):
        if i in matched:
            start, end = anchors[i]
        else:
            left = max(p for p in positions if p < i)
            right = min(p for p in positions if p > i)
            a, b = anchors[left][1], anchors[right][0]
            step = max(0.02, (b - a) / (right - left - 1))
            start = a + (i - left - 1) * step
            end = min(speech_end, start + step)
        if aligned:
            start = max(start, aligned[-1]['start'])
        aligned.append({'word': token, 'start': max(0, start), 'end': max(start + .04, end)})
    return aligned


def make_cues(words, offset):
    cues, pending = [], []
    for index, word in enumerate(words):
        pending.append(word)
        sentence_end = bool(re.search(r'[.!?]$', word['word']))
        if len(pending) >= 13 or sentence_end or index == len(words) - 1:
            start = max(0, pending[0]['start'] - .08)
            end = max(start + .65, pending[-1]['end'] + .18)
            if index + 1 < len(words):
                end = min(end, max(start + .5, words[index + 1]['start'] - .04))
            cues.append({'start': offset + start, 'end': offset + end,
                         'text': ' '.join(p['word'] for p in pending)})
            pending = []
    return cues


def timecode(value, ass=False):
    scale = 100 if ass else 1000
    t = round(value * scale)
    h, t = divmod(t, 3600 * scale)
    m, t = divmod(t, 60 * scale)
    s, part = divmod(t, scale)
    return f'{h}:{m:02d}:{s:02d}.{part:02d}' if ass else f'{h:02d}:{m:02d}:{s:02d},{part:03d}'


def handoff_image(site_url):
    im = Image.new('RGB', (1920, 1080), BG)
    d = ImageDraw.Draw(im)
    def font(size, bold=False):
        return ImageFont.truetype(BOLD if bold else FONT, size)
    d.text((38, 22), 'GitHub Issue Triage', font=font(38, True), fill='#F1F6F8')
    d.text((1410, 30), 'DIFY SDK + WORKFLOW', font=font(22, True), fill='#60E3BC')
    d.line((36, 85, 1884, 85), fill='#294150', width=2)
    d.rounded_rectangle((35, 110, 1348, 1017), radius=14, fill='#172E40')
    d.text((64, 145), 'SUBMISSION MATERIALS', font=font(22, True), fill='#60E3BC')
    code = [
        'plugin/                       Dify SDK source',
        'workflow/issue-triage.yml      Actual Dify export',
        'dist/issue_triage-0.1.0.difypkg',
        'docs/issue-triage-answers.md',
        '', 'English demo with candidate-recorded narration',
        site_url, '', 'Published Dify Web App',
        'https://udify.app/workflow/5SgEngzA4VeBZeH3',
        '', 'Public repository',
        'https://github.com/emptyteabot/dify-issue-triage',
    ]
    y = 215
    for line in code:
        for part in textwrap.wrap(line, 83) or ['']:
            d.text((64, y), part, font=ImageFont.truetype(MONO, 24), fill='#F1F6F8')
            y += 39
    y = 140
    for text, size, color in [
        ('10 / Limits and handoff', 35, '#60E3BC'),
        ('Public repositories. At most five comments.', 28, '#F1F6F8'),
        ('Rules and title search require human review.', 28, '#F1F6F8'),
        ('The final brief omits flagged text; earlier tool output can remain in execution logs.', 28, '#F1F6F8'),
        ('Source, exported YAML, app and English video are available.', 28, '#F1F6F8'),
    ]:
        for line in textwrap.wrap(text, 27 if size == 35 else 30):
            d.text((1400, y), line, font=font(size, size == 35), fill=color)
            y += size + 12
        y += 35
    return im


def prepare_visual(im):
    # Remove the old silent-template footer without changing captured UI content.
    body = im.convert('RGB').crop((0, 0, 1920, 1020)).resize((1760, 935), Image.Resampling.LANCZOS)
    out = Image.new('RGB', (1920, 1080), BG)
    out.paste(body, (80, 0))
    ImageDraw.Draw(out).text((80, 1054), 'Candidate-recorded English narration | Edited captures from real Dify executions',
                             font=ImageFont.truetype(FONT, 18), fill='#AEC1CC')
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--audio-directory', type=Path, required=True)
    parser.add_argument('--transcript-directory', type=Path, required=True)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--work-directory', type=Path, required=True)
    parser.add_argument('--site-url', required=True)
    args = parser.parse_args()
    work = args.work_directory
    work.mkdir(parents=True, exist_ok=True)
    reference = json.loads(args.reference.read_text())
    originals = json.loads((ROOT / 'media/walkthrough-chapters.json').read_text())
    captures = work / 'captures'
    with zipfile.ZipFile(ROOT / 'media/capture-source.zip') as archive:
        for item in archive.infolist():
            if not (captures / item.filename).resolve().is_relative_to(captures.resolve()):
                raise ValueError('Unsafe capture path')
            archive.extract(item, captures)
    all_frames, all_audio, all_cues, edits = [], [], [], []
    elapsed = 0.0
    for n in range(1, 11):
        rec = json.loads((args.transcript_directory / f'chapter-{n:02d}.json').read_text())
        recognized = [word for seg in rec['segments'] for word in seg['words']]
        end = min(duration(args.audio_directory / f'clip-{n:02d}.m4a'),
                  max(word['end'] for word in recognized) + .45)
        clean = work / f'voice-{n:02d}.wav'
        run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i',
             str(args.audio_directory / f'clip-{n:02d}.m4a'), '-af',
             f'atrim=start=0:end={end:.6f},asetpts=PTS-STARTPTS,highpass=f=70,lowpass=f=12000,afftdn=nf=-35,loudnorm=I=-18:TP=-1.5:LRA=11,apad=pad_dur=0.6',
             '-ar', '48000', '-ac', '1', str(clean)])
        clip_duration = duration(clean)
        all_audio.append(clean)
        words = align_words(reference[n - 1]['text'], recognized, end - .45)
        all_cues.extend(make_cues(words, elapsed))
        original = originals[n - 1]
        if n in (5, 9):
            folder = 'public-run' if n == 5 else 'run-invalid'
            timing = json.loads((captures / folder / 'timing.json').read_text())
            base = timing[0]['elapsed_ms'] / 1000
            offsets = [r['elapsed_ms'] / 1000 - base for r in timing]
            weights = [offsets[i + 1] - offsets[i] if i + 1 < len(offsets) else 1.2 for i in range(len(offsets))]
        else:
            offsets, weights = [0.0], [1.0]
        for j, (offset, weight) in enumerate(zip(offsets, weights)):
            raw = work / f'raw-{n:02d}-{j:02d}.png'
            if n == 10:
                image = handoff_image(args.site_url)
            else:
                run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-ss',
                     f'{original["start"] + offset + .08:.6f}', '-i',
                     str(ROOT / 'media/walkthrough-captioned.mp4'), '-frames:v', '1', str(raw)])
                image = Image.open(raw)
            output = work / f'frame-{n:02d}-{j:02d}.png'
            prepare_visual(image).save(output)
            all_frames.append((output, clip_duration * weight / sum(weights)))
        edits.append({'chapter': n, 'title': reference[n - 1]['title'], 'start': round(elapsed, 3),
                      'end': round(elapsed + clip_duration, 3), 'voice_source': f'candidate-clip-{n:02d}',
                      'source_trim_end': round(end, 3), 'text': reference[n - 1]['text']})
        elapsed += clip_duration
        print(json.dumps({'chapter': n, 'duration': round(clip_duration, 3), 'timeline_end': round(elapsed, 3)}), flush=True)
    for i in range(len(all_cues) - 1):
        all_cues[i]['end'] = min(all_cues[i]['end'], all_cues[i + 1]['start'] - .02)
    audio_list = work / 'audio.txt'
    audio_list.write_text(''.join(f"file '{p.as_posix()}'\n" for p in all_audio))
    joined = work / 'narration.wav'
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0',
         '-i', str(audio_list), '-c', 'copy', str(joined)])
    frames = work / 'frames.txt'
    frames.write_text(''.join(f"file '{p.as_posix()}'\nduration {d:.6f}\n" for p, d in all_frames) + f"file '{all_frames[-1][0].as_posix()}'\n")
    srt = ROOT / 'media/walkthrough-narrated.srt'
    srt.write_text('\n'.join(f"{i}\n{timecode(c['start'])} --> {timecode(c['end'])}\n" + '\n'.join(textwrap.wrap(c['text'], 76)) + '\n' for i, c in enumerate(all_cues, 1)))
    vtt = ROOT / 'media/walkthrough-narrated.vtt'
    vtt.write_text('WEBVTT\n\n' + '\n'.join(f"{timecode(c['start']).replace(',', '.')} --> {timecode(c['end']).replace(',', '.')}\n" + '\n'.join(textwrap.wrap(c['text'], 76)) + '\n' for c in all_cues))
    ass = work / 'captions.ass'
    ass.write_text('[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 0\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,DejaVu Sans,32,&H00FFFFFF,&H00FFFFFF,&H00101E2A,&H00101E2A,0,0,0,0,100,100,0,0,1,1.5,0,2,100,100,52,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n' + ''.join('Dialogue: 0,' + timecode(c['start'], True) + ',' + timecode(c['end'], True) + ',Default,,0,0,0,,' + r'\N'.join(textwrap.wrap(c['text'], 76)) + '\n' for c in all_cues))
    output = ROOT / 'media/walkthrough-narrated.mp4'
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0',
         '-i', str(frames), '-i', str(joined), '-i', str(srt), '-map', '0:v', '-map', '1:a', '-map', '2:0',
         '-vf', f'fps=24,ass={ass.as_posix()}', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-threads', '4',
         '-pix_fmt', 'yuv420p', '-r', '24', '-c:a', 'aac', '-b:a', '96k', '-c:s', 'mov_text',
         '-metadata:s:s:0', 'language=eng', '-metadata:s:a:0', 'language=eng',
         '-metadata', 'title=GitHub Issue Triage - Candidate English Walkthrough',
         '-t', f'{elapsed:.6f}', '-movflags', '+faststart', str(output)])
    streams = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(output)]))['streams']
    for stream_type in ('video', 'audio'):
        actual = float(next(s['duration'] for s in streams if s['codec_type'] == stream_type))
        if abs(actual - elapsed) > .15:
            raise ValueError(f'{stream_type} duration does not match the narration timeline: {actual} vs {elapsed}')
    report = {'candidate_narration': True, 'synthetic_voice': False,
              'duration_seconds': round(duration(output), 3), 'size_bytes': output.stat().st_size,
              'audio_editing': 'Trailing silence trimmed; mild filtering and loudness normalization; original voice and speed preserved.',
              'captions': 'English wording reviewed against the supplied script; speech timestamps used for alignment; technical names normalized.',
              'visuals': 'Edited captures from actual Dify executions, retimed to the candidate voice. Original silent-template footer removed.',
              'chapters': edits}
    (ROOT / 'media/narrated-edit.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'output': str(output), 'duration': report['duration_seconds'], 'bytes': report['size_bytes'], 'captions': len(all_cues)}), flush=True)


if __name__ == '__main__':
    main()
