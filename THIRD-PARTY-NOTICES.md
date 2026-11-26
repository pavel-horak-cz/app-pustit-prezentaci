# Third-party notices

SlidesByHand itself is released under the MIT License (see `LICENSE`).
It bundles the following third-party components. Each keeps its own license.

| Component | Where | License | Source |
|---|---|---|---|
| MediaPipe Tasks Vision (hand tracking runtime) | `lib/tasks-vision/` | Apache License 2.0, see `lib/tasks-vision/LICENSE` | https://github.com/google-ai-edge/mediapipe |
| MediaPipe Hand Landmarker model | `lib/hand_landmarker.task` | Apache License 2.0 | https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker |
| PDF.js (PDF rendering) | `lib/pdfjs/` | Apache License 2.0, see `lib/pdfjs/LICENSE` | https://github.com/mozilla/pdf.js |
| Character maps bundled with PDF.js | `lib/pdfjs/cmaps/` | see `lib/pdfjs/cmaps/LICENSE` | Adobe |
| Standard fonts bundled with PDF.js | `lib/pdfjs/standard_fonts/` | see `LICENSE_FOXIT` and `LICENSE_LIBERATION` in that folder | Foxit, Liberation fonts |
| Image decoders and color management bundled with PDF.js | `lib/pdfjs/wasm/`, `lib/pdfjs/iccs/` | see the `LICENSE_*` files in those folders | OpenJPEG, JBIG2, qcms, QuickJS |
| Tabler Icons (outline icons embedded in `index.html`) | `index.html` | MIT, see `lib/LICENSE-tabler-icons.txt` | https://github.com/tabler/tabler-icons |
| Inter typeface | `lib/fonts/` | SIL Open Font License 1.1, see `lib/fonts/LICENSE-Inter.txt` | https://github.com/rsms/inter |
| Sample applause sound | `ukazka.mp3` | CC0 (public domain) | "Applause from 40 People #5" (sound no. 3521) by Joseph Sardin, https://bigsoundbank.com/applause-from-40-people-5-s3521.html |

Changes made to the applause recording: silence trimmed at the start and the end, short fade in and fade out, loudness levelled, converted to MP3.

The sample presentations `ukazka-cs.pdf` and `ukazka-en.pdf` were made for this project and are covered by the project's MIT License.
