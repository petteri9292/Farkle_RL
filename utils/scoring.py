from itertools import product
from utils.config import RuleSet
import numpy as np


RULES = RuleSet.from_yaml("configs/KCD_4K.yaml")

def legal_keeps(counts, rules):
    best = {}
    for sub in product(*(range(c + 1) for c in counts)):
        sub = np.array(sub)
        k = int(sub.sum())
        if k == 0:
            continue
        s = score_counts(sub, rules)
        if s in (None, 0):
            continue
        if k not in best or s > best[k][0]:
            best[k] = (s, sub)
    return best



def score_counts(counts: tuple[int, ...], rules: RuleSet) -> int:
    """counts[i] = number of dice showing face i+1."""
    total = 0
    counts = np.array(counts)
    
    remaining = counts.copy()
    if "full_straight" in rules.specials and all(c >= 1 for c in counts):
        total += rules.specials["full_straight"]
        remaining = counts - 1
    elif "low_straight" in rules.specials and all(c >= 1 for c in counts[:-1]):
        total += rules.specials["low_straight"]
        remaining = remaining - np.pad(np.ones_like(counts[:-1]),(0,1),"constant")
    elif "high_straight" in rules.specials and all(c >= 1 for c in counts[1:]):
        total += rules.specials["high_straight"]
        remaining = remaining - np.pad(np.ones_like(counts[1:]),(1,0),"constant")
    for face_idx, count in enumerate(remaining):
        face = face_idx + 1
        if count != 0:    
            face_points = 0
            if count >= 3:
                total += rules.n_of_a_kind_score(face, count)
                face_points += rules.n_of_a_kind_score(face, count)
            elif face in rules.singles:
                total += rules.singles[face] * count
                face_points += rules.singles[face] * count
            if face_points == 0:
                return None

    return int(total)