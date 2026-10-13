# English-captioned demo template

`walkthrough-captioned.mp4` contains real Dify execution captures and English explanatory captions. It is silent. It does not impersonate the candidate or claim to be a finished candidate-narrated presentation.

The workflow, source, test evidence and exported DSL are ready. The remaining human step is the candidate's own spoken English explanation, as required by the assessment. Rehearse from `../docs/walkthrough-notes.md` and explain the implementation in your own words.

- `walkthrough-captions.srt`: English subtitle text.
- `walkthrough-chapters.json`: chapter timing.
- `capture-source.zip`: original available captured screens with timing metadata.
- `../scripts/build_captioned_video.py`: rebuilds the recording template with Pillow and ffmpeg.

The walkthrough is edited for presentation. Its execution images come from actual runs; no successful result or UI is simulated.
