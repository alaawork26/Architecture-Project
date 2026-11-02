"""Digital Logic Design Project
Truth table, K-Map / Boolean simplification, logic circuit, decoder.
Run:  python dld_project.py
"""
import re

LETTERS = "ABCDEF"
MAX_VARS = len(LETTERS)

HELP = """
Enter ANY Boolean function. You can use:
  AND : A*B   A&B   A AND B   or just write them together: AB
  OR  : A+B   A|B   A OR B
  NOT : A'    ~A    !A    NOT A
  XOR : A^B   A XOR B
  Constants 0 and 1, and parentheses ( )
  Or give minterms:  m(1,3,5,7)
Examples:  A'B + C      (A+B)(C+D')      A^B^C      m(0,2,5)
"""


# ------------------------------------------------------------------
# Parsing a Boolean expression
# ------------------------------------------------------------------
TOKEN_RE = re.compile(r"\s*(AND|OR|NOT|XOR|[A-Z]|[01]|[()+*&|~!^'])")
ALIAS = {"AND": "&", "*": "&", "OR": "|", "+": "|",
         "NOT": "~", "!": "~", "XOR": "^"}


def tokenize(text):
    text = text.upper().strip()
    tokens, pos = [], 0
    while pos < len(text):
        m = TOKEN_RE.match(text, pos)
        if not m:
            raise ValueError(f"Unexpected character '{text[pos:].strip()[0]}'")
        tok = m.group(1)
        tokens.append(ALIAS.get(tok, tok))
        pos = m.end()
    return tokens


def parse_expression(text, names):
    """Return a tree: ('var',x) ('const',0/1) ('~',a) ('&',a,b) ('|',a,b) ('^',a,b)"""
    tokens = tokenize(text)
    if not tokens:
        raise ValueError("Empty expression")
    starts = set(names) | {"0", "1", "(", "~"}
    pos = [0]

    def peek():
        return tokens[pos[0]] if pos[0] < len(tokens) else None

    def take():
        tok = peek()
        pos[0] += 1
        return tok

    def parse_or():
        node = parse_xor()
        while peek() == "|":
            take()
            node = ("|", node, parse_xor())
        return node

    def parse_xor():
        node = parse_and()
        while peek() == "^":
            take()
            node = ("^", node, parse_and())
        return node

    def parse_and():
        node = parse_unary()
        while True:
            if peek() == "&":
                take()
                node = ("&", node, parse_unary())
            elif peek() in starts:          # implicit AND:  AB, A(B+C)
                node = ("&", node, parse_unary())
            else:
                return node

    def parse_unary():
        if peek() == "~":
            take()
            return ("~", parse_unary())
        node = parse_primary()
        while peek() == "'":                # postfix NOT:  A'
            take()
            node = ("~", node)
        return node

    def parse_primary():
        tok = take()
        if tok is None:
            raise ValueError("Expression ended unexpectedly")
        if tok == "(":
            node = parse_or()
            if take() != ")":
                raise ValueError("Missing closing parenthesis ')'")
            return node
        if tok in ("0", "1"):
            return ("const", int(tok))
        if len(tok) == 1 and tok.isalpha():
            if tok not in names:
                raise ValueError(
                    f"Variable '{tok}' is not allowed. Use only: {', '.join(names)}")
            return ("var", tok)
        raise ValueError(f"Unexpected '{tok}'")

    tree = parse_or()
    if pos[0] != len(tokens):
        raise ValueError(f"Unexpected '{peek()}'")
    return tree


def evaluate(node, env):
    op = node[0]
    if op == "var":
        return env[node[1]]
    if op == "const":
        return node[1]
    if op == "~":
        return 1 - evaluate(node[1], env)
    a, b = evaluate(node[1], env), evaluate(node[2], env)
    if op == "&":
        return a & b
    if op == "|":
        return a | b
    return a ^ b


# ------------------------------------------------------------------
# Input and truth table
# ------------------------------------------------------------------
def bits_of(i, n):
    return [int(b) for b in format(i, f"0{n}b")]


def ask_number_of_variables():
    while True:
        s = input(f"Enter the number of input variables (1-{MAX_VARS}): ").strip()
        if s.isdigit() and 1 <= int(s) <= MAX_VARS:
            return int(s)
        print(f"Invalid input. Enter a whole number from 1 to {MAX_VARS}.")


def read_function(n, names):
    """Ask for a Boolean function; return the list of outputs (one per row)."""
    print(f"\nVariables: {', '.join(names)}  ({names[0]} is the MSB)")
    print(HELP)
    while True:
        text = input("F = ").strip()
        try:
            m = re.fullmatch(r"[mM]\s*\(?\s*([\d,\s]*)\)?", text)
            if m:
                nums = [int(x) for x in re.split(r"[,\s]+", m.group(1).strip()) if x]
                if not nums:
                    raise ValueError("Enter at least one minterm, e.g. m(1,3)")
                bad = [x for x in nums if x >= 2 ** n]
                if bad:
                    raise ValueError(f"Minterm {bad[0]} is out of range (0-{2 ** n - 1})")
                return [1 if i in nums else 0 for i in range(2 ** n)]
            tree = parse_expression(text, names)
            return [evaluate(tree, dict(zip(names, bits_of(i, n))))
                    for i in range(2 ** n)]
        except ValueError as err:
            print(f"Invalid function: {err}. Try again.")


def show_truth_table(outputs, n, names):
    print("\nTruth table")
    print(" ".join(names) + " | F")
    print("-" * (2 * n) + "+--")
    for i, out in enumerate(outputs):
        print(" ".join(map(str, bits_of(i, n))) + " | " + str(out))


# ------------------------------------------------------------------
# Simplification (Quine-McCluskey gives the same result as a K-Map)
# A term is a string like "1-0": 1 = X, 0 = X', - = not used
# ------------------------------------------------------------------
def literals(term, names):
    return [names[i] + ("" if b == "1" else "'")
            for i, b in enumerate(term) if b != "-"]


def term_text(term, names):
    return "".join(literals(term, names)) or "1"


def sop_text(terms, names):
    return " + ".join(term_text(t, names) for t in terms) if terms else "0"


def covers(term, m, n):
    bits = format(m, f"0{n}b")
    return all(t in ("-", b) for t, b in zip(term, bits))


def combine(a, b):
    diff = [i for i in range(len(a)) if a[i] != b[i]]
    if len(diff) == 1 and "-" not in (a[diff[0]], b[diff[0]]):
        i = diff[0]
        return a[:i] + "-" + a[i + 1:]
    return None


def simplify(minterms, n):
    """Return (chosen_terms, prime_implicants, merge_steps)."""
    if not minterms:
        return [], [], []
    current = {format(m, f"0{n}b") for m in minterms}
    primes, steps, seen = set(), [], set()
    while current:
        used, nxt = set(), set()
        ordered = sorted(current)
        for i, a in enumerate(ordered):
            for b in ordered[i + 1:]:
                merged = combine(a, b)
                if merged:
                    used.update((a, b))
                    nxt.add(merged)
                    if merged not in seen:
                        seen.add(merged)
                        steps.append((a, b, merged))
        primes |= current - used
        current = nxt
    primes = sorted(primes)

    # choose the cover: essential primes first, then greedy
    chosen, remaining = [], set(minterms)
    for m in minterms:
        owners = [p for p in primes if covers(p, m, n)]
        if len(owners) == 1 and owners[0] not in chosen:
            chosen.append(owners[0])
    for p in chosen:
        remaining -= {m for m in remaining if covers(p, m, n)}
    while remaining:
        best = max(primes, key=lambda p: sum(covers(p, m, n) for m in remaining))
        chosen.append(best)
        remaining -= {m for m in remaining if covers(best, m, n)}
    return sorted(chosen), primes, steps


# ------------------------------------------------------------------
# Option 1: K-Map
# ------------------------------------------------------------------
def gray(k):
    if k == 0:
        return [""]
    return [format(i ^ (i >> 1), f"0{k}b") for i in range(2 ** k)]


def option_kmap(outputs, n, names, minterms):
    r = n // 2
    c = n - r
    rows, cols = gray(r), gray(c)
    corner = f"{names[:r]}\\{names[r:]}"
    lw = max(len(corner), r)
    w = c + 1
    print("\nK-Map")
    print(corner.ljust(lw) + " | " + " ".join(cb.center(w) for cb in cols))
    print("-" * lw + "-+-" + "-" * (len(cols) * (w + 1) - 1))
    for rb in rows:
        cells = " ".join(str(outputs[int(rb + cb, 2)]).center(w) for cb in cols)
        print(rb.ljust(lw) + " | " + cells)

    chosen, _, _ = simplify(minterms, n)
    print("\nGroups:")
    if not chosen:
        print("  (no 1s in the map)")
    for t in chosen:
        ms = [m for m in minterms if covers(t, m, n)]
        print(f"  {term_text(t, names):<8} covers minterms {ms}")
    print(f"\nSimplified:  F = {sop_text(chosen, names)}")


# ------------------------------------------------------------------
# Option 2: Boolean algebra
# ------------------------------------------------------------------
def option_algebra(n, names, minterms):
    chosen, primes, steps = simplify(minterms, n)
    if not minterms:
        print("\nF is 0 for every input, so F = 0.")
        return
    full = [format(m, f"0{n}b") for m in minterms]
    print("\nStep 1 - Canonical form (sum of minterms):")
    print(f"  F = {sop_text(full, names)}")

    print("\nStep 2 - Combine terms that differ in ONE variable (X + X' = 1):")
    if not steps:
        print("  No two terms can be combined.")
    for a, b, m in steps:
        idx = next(i for i in range(n) if a[i] != b[i])
        v = names[idx]
        print(f"  {term_text(a, names)} + {term_text(b, names)} = "
              f"{term_text(m, names)}    ({v} + {v}' = 1)")

    print("\nStep 3 - Keep only the terms that are needed:")
    dropped = [p for p in primes if p not in chosen]
    if dropped:
        print("  Redundant (already covered): " +
              ", ".join(term_text(p, names) for p in dropped))
    else:
        print("  No redundant terms.")
    print(f"\nSimplified:  F = {sop_text(chosen, names)}")


# ------------------------------------------------------------------
# Option 3: Logic circuit (text drawing)
# ------------------------------------------------------------------
def draw_gate(inputs, gate, out):
    k = len(inputs)
    mid = k // 2
    w = max(len(x) for x in inputs)
    for i, lab in enumerate(inputs):
        ch = "+" if i in (0, k - 1) else "|"
        line = f"  {lab:<{w}} ---{ch}"
        if i == mid:
            line += f"--[{gate}]--- {out}"
        print(line)
    print()


def option_circuit(n, names, minterms):
    chosen, _, _ = simplify(minterms, n)
    print(f"\nLogic circuit for F = {sop_text(chosen, names)}\n")
    if not chosen:
        print("F = 0  (output tied to ground)")
        return
    if chosen == ["-" * n]:
        print("F = 1  (output tied to VCC)")
        return

    lits = [literals(t, names) for t in chosen]
    nots = sorted({x[0] for group in lits for x in group if x.endswith("'")})
    if nots:
        print("NOT gates needed: " + ", ".join(f"{v}' = NOT {v}" for v in nots) + "\n")

    outs = []
    for i, group in enumerate(lits):
        if len(group) == 1:
            outs.append(group[0])
        else:
            name = "F" if len(lits) == 1 else f"T{i + 1}"
            draw_gate(group, "AND", name)
            outs.append(name)
    if len(outs) > 1:
        draw_gate(outs, "OR", "F")
    elif len(lits[0]) == 1:
        print(f"F = {outs[0]}  (a single wire)")


# ------------------------------------------------------------------
# Option 4: Decoder
# ------------------------------------------------------------------
def option_decoder(n, names, minterms):
    size = 2 ** n
    print(f"\nF = sum of minterms {minterms if minterms else '(none)'}")
    print(f"Using a {n}-to-{size} decoder ({names[0]} = MSB) and one OR gate:\n")
    border = "+" + "-" * 13 + "+"
    print(" " * 8 + border)
    for r in range(size):
        left = f"{names[r]} --" if r < n else ""
        title = f"{n}-to-{size}" if r == size // 2 else ""
        tag = " --> OR" if r in minterms else ""
        print(f"  {left:<6}|{title:^13}|-- D{r}{tag}")
    print(" " * 8 + border)
    if minterms:
        print("\nF = " + " + ".join(f"D{m}" for m in minterms) + "   (OR of the marked outputs)")
    else:
        print("\nNo outputs are connected, so F = 0.")


# ------------------------------------------------------------------
# Main program
# ------------------------------------------------------------------


MENU = """
===== MENU =====
1. Simplify using K-Map
2. Simplify using Boolean Algebra
3. Draw the logic circuit
4. Implement using a Decoder
5. Exit"""


def main():
    while True:

        print("=== Digital Logic Design Project ===\n")
        n = ask_number_of_variables()
        names = LETTERS[:n]
        outputs = read_function(n, names)
        minterms = [i for i, o in enumerate(outputs) if o]
        show_truth_table(outputs, n, names)

        while True:
            print(MENU)
            choice = input("Choose an option (1-5): ").strip()
            if choice == "1":
                option_kmap(outputs, n, names, minterms)
            elif choice == "2":
                option_algebra(n, names, minterms)
            elif choice == "3":
                option_circuit(n, names, minterms)
            elif choice == "4":
                option_decoder(n, names, minterms)
            elif choice == "5":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number from 1 to 5.")
            


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
