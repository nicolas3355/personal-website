# When One Random Check Isn’t Many: A Subtle Soundness Trap in Group Tests

**The good news (fields).**
In a lot of crypto, you need to verify a *bunch of equations* at once. Think of equations

$$
E_1=0,\; E_2=0,\; \dots,\; E_s=0
$$

where each $E_i$ is an expression over a large finite field $\mathbb F$ (e.g., constraints of a circuit, polynomial identities, signature checks in a batch). Instead of checking all $s$ equalities separately, you can **batch** them by picking random coefficients $$r_1,\dots,r_s \stackrel{\$}{\leftarrow} \mathbb F$$ and verifying a *single* equation:

$$
\sum_{i=1}^s r_i\,E_i \;\stackrel{?}{=}\; 0 \quad\text{over }\mathbb F.
$$

If at least one $E_i\neq 0$, then (because this is one linear relation over a field) the combined check fails except with probability exactly $1/|\mathbb F|$. When $|\mathbb F|\ge 2^{128}$, that’s **already negligible**. This “random linear batching” is the engine behind Freivalds’ check, Schwartz–Zippel style tests, PCS/IPA batching, and many signature batch verifiers.

**The trap (groups with cofactors).**

We want to convince a verifier that an elliptic-curve group really has **prime order $n$**. A standard necessary-and-sufficient check is

$$
[n]P_i = O \quad \text{for } i=1,\dots,s,
$$

where each $P_i$ is sampled independently (e.g., via hash-to-curve) and $O$ is the identity. If the true group size is actually $N=k\cdot n$ with a cofactor $k\ge2$, then for a random $P$ we have $[n]P$ essentially uniform in a size-$k$ subgroup, so

$$
\Pr([n]P=O)=1/k.
$$

Independence across the $s$ equations gives the **naïve soundness**

$$
\Pr\big(\forall i,\ [n]P_i=O\big)=(1/k)^s,
$$

which is great: exponential decay in $s$.

**Why it’s tempting to batch them like in the field setting.**
From the world of fields, we know a powerful trick: to check many equalities $E_i=0$ over a large field $\mathbb F$, pick random $r_i\in\mathbb F$ and verify a single combined equality $\sum r_i E_i=0$. If any $E_i\neq0$, this fails except with probability $1/|\mathbb F|$ (already negligible). It’s natural to try the **same batching move** here: sample random coefficients $c_1,\dots,c_s$, form one point

$$
Q \;=\; \sum_{i=1}^s [c_i]\,P_i,
$$

and replace the $s$ checks by a **single** group equation

$$
[n]Q \stackrel{?}= O.
$$

**Why that “field-style” batching quietly breaks soundness in groups.**

## Ground-up explanation (no hand-waving)

* **Group and identity.** $G$ is a finite abelian group with identity $O$.
* **Scalar multiplication.** $[n]: G \to G$, $P \mapsto nP$, is a homomorphism.
* **Kernel.** $\ker([n]) = \{ P \in G \mid [n]P = O \}$.
* **Image.** $\mathrm{Im}([n]) = \{ [n]P \mid P \in G \}$.

If $|G| = k n$ with $n$ prime:

* $|\ker([n])| = n$, and $|\mathrm{Im}([n])| = k$.
* Write $H := \mathrm{Im}([n])$; it has exactly $k$ elements.

For random $P$, define $R = [n]P \in H$; then $R$ is (close to) uniform in $H$, so $\Pr(R=O) = 1/k$.

### Naïve test revisited

Pick independent $P_1,\dots,P_s$; set $R_i = [n]P_i \in H$.
Check $[n]P_i = O$ for each $i$. Then

$$
\Pr(\forall i,\; R_i = O) = (1/k)^s.
$$

### “One random linear combo” analyzed

Pick random coefficients $c_1,\dots,c_s$ (from the field $\mathbb{F}_p$), set

$$
Q = \sum_i [c_i] P_i,\qquad \text{check } [n]Q = \sum_i [c_i] R_i = O \text{ in } H.
$$

**Key fact:** on a subgroup of size $k$, multiplying by any integer $c$ depends only on $c \bmod k$. (Because every $h \in H$ satisfies $[k]h = O$, so $[c]h = [\,c \bmod k\,]h$.) Thus only the residues $c_i \bmod k$ matter; with random field coefficients these residues are essentially uniform in $\mathbb{Z}_k$.

Conditioned on the $R_i$ being random (they are), they almost surely generate all of $H$. Then the sum $\sum_i (c_i \bmod k)\, R_i$ is **uniform** in $H$. A uniform element of a $k$-element group is the identity with probability exactly $1/k$. One random linear relation removes **one** degree of freedom—no more.

> **Counting picture (cyclic $H$).** If $H=\langle g\rangle$ and $R_i = b_i g$ (with some $b_i \not\equiv 0 \mod k$), the acceptance condition is one linear equation
> $\sum_i (c_i b_i) \equiv 0 \ (\bmod\ k)$. Among the $k^s$ residue vectors $(c_1,\dots,c_s) \bmod k$, exactly $k^{s-1}$ satisfy it ⇒ probability $1/k$.

**Conclusion:** collapsing $s$ checks into one random linear combination buys you **cost** (one check instead of $s$) but destroys **soundness**, from $(1/k)^s$ down to $1/k$.

**Takeaway.**  Don’t blindly port “one random linear check” from field settings into group settings with cofactors. Count independent constraints, not just operations. That’s the difference between “negligible” and “oops.”
---


## A precise toy example you can hold in your head

Take $G = \mathbb{Z}_{15}$ under addition (identity $0$). We “want” order $n=5$, but the true size is $15 = 3 \cdot 5$, so the cofactor is $k=3$.

* The map $[5]: x \mapsto 5x \pmod{15}$ has
  **image** $\{0,5,10\}$ (size 3) and **kernel** $\{0,3,6,9,12\}$ (size 5).

**Naïve (s=2).** Pick $P_1,P_2 \in \{0,\dots,14\}$ uniformly; set $R_i = 5 P_i \pmod{15}$. Each $R_i$ is uniform in $\{0,5,10\}$ so $\Pr(R_i=0)=1/3$. Both zero with probability $(1/3)^2 = 1/9$.

**Compressed (s=2).** Pick random coefficients $c_1,c_2$; form $Q = c_1 P_1 + c_2 P_2 \pmod{15}$; accept if $5Q \equiv 0$.
This is equivalent to a **single** linear equation modulo 3:
$c_1 (5P_1) + c_2 (5P_2) \equiv 0 \ (\bmod 15)$ ⇔ $(c_1 \bmod 3) (R_1/5) + (c_2 \bmod 3) (R_2/5) \equiv 0 \ (\bmod 3)$.
Exactly one third of coefficient pairs satisfy it ⇒ acceptance probability $1/3$, not $1/9$.




````python
import random
import math

def simulate_small_example(
    N=15, n_claim=5, s_values=(1,2,3,4,5), trials=200_000, p_field=15, seed=123
):
    """
    Monte Carlo on G = Z_N (additive). True size N = k * n_claim.
    - Naive: check [n]P_i == 0 for i=1..s independently  -> expected accept (1/k)^s
    - Compressed: pick random coeffs c_i in F_p, form Q = sum c_i P_i, check [n]Q == 0
      -> conditional on NOT(all [n]P_i==0), accept ~ 1/k exactly.
         Unconditional accept ≈ 1/k + (1/k)^s - (1/k)*(1/k)^s.
    """
    rng = random.Random(seed)
    if N % n_claim != 0:
        raise ValueError("Require N to be a multiple of n_claim.")
    k = N // n_claim  # cofactor
    
    print(f"=== Monte Carlo on Z_{N}, claimed n = {n_claim}, cofactor k = {k}, trials per s = {trials} ===")
    print(f"(Coefficients sampled from F_{p_field}, effectively reduced mod k={k} on the image subgroup)\n")
    header = (
        f"{'s':>2}  {'naive_accept':>13}  {'naive_pred':>11}  "
        f"{'compr_accept':>13}  {'compr_pred(~1/k)':>17}  "
        f"{'compr_accept | not-all-zero':>28}"
    )
    print(header)
    print("-" * len(header))
    
    for s in s_values:
        naive_accept = 0
        comp_accept = 0
        comp_accept_and_notallzero = 0
        comp_notallzero_count = 0
        
        for _ in range(trials):
            # s random points P_i in Z_N
            P = [rng.randrange(N) for _ in range(s)]
            # R_i = [n]P_i = n_claim * P_i mod N  (lies in image subgroup of size k)
            R = [(n_claim * Pi) % N for Pi in P]
            
            # Naive: all R_i must be 0
            if all(r == 0 for r in R):
                naive_accept += 1
            
            # Compressed: random field coeffs, one combined check
            coeffs = [rng.randrange(p_field) for _ in range(s)]
            Q = sum(ci * Pi for ci, Pi in zip(coeffs, P)) % N
            if (n_claim * Q) % N == 0:
                comp_accept += 1
            
            # Conditional acceptance given NOT(all R_i == 0)
            not_all_zero = not all(r == 0 for r in R)
            if not_all_zero:
                comp_notallzero_count += 1
                if (n_claim * Q) % N == 0:
                    comp_accept_and_notallzero += 1
        
        naive_rate = naive_accept / trials
        naive_pred = (1 / k) ** s
        
        comp_rate = comp_accept / trials
        comp_pred = 1 / k  # asymptotically (exact conditional on not-all-zero)
        
        comp_cond_rate = (
            comp_accept_and_notallzero / comp_notallzero_count
            if comp_notallzero_count > 0 else float('nan')
        )
        
        print(
            f"{s:2d}  {naive_rate:13.6f}  {naive_pred:11.6f}  "
            f"{comp_rate:13.6f}  {comp_pred:17.6f}  "
            f"{comp_cond_rate:28.6f}"
        )

if __name__ == "__main__":
    # Default demo: Z_15, n=5 -> k=3
    simulate_small_example()

````


````
=== Monte Carlo on Z_15, claimed n = 5, cofactor k = 3, trials per s = 200000 ===
(Coefficients sampled from F_15, effectively reduced mod k=3 on the image subgroup)

 s   naive_accept   naive_pred   compr_accept   compr_pred(~1/k)   compr_accept | not-all-zero
----------------------------------------------------------------------------------------------
 1       0.333620     0.333333       0.554870           0.333333                      0.332018
 2       0.112160     0.111111       0.408285           0.333333                      0.333534
 3       0.036600     0.037037       0.357465           0.333333                      0.333055
 4       0.012750     0.012346       0.341315           0.333333                      0.332808
 5       0.003980     0.004115       0.334105           0.333333                      0.331444

````

