#!/usr/bin/env python3
"""Minecraft-flavoured SFX synthesis engine (numpy only).

Design goals (why these sound like Minecraft, not generic indie):
  * mono, lo-fi (gentle bitcrush + high roll-off) — early-engine character
  * noise-based, percussive hits with fast attack / quick decay for materials
  * warm, low-passed — no harsh highs
  * short durations, pitch-randomisation friendly (the game shifts 0.85-1.2x)
  * End-ethereal layer: reverb tails, inharmonic glassy bells, warbling voices
"""
import numpy as np

SR = 44100


def rng(seed):
    return np.random.default_rng(seed)


def t(dur):
    return np.linspace(0, dur, int(SR * dur), endpoint=False)


# ---------- sources ----------
def sine(freq, dur, phase=0.0):
    return np.sin(2 * np.pi * freq * t(dur) + phase)


def saw(freq, dur):
    x = t(dur) * freq
    return 2 * (x - np.floor(x + 0.5))


def square(freq, dur, duty=0.5):
    return np.where((t(dur) * freq) % 1 < duty, 1.0, -1.0)


def triangle(freq, dur):
    return 2 * np.abs(saw(freq, dur)) - 1


def glide(f0, f1, dur, curve=1.0, kind="sine"):
    """Pitch sweep via instantaneous phase (curve>1 = fast->slow)."""
    tt = t(dur)
    frac = (tt / dur) ** curve
    freq = f0 * (f1 / f0) ** frac
    phase = 2 * np.pi * np.cumsum(freq) / SR
    if kind == "saw":
        x = phase / (2 * np.pi)
        return 2 * (x - np.floor(x + 0.5))
    if kind == "square":
        return np.sign(np.sin(phase))
    return np.sin(phase)


def white(dur, seed=0):
    return rng(seed).uniform(-1, 1, int(SR * dur))


def pink(dur, seed=0):
    n = int(SR * dur)
    X = np.fft.rfft(rng(seed).uniform(-1, 1, n))
    f = np.fft.rfftfreq(n, 1 / SR)
    f[0] = 1
    X = X / np.sqrt(f)
    x = np.fft.irfft(X, n)
    return x / (np.max(np.abs(x)) + 1e-9)


def brown(dur, seed=0):
    x = np.cumsum(white(dur, seed))
    return x / (np.max(np.abs(x)) + 1e-9)


# ---------- envelopes ----------
def perc(x, attack=0.005, decay=0.12, curve=3.0):
    """Fast-attack, exponential-decay percussive envelope."""
    n = len(x)
    tt = np.arange(n) / SR
    env = np.ones(n)
    a = max(1, int(attack * SR))
    env[:a] = np.linspace(0, 1, a)
    env[a:] = np.exp(-curve * (tt[a:] - tt[a]) / max(decay, 1e-3))
    return x * env


def adsr(x, a=0.01, d=0.1, s=0.6, r=0.2):
    n = len(x)
    env = np.ones(n)
    ai, di, ri = int(a * SR), int(d * SR), int(r * SR)
    ai, di, ri = min(ai, n), min(di, n - ai if n - ai > 0 else 0), min(ri, n)
    env[:ai] = np.linspace(0, 1, ai)
    env[ai:ai + di] = np.linspace(1, s, di)
    env[ai + di:n - ri] = s
    if ri > 0:
        env[n - ri:] = np.linspace(s, 0, ri)
    return x * env


def fade(x, fin=0.005, fout=0.02):
    n = len(x)
    fi, fo = int(fin * SR), int(fout * SR)
    if fi:
        x[:fi] *= np.linspace(0, 1, fi)
    if fo:
        x[-fo:] *= np.linspace(1, 0, fo)
    return x


# ---------- filters (FFT-based, soft edges) ----------
def _mask(n, edges):
    f = np.fft.rfftfreq(n, 1 / SR)
    return f, edges(f)


def lowpass(x, cutoff, width=0.3):
    n = len(x)
    f, _ = _mask(n, lambda f: f)
    m = 1 / (1 + (f / cutoff) ** 4)          # gentle 4th-order-ish rolloff
    return np.fft.irfft(np.fft.rfft(x) * m, n)


def highpass(x, cutoff):
    n = len(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    m = 1 / (1 + (cutoff / np.maximum(f, 1e-6)) ** 4)
    return np.fft.irfft(np.fft.rfft(x) * m, n)


def bandpass(x, lo, hi, resonance=1.0):
    return highpass(lowpass(x, hi), lo) * resonance


def formant(x, freqs, q=12.0):
    """Emphasise resonant peaks (vowel-ish) for creature voices."""
    n = len(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    m = np.ones_like(f) * 0.15
    for fc in freqs:
        m += np.exp(-((f - fc) ** 2) / (2 * (fc / q) ** 2))
    return np.fft.irfft(np.fft.rfft(x) * m, n)


# ---------- character / space ----------
def bitcrush(x, bits=10, downsample=2):
    q = 2 ** bits
    y = np.round(x * q) / q
    if downsample > 1:
        y = np.repeat(y[::downsample], downsample)[:len(x)]
    return y


def softclip(x, drive=1.5):
    return np.tanh(x * drive)


def tremolo(x, rate=18, depth=0.4):
    return x * (1 - depth + depth * np.sin(2 * np.pi * rate * np.arange(len(x)) / SR))


def reverb(x, decay=0.4, mix=0.3, cutoff=4500, seed=1):
    """Cheap ethereal reverb: convolve with a decaying, low-passed noise IR."""
    ir_len = int(decay * SR)
    ir = white(decay, seed) * np.exp(-4 * np.arange(ir_len) / ir_len)
    ir = lowpass(ir, cutoff)
    ir /= (np.sum(np.abs(ir)) + 1e-9)
    wet = np.convolve(x, ir)[:len(x)]
    return (1 - mix) * x + mix * wet * (np.max(np.abs(x)) / (np.max(np.abs(wet)) + 1e-9))


# ---------- instruments ----------
def bell(base, dur, partials=(1.0, 2.76, 5.4, 8.9), amps=(1, 0.6, 0.35, 0.2),
         decay=0.5, seed=0, detune=0.004):
    """Inharmonic metallic/glassy bell (crystal, chimes)."""
    r = rng(seed)
    out = np.zeros(int(SR * dur))
    for p, a in zip(partials, amps):
        f = base * p * (1 + r.uniform(-detune, detune))
        tone = sine(f, dur)
        out += a * perc(tone, attack=0.002, decay=decay * (1.0 / p ** 0.5), curve=2.0)
    return out / (np.max(np.abs(out)) + 1e-9)


def thud(freq=90, dur=0.28, seed=0, noise=0.4):
    """Deep stony/heavy impact (obsidian, golem)."""
    body = perc(glide(freq * 1.6, freq, dur, curve=2.5), attack=0.002, decay=dur * 0.5, curve=4)
    n = perc(lowpass(white(dur, seed), 1200), attack=0.001, decay=dur * 0.25, curve=6)
    return (body + noise * n) / (1 + noise)


def dig(color="stone", dur=0.22, seed=0):
    """Short material break/step: filtered noise burst + light body."""
    base = pink(dur, seed) if color != "wood" else brown(dur, seed)
    cut = {"stone": 3000, "obsidian": 1800, "crystal": 6000, "wood": 2200, "grass": 3500}.get(color, 3000)
    body = perc(base, attack=0.001, decay=dur * 0.4, curve=7)
    body = lowpass(body, cut)
    if color == "crystal":
        body = body + 0.5 * bell(1400, dur, decay=0.12, seed=seed)
    if color == "wood":
        body = body + 0.4 * perc(sine(200, dur), attack=0.001, decay=0.05, curve=8)
    return body / (np.max(np.abs(body)) + 1e-9)


def voice(base, dur, kind="warble", seed=0, formants=(500, 1200), reverb_mix=0.28):
    """Creature vocalisation: warbling glide through formants (Enderman-ish)."""
    r = rng(seed)
    if kind == "warble":
        vib = 1 + 0.06 * np.sin(2 * np.pi * r.uniform(9, 16) * t(dur))
        base_wave = glide(base * 1.05, base * 0.95, dur, kind="saw") * vib
    elif kind == "down":       # hurt / death descending
        base_wave = glide(base * 1.2, base * 0.5, dur, curve=1.4, kind="saw")
    elif kind == "up":
        base_wave = glide(base * 0.8, base * 1.3, dur, kind="saw")
    else:
        base_wave = saw(base, dur)
    breath = 0.25 * pink(dur, seed + 7)
    x = formant(base_wave + breath, formants)
    x = adsr(x, a=0.02, d=dur * 0.3, s=0.6, r=dur * 0.4)
    x = lowpass(x, 5000)
    return reverb(x, decay=0.35, mix=reverb_mix)


def zap(dur=0.35, seed=0):
    """Energy/laser bolt (crystal sentinel): resonant descending sweep + noise."""
    sweep = glide(2200, 500, dur, curve=1.6, kind="square")
    sweep = bandpass(sweep, 400, 3500, 1.2)
    n = perc(bandpass(white(dur, seed), 800, 4000), attack=0.001, decay=dur * 0.4, curve=5)
    x = perc(sweep, attack=0.002, decay=dur * 0.6, curve=2) + 0.4 * n
    return reverb(x, decay=0.25, mix=0.25)


def roar(base=70, dur=1.8, seed=0):
    """Boss roar: layered low growl + distortion + long reverb tail."""
    r = rng(seed)
    growl = glide(base * 1.3, base * 0.8, dur, curve=1.2, kind="saw")
    growl = growl * (1 + 0.5 * np.sin(2 * np.pi * 30 * t(dur)))   # amplitude growl
    sub = sine(base * 0.5, dur)
    air = 0.3 * lowpass(white(dur, seed), 2500)
    x = softclip(growl + 0.6 * sub + air, drive=2.0)
    x = formant(x, (300, 900, 1800), q=8)
    x = adsr(x, a=0.05, d=0.4, s=0.7, r=dur * 0.4)
    x = lowpass(x, 4000)
    return reverb(x, decay=0.8, mix=0.4, cutoff=3000)


# ---------- combine ----------
def mix(*xs):
    """Sum layers of differing lengths, zero-padding to the longest."""
    n = max(len(x) for x in xs)
    out = np.zeros(n)
    for x in xs:
        x = np.asarray(x, dtype=float)
        out[:len(x)] += x
    return out


# ---------- output ----------
def normalize(x, peak=0.9):
    m = np.max(np.abs(x))
    return x * (peak / m) if m > 1e-9 else x


def master(x, lofi=True, bits=11, ds=1):
    """Final Minecraft-style polish: gentle high roll-off, light bitcrush, normalise."""
    x = lowpass(x, 9000)
    if lofi:
        x = bitcrush(x, bits=bits, downsample=ds)
    x = fade(np.asarray(x, dtype=float), fin=0.003, fout=0.01)
    return normalize(x, 0.92).astype(np.float32)


def loopable(x, xfade=0.15):
    """Crossfade the tail into the head for a seamless ambient loop."""
    n = len(x)
    f = int(xfade * SR)
    if f * 2 >= n:
        return x
    head, tail = x[:f].copy(), x[-f:].copy()
    win = np.linspace(0, 1, f)
    x[:f] = head * win + tail * (1 - win)
    return x[:n - f]
