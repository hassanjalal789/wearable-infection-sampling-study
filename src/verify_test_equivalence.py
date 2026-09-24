"""Check: is within-participant sign-flip permutation on the win proportion theta
identical to the exact binomial sign test conditional on discordant pairs?"""
import numpy as np
from scipy.stats import binomtest
rng = np.random.default_rng(42)

def theta(w, l, t, n): return (w + 0.5*t)/n

def perm_p(outcomes, B=200000, rng=rng):
    """outcomes: array of +1 (A wins), -1 (B wins), 0 (tie) per participant.
       Null: schedule label exchangeable within participant -> sign flip."""
    n = len(outcomes)
    obs = theta((outcomes>0).sum(), (outcomes<0).sum(), (outcomes==0).sum(), n)
    flips = rng.choice([-1,1], size=(B,n))
    perm = flips*outcomes
    w = (perm>0).sum(axis=1); l=(perm<0).sum(axis=1); t=(perm==0).sum(axis=1)
    th = (w + 0.5*t)/n
    return (np.abs(th-0.5) >= abs(obs-0.5) - 1e-12).mean(), obs

print(f"{'n':>4} {'W':>4} {'L':>4} {'T':>4} {'theta':>7} {'perm p':>10} {'sign p':>10} {'|diff|':>9}")
for (w,l,t) in [(9,3,18),(12,4,14),(7,7,16),(15,5,10),(6,2,22),(11,3,6),(20,8,12)]:
    n=w+l+t
    o=np.array([1]*w+[-1]*l+[0]*t)
    pp,th=perm_p(o)
    sp=binomtest(w,w+l,0.5).pvalue
    print(f"{n:>4} {w:>4} {l:>4} {t:>4} {th:>7.4f} {pp:>10.5f} {sp:>10.5f} {abs(pp-sp):>9.5f}")
