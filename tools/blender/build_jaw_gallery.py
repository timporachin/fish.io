#!/usr/bin/env python3
"""Build a private, local C1 jaw comparison page from existing QA renders.

No rendering or pixel editing takes place. The page can embed existing images
for portable private review, or link them relative to its output location.
"""

from __future__ import annotations

import argparse
import base64
import html
import json
import os
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[2]
VIEWS = (
    ("full_body_lateral", "Full body · lateral", "Check whether the head still belongs to the body silhouette."),
    ("close_left_mouth", "Close mouth · left", "Inspect the mouth seam, rolled lip, jaw depth, and maxillary plate below the eye."),
    ("close_right_mouth", "Close mouth · right", "Check the opposite cheek and mouth corner for matching volume."),
    ("front_mouth", "Mouth · front", "Check upper lip width, forward lower lip, and chin fullness."),
    ("top_snout_jaw", "Snout and jaw · top", "Check blunt muzzle width and the side walls of the opening."),
    ("front_three_quarter_head", "Head · three-quarter", "Check that lip, cheek, and jaw read as connected forms."),
    ("jaw_open_25deg", "Jaw open · 25°", "Temporary deformation check: look for a recessed cavity and substantial lower jaw."),
)
PHOTOS = (
    ("stock-306335267.jpg", "Relaxed side / three-quarter", "Adult largemouth, nearly closed mouth. Use for the blunt snout, curved seam, thick lips, lower-jaw volume, and side plate below the eye. Underwater perspective foreshortens the head."),
    ("stock-512226129.jpg", "Near-closed frontal head", "Adult largemouth. Use for the broad upper rim, forward rounded lower jaw, and deep chin. The frontal view cannot establish lateral jaw length."),
    ("stock-482505893.jpg", "Hand-held extreme gape", "Species-identified open-mouth photograph. Use for rolled lip, maxillary side wall, full mandible, and oral-cavity depth. A hand pulls/supports the lower lip; the gape and stretched tissue are externally forced, not a natural resting pose or a target jaw angle."),
)


def local_url(target: Path, output: Path) -> str:
    relative = Path(os.path.relpath(target, output.parent))
    return "/".join(quote(part) for part in relative.parts)


def read_metrics(path: Path) -> tuple[int, int, int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    browser = data["browser"]
    structure = data["structure"]
    return (int(browser["triangles"]), int(browser["drawCalls"]), int(structure["embeddedImages"]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qa-dir", type=Path, default=ROOT / "artifacts/c1/anatomical-revision-v2/jaw-qa",
                        help="QA directory containing before/, after/, and supplemental-open/")
    parser.add_argument("--review-note", default="", help="Explicit reviewer note for this frozen checkpoint")
    parser.add_argument("--embed-images", action="store_true", help="Embed unaltered image bytes for a portable private HTML gallery")
    parser.add_argument("--output", type=Path, help="Output HTML; defaults to <qa-dir>/jaw-comparison.html")
    parser.add_argument("--reference-dir", type=Path, default=ROOT / "artifacts/c1/references")
    parser.add_argument("--supplemental-dir", type=Path, help="Defaults to <qa-dir>/supplemental-open")
    parser.add_argument("--baseline-metrics", type=Path, default=ROOT / "docs/evidence/c1/before/browser-validation.json")
    parser.add_argument("--candidate-metrics", type=Path,
                        help="Defaults to <qa-dir>/../browser-validation.json")
    args = parser.parse_args()

    qa = args.qa_dir.resolve()
    output = (args.output or qa / "jaw-comparison.html").resolve()
    references = args.reference_dir.resolve()
    supplemental = (args.supplemental_dir or qa / "supplemental-open").resolve()
    baseline_metrics = args.baseline_metrics.resolve()
    candidate_metrics = (args.candidate_metrics or qa.parent / "browser-validation.json").resolve()

    pairs = [(key, title, note, qa / "before" / f"{key}.png", qa / "after" / f"{key}.png")
             for key, title, note in VIEWS]
    pairs.append(("supplemental_open_three_quarter", "Jaw open · supplemental three-quarter",
                  "Additional open-pose perspective; compare mouth-corner depth and the lower-jaw mass.",
                  supplemental / "before/jaw_open_25deg.png", supplemental / "after/jaw_open_25deg.png"))
    required = [baseline_metrics, candidate_metrics]
    required.extend(path for *_, before, after in pairs for path in (before, after))
    required.extend(references / name for name, _, _ in PHOTOS)
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        parser.error("missing inputs:\n  " + "\n  ".join(missing))

    before_cost = read_metrics(baseline_metrics)
    after_cost = read_metrics(candidate_metrics)
    esc = html.escape

    def image_url(path: Path) -> str:
        if args.embed_images:
            mime = "image/jpeg" if path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
            return "data:" + mime + ";base64," + base64.b64encode(path.read_bytes()).decode("ascii")
        return local_url(path, output)

    def figure(path: Path, label: str) -> str:
        url = esc(image_url(path), quote=True)
        return f'<figure><a href="#" onclick="this.href=this.querySelector(&quot;img&quot;).src" download="{esc(path.name, quote=True)}"><img src="{url}" alt="{esc(label, quote=True)}" loading="lazy"></a><figcaption>{esc(label)}</figcaption></figure>'

    sections = []
    for key, title, note, before, after in pairs:
        photo_index = 2 if "open" in key else (1 if key == "front_mouth" else 0)
        photo_name, photo_title, photo_caption = PHOTOS[photo_index]
        reference_url = esc(image_url(references / photo_name), quote=True)
        reference = (f'<aside class="view-reference"><a href="#" onclick="this.href=this.querySelector(&quot;img&quot;).src" download="{esc(photo_name, quote=True)}">'
                     f'<img src="{reference_url}" alt="{esc(photo_title, quote=True)}" loading="lazy"></a>'
                     f'<p><strong>Photographic reference · {esc(photo_title)}</strong><br>{esc(photo_caption)}</p></aside>')
        sections.append(f'<section class="comparison"><h2>{esc(title)}</h2><p>{esc(note)}</p><div class="pair">'
                        + figure(before, "Before · saved pre-jaw checkpoint") + figure(after, "Candidate")
                        + "</div>" + reference + "</section>")
    photo_cards = []
    for name, title, caption in PHOTOS:
        url = esc(image_url(references / name), quote=True)
        photo_cards.append(f'<figure class="photo"><a href="#" onclick="this.href=this.querySelector(&quot;img&quot;).src" download="{esc(name, quote=True)}">'
                           f'<img src="{url}" alt="{esc(title, quote=True)}" loading="lazy"></a>'
                           f'<figcaption><strong>{esc(title)}</strong><br>{esc(caption)}</figcaption></figure>')

    review_note = f'<div class="notice"><p>{esc(args.review_note)}</p></div>' if args.review_note else ""

    def metric_row(label: str, index: int) -> str:
        return (f"<tr><th>{esc(label)}</th><td>{before_cost[index]:,}</td>"
                f"<td>{after_cost[index]:,}</td><td>{after_cost[index] - before_cost[index]:+,}</td></tr>")

    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>C1 jaw review · local comparison</title>
<style>
:root {{color-scheme:dark;font-family:system-ui,sans-serif;background:#151b1a;color:#e8ede8}}
body {{max-width:1500px;margin:auto;padding:clamp(16px,3vw,42px)}}
h1 {{font-size:clamp(2rem,4vw,3.3rem);margin:.2em 0}} h2 {{margin:0 0 .3em}}
p {{line-height:1.5;color:#c9d3cc;max-width:95ch}}
.badge {{display:inline-block;background:#653b32;color:#fff3e9;border-radius:3px;padding:.4em .65em;font-weight:700;letter-spacing:.04em}}
.notice {{border-left:4px solid #bc9e6b;background:#222927;padding:10px 18px;margin:22px 0}}
.comparison {{border-top:1px solid #41504a;padding:24px 0}}
.pair,.references {{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}}
figure {{margin:0;background:#242d29;border:1px solid #45534a}}
figure img {{display:block;width:100%;height:auto}}
figcaption {{padding:10px 13px;line-height:1.45}} a {{color:#b8d8c7}}
table {{border-collapse:collapse;width:min(680px,100%);margin:18px 0 30px;text-align:right}}
th,td {{padding:10px;border-bottom:1px solid #45534a}} th:first-child {{text-align:left}}
.references {{grid-template-columns:repeat(3,minmax(0,1fr));margin:16px 0 36px}}
.view-reference {{display:flex;gap:18px;align-items:center;margin-top:16px}}
.view-reference img {{width:240px;height:auto}} .view-reference p {{max-width:70ch}}
.photo img {{height:300px;object-fit:contain;background:#101513}}
@media(max-width:760px) {{.pair,.references {{grid-template-columns:1fr}} .photo img {{height:auto}} .view-reference {{display:block}}}}
</style></head><body>
<header><span class="badge">C1 NOT ACCEPTED</span><h1>Adult largemouth bass · jaw review</h1>
<p>Private local review of the saved pre-jaw checkpoint and candidate renders. Click any image to download its original pixels. Rendered views share QA camera and lighting settings; the supplemental three-quarter open view is a separate camera setup.</p></header>
<div class="notice"><p>These licensed photographs are for local anatomical review only. Keep the raw images and this linked gallery inside the ignored artifacts workspace; do not commit or publish the photos or this page. The 25° opening is a temporary deformation check, not an authored animation or measured biological angle. C1 remains unaccepted pending review. Any higher triangle budget is an unapproved proposal pending explicit owner approval.</p></div>
{review_note}
<h2>Asset cost</h2><p>Original C1 browser validation versus candidate browser validation. The cost reference is the original 10,976-triangle candidate; the before images show the later saved pre-jaw model, not that original asset. Counts load from the JSON evidence at gallery generation time. Draw calls are for one fish; maps are embedded image count.</p>
<table><thead><tr><th>Metric</th><th>Original</th><th>Candidate</th><th>Change</th></tr></thead><tbody>
{metric_row('Triangles', 0)}{metric_row('Draw calls', 1)}{metric_row('Maps', 2)}
</tbody></table>
<h2>Photographic references</h2><p>These are actual locally licensed photographs. Source records: <a href="https://stock.adobe.com/images/id/306335267">306335267</a>, <a href="https://stock.adobe.com/images/id/512226129">512226129</a>, <a href="https://stock.adobe.com/images/id/482505893">482505893</a>. Their perspective and pose limits matter when judging the rendered jaw; see <a href="https://github.com/timporachin/fish.io/blob/dev/c1-largemouth-bass/docs/C1_JAW_REFERENCES.md">C1 jaw reference notes</a>.</p>
<div class="references">{''.join(photo_cards)}</div>
<h2>Matched QA views</h2>{''.join(sections)}
</body></html>'''
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding="utf-8")
    print(f"Wrote private local gallery: {output}")
    print(f"Original: {before_cost}; candidate: {after_cost}")


if __name__ == "__main__":
    main()
