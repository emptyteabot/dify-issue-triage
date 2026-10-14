# English assessment walkthrough

[Watch the final English walkthrough](https://dify-issue-triage-demo.lunarnewt3.chatgpt.site/) or [download the MP4](https://dify-issue-triage-demo.lunarnewt3.chatgpt.site/walkthrough.mp4).

The final video uses ten audio clips recorded by the candidate. The original voice and speed are preserved. Editing trims trailing silence, applies mild filtering, balances loudness, retimes the captured visuals and adds reviewed English subtitles. It does not synthesize or replace the candidate's speech.

The original `walkthrough-captioned.mp4` is a silent recording template with real Dify execution captures. It remains here as supporting material. The final narrated MP4 is hosted on the submission page; private raw recordings are not committed.

- `walkthrough-captions.srt`: English subtitle text.
- `walkthrough-chapters.json`: chapter timing.
- `capture-source.zip`: original available captured screens with timing metadata.
- `../scripts/build_captioned_video.py`: rebuilds the recording template with Pillow and ffmpeg.
- `walkthrough-narrated.srt` and `.vtt`: reviewed English captions for the final video.
- `narration-reference.json`: English reference text used to review captions.
- `narrated-edit.json`: the final chapter timing and editing scope.
- `../scripts/build_narrated_video.py`: combines ordered candidate clips and reviewed transcript timing with the actual captured visuals. Raw input audio is supplied locally and is not part of the public repository.

The walkthrough is edited for presentation. Its execution images come from actual runs; no successful result or UI is simulated.
