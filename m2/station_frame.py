"""The angular frame each station's sectors are measured in — one implementation, used everywhere.

A station's ring is described by an angle, and that angle is only meaningful relative to some reference direction in
the plane of the ring. The original choice was to parallel-transport a normal along the station path: start with any
vector perpendicular to the first tangent, and at each station re-project it onto the new perpendicular plane.

That is correct for a straight path and wrong for a wandering one. The station path is the SMOOTHED CAMERA PATH, so
when the scope wanders the path is a helix, its tangent circles, and the transported frame rotates with it. Measured
against planted truth, a notch at a true -90 deg was reported at -90 on axis and at +64 to +75 once the camera sat
0.2-0.3 R off the axis: a 155 degree error, from the frame, not the wall.

`global_reference` fixes a single direction for the whole run and projects it into each station's plane. It cannot
accumulate rotation, because nothing is carried from one station to the next.

    N1, N2 = station_frame(S, method="global")      # method="transport" reproduces the original behaviour
"""
import numpy as np


def _unit(v):
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.maximum(n, 1e-12)


def tangents(S):
    """Unit tangent at each station, from the station path."""
    return _unit(np.gradient(np.asarray(S, float), axis=0))


def station_frame(S, method="global", reference=None):
    """Return (N1, N2): two unit vectors per station spanning the plane perpendicular to the path.

    method="global"    : one fixed reference direction projected into every station's plane. Non-accumulating, so a
                         wandering path cannot rotate it. This is the correct default.
    method="transport" : the original parallel transport, kept so old results can be reproduced exactly.
    """
    S = np.asarray(S, float); T = tangents(S); n = len(S)
    N1 = np.zeros_like(S); N2 = np.zeros_like(S)
    if method == "transport":
        n1 = np.cross(T[0], [0, 0, 1.0])
        if np.linalg.norm(n1) <= 1e-3: n1 = np.cross(T[0], [0, 1.0, 0])
        n1 = n1 / np.linalg.norm(n1)
        for i in range(n):
            n1 = n1 - (n1 @ T[i]) * T[i]; n1 = n1 / max(np.linalg.norm(n1), 1e-12)
            N1[i] = n1; N2[i] = np.cross(T[i], n1)
        return N1, N2
    if method != "global": raise ValueError(f"unknown method {method!r}")
    if reference is None:
        # the mean direction of travel defines the axis; take any fixed vector well away from it as the reference
        axis = _unit(T.mean(0))
        cand = np.eye(3)[int(np.argmin(np.abs(axis)))]          # the world axis least parallel to the path
        reference = _unit(cand - (cand @ axis) * axis)
    reference = _unit(np.asarray(reference, float))
    for i in range(n):
        v = reference - (reference @ T[i]) * T[i]
        nv = np.linalg.norm(v)
        if nv < 1e-6:                                            # reference parallel to this tangent: fall back
            alt = np.eye(3)[int(np.argmin(np.abs(T[i])))]
            v = alt - (alt @ T[i]) * T[i]; nv = np.linalg.norm(v)
        N1[i] = v / nv; N2[i] = np.cross(T[i], N1[i])
    return N1, N2


def frame_rotation(S, method="global"):
    """How much the frame turns from station to station, in degrees — a diagnostic, not used in the estimate."""
    N1, _ = station_frame(S, method); T = tangents(S)
    out = np.zeros(len(S))
    for i in range(1, len(S)):
        a = N1[i - 1] - (N1[i - 1] @ T[i]) * T[i]
        na = np.linalg.norm(a)
        if na < 1e-9: continue
        a /= na
        out[i] = np.degrees(np.arccos(np.clip(a @ N1[i], -1, 1)))
    return out


def frame_from_grid(G, method=None):
    """The frame a grid was actually binned in.

    Grids written after this change carry N1 and N2, so a downstream tool must use those rather than re-deriving them:
    if the tool's convention and the grid's disagree, every angle it reports is silently rotated.

    A grid written BEFORE this change stores no frame. Those were binned by parallel transport, so that is what we fall
    back to - reproducing the grid's own convention, wrong as it is, beats quietly rotating it into a different one. The
    warning is the point: such a grid should be rebuilt, not reinterpreted.
    """
    files = list(getattr(G, "files", []))
    if "N1" in files and "N2" in files:
        return G["N1"], G["N2"], (str(G["frame"]) if "frame" in files else "stored")
    m = method or "transport"
    N1, N2 = station_frame(G["S"], method=m)
    print(f"   ! this grid predates stored frames; falling back to '{m}' (its original convention). Rebuild it to get the corrected frame.")
    return N1, N2, f"{m} (re-derived)"
