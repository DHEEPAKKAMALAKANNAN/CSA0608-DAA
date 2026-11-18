"""ShopSphere audit - Module M1: Duplicate-Listing Detector (parts (a), (b) and (g)).

The nightly routine compares every product with every later product:

    FOR i <- 0 TO n-2 DO
      FOR j <- i+1 TO n-1 DO
        IF Product[i].title = Product[j].title AND Product[i].seller = Product[j].seller THEN
          MarkDuplicate(j)

Input size      : n = number of products in the catalogue.
Basic operation : the title comparison in the IF test. It runs on every inner-loop iteration; the
                  seller comparison only runs when the titles match (AND short-circuits).
Derivation      : C(n) = sum_{i=0}^{n-2} (n-1-i) = n(n-1)/2  ->  Theta(n^2) time, Theta(1) extra space.

The program
  1. runs the nested-loop detector on a hand-made catalogue and on random catalogues with planted
     duplicates, counting title and seller comparisons;
  2. checks the count against n(n-1)/2 and the duplicates found against a set-based reference;
  3. doubles n to show the ~4x growth (counts first, wall-clock time second);
  4. runs two redesigns (hash set keyed on (title, seller) and sort-then-scan) and checks that they
     find the same duplicates with far fewer basic operations.
"""
import random

from audit_common import (NIGHTLY_WINDOW_S, N_CURRENT, N_FUTURE, OPS_PER_SECOND, banner, check,
                          fmt_int, fmt_time, min_time, print_table, section, verdict, write_csv)

BRANDS = ["Acme", "Zento", "Nova", "Orbit", "Pixel", "Lumo", "Vertex", "Kiva", "Aero", "Mira"]
ITEMS = ["USB-C Cable", "Steel Bottle", "Desk Lamp", "Yoga Mat", "Wireless Mouse", "Backpack",
         "Smart Watch", "Tea Kettle", "Phone Case", "Earbuds", "Notebook", "Power Bank"]


# --------------------------------------------------------------------------- data generation
def make_catalogue(n_unique, n_duplicates, seed=42):
    """Build a catalogue of (title, seller) pairs with exactly n_duplicates planted re-uploads.

    Titles are shared between sellers (as on a real marketplace), so title matches also happen for
    non-duplicates and the seller comparison is exercised. Every (title, seller) pair of the first
    n_unique products is distinct; then n_duplicates distinct products are uploaded a second time.
    """
    rng = random.Random(seed)
    n_titles = max(4, n_unique // 3)                       # ~3 sellers per title on average
    titles = [f"{rng.choice(BRANDS)} {rng.choice(ITEMS)} M{k:05d}" for k in range(n_titles)]
    sellers = [f"seller-{k:03d}" for k in range(60)]
    used, catalogue = set(), []
    while len(catalogue) < n_unique:
        product = (rng.choice(titles), rng.choice(sellers))
        if product not in used:
            used.add(product)
            catalogue.append(product)
    catalogue += rng.sample(catalogue, n_duplicates)        # re-uploads of existing products
    rng.shuffle(catalogue)
    return catalogue


def reference_duplicates(catalogue):
    """Reference answer: index j is a duplicate if the same (title, seller) appeared before j."""
    seen, duplicates = set(), set()
    for j, product in enumerate(catalogue):
        if product in seen:
            duplicates.add(j)
        seen.add(product)
    return duplicates


# --------------------------------------------------------------------------- current module M1
def detect_duplicates_nested(catalogue):
    """The audited nested-loop detector. Returns (marked indexes, title comparisons, seller comps)."""
    n = len(catalogue)
    title_comparisons = seller_comparisons = 0
    marked = set()
    for i in range(0, n - 1):                    # FOR i <- 0 TO n-2
        title_i, seller_i = catalogue[i]
        for j in range(i + 1, n):                # FOR j <- i+1 TO n-1
            title_comparisons += 1               # basic operation: Product[i].title = Product[j].title
            if title_i == catalogue[j][0]:
                seller_comparisons += 1          # evaluated only when the titles match
                if seller_i == catalogue[j][1]:
                    marked.add(j)                # MarkDuplicate(j)
    return marked, title_comparisons, seller_comparisons


def closed_form(n):
    """Derived number of title comparisons C(n) = n(n-1)/2."""
    return n * (n - 1) // 2


# --------------------------------------------------------------------------- redesigns
def detect_duplicates_hash(catalogue):
    """Redesign A: one pass with a hash set keyed on (title, seller). Theta(n) expected time."""
    seen, marked, lookups = set(), set(), 0
    for j, key in enumerate(catalogue):
        lookups += 1                             # basic operation: one hash-set membership test
        if key in seen:
            marked.add(j)
        else:
            seen.add(key)
    return marked, lookups


def merge_sort(items, key, counter):
    """Hand-written stable merge sort; counter[0] counts key comparisons."""
    if len(items) <= 1:
        return items
    mid = len(items) // 2
    left, right = merge_sort(items[:mid], key, counter), merge_sort(items[mid:], key, counter)
    out, a, b = [], 0, 0
    while a < len(left) and b < len(right):
        counter[0] += 1
        if key(left[a]) <= key(right[b]):
            out.append(left[a])
            a += 1
        else:
            out.append(right[b])
            b += 1
    return out + left[a:] + right[b:]


def detect_duplicates_sort_scan(catalogue):
    """Redesign B: sort indexes by (title, seller, index), then compare neighbours. Theta(n log n)."""
    counter = [0]
    order = merge_sort(list(range(len(catalogue))), lambda k: (catalogue[k], k), counter)
    marked = set()
    for a, b in zip(order, order[1:]):
        counter[0] += 1                          # adjacent comparison
        if catalogue[a] == catalogue[b]:
            marked.add(b)                        # the later upload (larger index) is the duplicate
    return marked, counter[0]


def main():
    banner("ShopSphere audit - M1 Duplicate-Listing Detector (nested loops)")

    section("1. Test cases on a hand-made catalogue (expected / actual / PASS|FAIL)")
    demo = [("Steel Bottle 1L", "seller-07"), ("Desk Lamp", "seller-02"),
            ("Steel Bottle 1L", "seller-03"), ("Steel Bottle 1L", "seller-07"),
            ("Yoga Mat", "seller-02"), ("Desk Lamp", "seller-02")]
    marked, t_cmp, s_cmp = detect_duplicates_nested(demo)
    ok = check("duplicates marked (indexes)", [3, 5], sorted(marked))
    ok &= check("title comparisons = n(n-1)/2 = 6*5/2", 15, t_cmp)
    ok &= check("seller comparisons (only title matches)", 4, s_cmp)
    ok &= check("n = 0 -> comparisons", 0, detect_duplicates_nested([])[1])
    ok &= check("n = 1 -> comparisons", 0, detect_duplicates_nested(demo[:1])[1])
    ok &= check("n = 2 -> comparisons", 1, detect_duplicates_nested(demo[:2])[1])

    section("2. Counted comparisons vs C(n) = n(n-1)/2 on random catalogues (2% planted duplicates)")
    rows, csv_rows, prev = [], [], None
    for n in (500, 1000, 2000, 4000):
        cat = make_catalogue(n - n // 50, n // 50, seed=n)
        marked, t_cmp, s_cmp = detect_duplicates_nested(cat)
        found_ok = marked == reference_duplicates(cat) and len(marked) == n // 50
        seconds = min_time(detect_duplicates_nested, cat, repeats=3)
        growth = f"{t_cmp / prev[0]:.3f}" if prev else "-"
        t_growth = f"{seconds / prev[1]:.2f}" if prev else "-"
        ok &= t_cmp == closed_form(n) and found_ok
        rows.append([fmt_int(n), fmt_int(t_cmp), fmt_int(closed_form(n)), verdict(t_cmp == closed_form(n)),
                     fmt_int(s_cmp), f"{len(marked)}/{n // 50} {verdict(found_ok)}", growth,
                     f"{seconds:.3f}", t_growth])
        csv_rows.append([n, t_cmp, closed_form(n), s_cmp, len(marked), n // 50, f"{seconds:.6f}"])
        prev = (t_cmp, seconds)
    print_table(["n", "title cmps (counted)", "n(n-1)/2", "match", "seller cmps", "dups found",
                 "C(n)/C(n/2)", "time (s)", "time ratio"], rows)
    write_csv("m1_comparisons.csv", ["n", "title_comparisons", "closed_form", "seller_comparisons",
                                     "duplicates_found", "duplicates_planted", "seconds"], csv_rows)
    print("Doubling n multiplies the comparisons by (2n)(2n-1)/(n(n-1)) -> 4: quadratic growth.")

    section("3. Redesigns on the same catalogue (n = 4,000)")
    cat = make_catalogue(4000 - 80, 80, seed=4000)
    ref = reference_duplicates(cat)
    nested = detect_duplicates_nested(cat)
    hashed = detect_duplicates_hash(cat)
    sorted_scan = detect_duplicates_sort_scan(cat)
    print_table(["design", "basic operations", "growth", "same duplicates?"],
                [["nested loops (current)", fmt_int(nested[1]), "Theta(n^2)", verdict(nested[0] == ref)],
                 ["hash set on (title, seller)", fmt_int(hashed[1]), "Theta(n) expected",
                  verdict(hashed[0] == ref)],
                 ["sort + adjacent scan", fmt_int(sorted_scan[1]), "Theta(n log n)",
                  verdict(sorted_scan[0] == ref)]])
    ok &= nested[0] == hashed[0] == sorted_scan[0] == ref

    section(f"4. Projection at {OPS_PER_SECOND:.0e} basic operations per second (window = 600 s)")
    rows = []
    for n in (N_CURRENT, N_FUTURE):
        ops = closed_form(n)
        secs = ops / OPS_PER_SECOND
        rows.append([fmt_int(n), fmt_int(ops), f"{secs:,.1f}", fmt_time(secs),
                     verdict(secs <= NIGHTLY_WINDOW_S)])
    print_table(["n", "comparisons n(n-1)/2", "seconds", "readable", "fits 10 min?"], rows)

    print(f"\nOverall self-check: {verdict(ok)}")


if __name__ == "__main__":
    main()
