"""Asset-specific C1 QA gate for the supplied bass static candidate.

This validates observed eye-socket/eye-cup and thin dorsal-fin boundary
semantics. It never applies the custom procedural bass's named-part contract.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path


def intersections(segments, coordinate):
    values = []
    for (a, z0), (b, z1) in segments:
        if min(a, b) <= coordinate <= max(a, b) and abs(b - a) > 1e-9:
            values.append(z0 + (z1 - z0) * (coordinate - a) / (b - a))
    return sorted(values)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--qa-dir", type=Path, required=True)
    a = p.parse_args()
    folder = a.qa_dir
    def read(name):
        return json.loads((folder / name).read_text())
    prep = read("preparation-report.json")
    geometry = read("candidate-geometry-qa.json")
    mouth = read("candidate-mouth-qa.json")
    section = read("candidate-rest-section.json")
    equivalence = read("weighted-static-equivalence.json")
    browser = read("browser-qa.json")
    glb = read("glb-validator-qa.json")
    candidate_glb = folder / "candidate-static.glb"
    candidate_blend = folder / "candidate-static.blend"
    weighted_blend = folder / "candidate-weighted-qa.blend"
    def sha(file):
        return hashlib.sha256(file.read_bytes()).hexdigest()
    body = geometry["objects"]["body_mesh"]["evaluated"]
    eyes = geometry["objects"]["eye_mesh"]["evaluated"]
    body_loops = body["boundaryGroups"]
    eye_loops = eyes["boundaryGroups"]
    bilateral_sockets = [g for g in body_loops if g["edges"] == 26 and
                         g["bounds"][0][0] > .15 and min(abs(v) for v in g["bounds"][1]) > .015]
    dorsal_rims = [g for g in body_loops if g["edges"] == 12 and
                   g["bounds"][0][1] < .02 and max(abs(v) for v in g["bounds"][1]) < .0001 and
                   g["bounds"][2][0] > .055]
    # Source-coordinate weighted rest/open section is x=+2 mm at Y=-105 mm.
    rest_z = intersections(mouth["neutral"]["midlineSectionAtX0p002M"], -.105)
    open_z = intersections(mouth["jawOpen25"]["midlineSectionAtX0p002M"], -.105)
    coeff = equivalence["objects"]["body_mesh"]["affineCoefficients"]
    scale = coeff[0][0]
    candidate_x = coeff[3][0] + scale * .105
    static_z = intersections(section["segments"], candidate_x)
    rest_gap = rest_z[2] - rest_z[1] if len(rest_z) == 4 else None
    open_gap = open_z[2] - open_z[1] if len(open_z) == 4 else None
    static_gap = static_z[2] - static_z[1] if len(static_z) == 4 else None
    checks = {
        "frozenAssetHashes": sha(candidate_glb) == prep["glb_sha256"] and
            sha(candidate_blend) == prep["candidate_blend_sha256"] and
            Path(browser["input"]).resolve() == candidate_glb.resolve() and
            Path(equivalence["weighted"]).resolve() == weighted_blend.resolve(),
        "triangleBudget": browser["triangles"] == prep["candidate_triangle_total"] <= 10976,
        "drawCallBudget": 0 < browser["drawCalls"] <= 11,
        "mapsAndPbr": len(browser["decodedImages"]) <= 5 and browser["bodyPbrMaterialFound"] and
            all(im["decoded"] and max(im["width"], im["height"]) <= 2048 for im in browser["decodedImages"]),
        "staticNoSkinClips": browser["skinnedMeshCount"] == browser["animationClips"] == 0,
        "glbFormat": glb["numErrors"] == glb["numWarnings"] == 0,
        "bodyFiniteClean": body["invalidVertices"] == body["zeroAreaFaces"] == body["looseVertices"] == 0 and
            len(body["components"]) == 1 and body["components"][0]["wireEdges"] ==
            body["components"][0]["nonManifoldEdges"] == body["components"][0]["windingConflicts"] == 0,
        "uvFinite": all(layer["invalid"] == 0 for obj in (body, eyes) for layer in obj["uvLayers"]),
        "boundarySemantics": len(body_loops) == 3 and len(bilateral_sockets) == 2 and len(dorsal_rims) == 1 and
            len(eye_loops) == 2 and all(g["edges"] == 16 for g in eye_loops),
        "weightedStaticExactTopology": all(o["identicalFaceIndexOrder"] and o["maxAffineResidualM"] < 1e-6
                                           for o in equivalence["objects"].values()),
        "staticOralPocket": static_gap is not None and static_gap > .003 and rest_gap is not None and
            abs(static_gap - scale * rest_gap) < .0002,
        "weightedJawOpens": open_gap is not None and rest_gap is not None and open_gap > rest_gap + .015,
        "headRoiNoStrictCrossings": all(mouth[pose]["combinedHeadRoiYLessThanMinus0p06235M"]
                                        ["selfCrossing"]["strictCrossings"] == 0
                                        for pose in ("neutral", "jawOpen25")),
    }
    result = {"checks": checks, "pass": all(checks.values()),
              "measurements": {"staticOralGapM": static_gap, "weightedRestGapM": rest_gap,
                               "weightedOpen25GapM": open_gap, "candidateSectionXM": candidate_x,
                               "bilateralEyeSockets": len(bilateral_sockets),
                               "dorsalFinRimLoops": len(dorsal_rims)},
              "limitations": [
                  "The body is open at both eye sockets and a 12-edge thin dorsal fin rim; this gate does not claim a watertight body or closed fin sheets.",
                  "The 25-degree opening uses a temporary source-bone binding on the exact weighted decimated mesh. The static GLB has no skin or animation.",
                  "Strict BVH crossings exclude shared-vertex and coplanar cases and cover the scoped anterior head ROI, not all-body collision freedom.",
                  "The section gap is a repeatable geometry sample, not an annotated anatomical landmark or biologically validated maximum gape.",
                  "Browser loading does not establish physical iPhone/Safari performance or visual acceptance.",
              ]}
    output = folder / "candidate-qa-gate.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if not result["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
