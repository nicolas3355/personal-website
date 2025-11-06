## Polynomial Intersection via Grand-Product Arguments

In many modern SNARK systems (most notably **PLONK**) we often need to prove that two sets of polynomial evaluations are the same *up to permutation*.
This arises in **copy constraints**, where a prover must show that certain wires in a circuit carry the same value, even though they may appear in different columns or positions in the evaluation table.

At its heart, this problem is purely algebraic:
given two low-degree polynomials $f_1$ and $f_2$, we want to prove that their evaluations **intersect** over a known domain $D$. 
That is, for some permutation $\sigma$, we want to show:
<div> 
\[
\\{f_1(d_i) \\}_{i=0}^{n-1} = \\{ f_2(d_{\sigma(i)}) \\}_{i=0}^{n-1}
\]
</div>

The **grand-product argument** is the elegant algebraic trick that makes this possible with only constant-size proofs.
It transforms the set equality condition into a single multiplicative relation that can be verified by checking that a certain *running product polynomial* $Z(X)$ behaves consistently across the domain.

---

### Setup

Let $D = { d_0, \dots, d_{n-1} } \subset \mathbb{F}_p$ be a public evaluation domain with **vanishing polynomial**

$$
V_D(X) = \prod_{i=0}^{n-1} (X - d_i).
$$

Suppose two polynomials $f_1, f_2 \in \mathbb{F}_p[X]$ are committed under KZG commitments:

$$
C_1 = \mathsf{KZG}(f_1), \qquad C_2 = \mathsf{KZG}(f_2).
$$

We wish to prove that **the evaluations of $f_1$ and $f_2$ coincide up to a permutation** of the domain $D$.
Let $\sigma$ be such a permutation, encoded by a low-degree permutation polynomial $\pi$ satisfying

$$
\pi(d_i) = d_{\sigma(i)}.
$$

---

### Constructing the Grand Product Polynomial

The prover defines a *running product* polynomial $Z(X)$ of degree ≤ n by the recurrence:

$$
Z(d_0) = 1, \qquad
Z(d_{i+1}) = Z(d_i) \cdot \frac{f_1(d_i)}{f_2(\pi(d_i))}, \quad (i = 0, \dots, n-2).
$$

Intuitively, if all ratios $f_1(d_i) / f_2(\pi(d_i)) = 1$,
then $Z(d_n) = 1$.
Otherwise, the product accumulates any discrepancy.

This construction encodes the **permutation check** between the evaluations of $f_1$ and $f_2$.

---

### Encoding the Recurrence as a Polynomial Identity

To express the recurrence in polynomial form, define a *next-point* map $\tau$ on $D$ such that

$$
\tau(d_i) = d_{i+1}.
$$

Now form the polynomial

$$
P(X) = Z(\tau(X)) f_2(\pi(X)) - Z(X) f_1(X).
$$

By construction,
$P(x) = 0$ for all $x \in D$ **if and only if** the recurrence holds for every adjacent pair in the domain.

The prover then defines a quotient polynomial $Q(X)$ such that

$$
P(X) = Q(X) , V_D(X),
$$
which enforces the vanishing condition over $D$.

---

### Commitments and Proof

The prover sends:

$$
C_Z = \mathsf{KZG}(Z(X)), \qquad C_Q = \mathsf{KZG}(Q(X)).
$$

Using Fiat–Shamir, the verifier samples a random evaluation point $z \notin D$,
and the prover provides constant-size KZG openings at $z$ and $\tau(z)$ for:

$$
Z(X), \quad f_1(X), \quad f_2(\pi(X)), \quad Q(X).
$$

---

### Verification Steps

1. **Initialization check:** verify $Z(d_0) = 1$ via an opening at $d_0$.
2. **Recurrence check:**
   $$
   P(z) = Z(\tau(z)) f_2(\pi(z)) - Z(z) f_1(z).
   $$
3. **Quotient relation:**
   $$
   P(z) = Q(z) , V_D(z).
   $$

All of these checks can be verified using **one pairing equation** through batched openings
(as described in the *PLONK* paper, p. 13).

---

### Soundness Intuition

Soundness of the grand-product argument ensures:

$$
\prod_{i=0}^{n-1} \frac{f_1(d_i)}{f_2(d_{\sigma(i)})} = 1,
$$

which implies that the multisets of evaluations coincide:

$$
{ f_1(d_i) } = { f_2(d_{\sigma(i)}) }.
$$

In other words, the prover convinces the verifier that
**the two committed polynomials evaluate to the same values up to a known permutation of the domain**.

