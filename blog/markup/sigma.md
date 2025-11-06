# Sigma Protocols and How to OR Them

Σ-protocols (Sigma protocols) are a family of **three-move interactive proofs of knowledge** that let a prover convince a verifier that they know a secret witness satisfying some public relation (without revealing the witness itself).

They form the foundation of many zero-knowledge constructions such as Schnorr proofs, range proofs, and zkSNARK components.

At their core, all Σ-protocols follow a simple template:

1. **Commit:** the prover commits to a random value.
2. **Challenge:** the verifier sends a random challenge.
3. **Response:** the prover replies with a value that “binds” the commitment to the secret.

---

## What we’ll cover

1. **Warm-up: Schnorr proof of knowledge (PoK) of a discrete log.**
   The canonical Σ-protocol: prove knowledge of $x$ such that $X = g^x$.

2. **OR-composition of Σ-protocols.**
   The simulate-one / prove-one pattern: tie two branches with a *single* global challenge so you can’t fake both.

3. **Three Σ-protocols over Pedersen commitments ($C = g^r h^m$):**

    * **PoK of the opening** $(r,m)$.
    * **Equality to a known constant**: prove $m = m^*$ without revealing $r$.
    * **Bitness**: prove $m \in \{0,1\}$ via an **OR-proof**. Ergo, show $C = g^{r}$ **or** $C = g^{r}h$ without revealing which.

---

## Schnorr Proof of Knowledge of a Discrete Log

Recall the classic Σ-protocol for proving knowledge of a discrete logarithm.

We work in a cyclic group $G = \langle g \rangle$ of order $q$.
The public value is $X = g^{x}$, and the prover wishes to prove knowledge of $x$ without revealing it.

### Protocol

**Prover** (knows $x$)

1. Pick $k \leftarrow \mathbb{Z}_q$.
2. Send $T = g^{k}$.
3. Receive challenge $e \leftarrow \mathbb{Z}_q$.
4. Compute $s = k - e x \bmod q$.
5. Send $s$.

**Verifier**
Check
$$
g^{s} \stackrel{?}{=} T \cdot X^{e}.
$$
Accept if true.

**Fiat–Shamir (Non-interactive)**
Set $e = H(g, X, T)$ for a hash function $H$.
Then the transcript $(T, s)$ is a non-interactive proof of knowledge of $x$.

> 💡 **Intuition:** The prover blinds $x$ with randomness $k$.
> The verifier’s challenge $e$ forces the prover to “open” this commitment consistently,
> so only someone who knows $x$ can produce a valid response.

---

## 🔀 Combining Two Σ-Protocols: The OR-Proof Skeleton

Before we move on to commitments, it’s useful to see how to **combine two Σ-protocols** into an **OR-proof** — one that proves knowledge of *either* of two secrets, without revealing which.

### OR-Proof Skeleton (you know $x_1$, don’t know $x_2$)

**Public:** $(g, q, y_1 = g^{x_1}, y_2 = g^{x_2})$

1. **Commit phase (before global challenge $e$):**

    * **Real branch (#1):**
     pick $k_1 \leftarrow \mathbb{Z}_q$; set $t_1 = g^{k_1}$.

    * **Fake branch (#2):**
     pick $e_2, s_2 \leftarrow \mathbb{Z}_q$ independently at random,
     then set
     $$
     t_2 := g^{s_2} \, y_2^{e_2}.
     $$
     This makes $(t_2, e_2, s_2)$ a *valid-looking* Schnorr transcript without needing $x_2$.

     Send $(t_1, t_2)$.

2. **Challenge:**
   Verifier sends global $e \leftarrow \mathbb{Z}_q$.
   Split it as $e_1 = (e - e_2) \bmod q$.

3. **Responses:**

   * **Real branch (#1):** compute $s_1 = k_1 - e_1 x_1 \bmod q$.
   * **Fake branch (#2):** already have $s_2$.
     Send $(e_1, e_2, s_1, s_2)$.

4. **Verifier checks:**

    * $e \stackrel{?}{=} (e_1 + e_2) \bmod q$
    * $g^{s_1} y_1^{e_1} \stackrel{?}{=} t_1$
    * $g^{s_2} y_2^{e_2} \stackrel{?}{=} t_2$

> 💡 **Intuition:** You “prove one and simulate one.”
> The fake branch looks valid because you chose $e_2, s_2$ to satisfy the equation synthetically.
> The real branch ties to your secret through $e_1 = e - e_2$.
> The global challenge ensures you can’t fake both simultaneously.

This pattern will be reused later to prove that a Pedersen commitment hides a bit $m \in \{0,1\}$.

---

## 🔒 From Schnorr to Commitments

Schnorr proofs handle a single secret exponent.
Pedersen commitments extend this by hiding **two unknowns** $(r, m)$:
$$
C = g^{r} h^{m},
$$
where $g, h$ are independent generators of the same group.

The same Σ-protocol logic applies — we just track two exponents.

> 💡 **Intuition:** The commitment $C$ binds two secrets:
> $r$ (randomness) ensures *hiding*, while $m$ ensures *binding*.

---

## 1️⃣ Proof of Knowledge of the Opening $(r, m)$

**Goal:** Prove knowledge of $(r, m)$ such that $C = g^{r} h^{m}$.

**Prover (knows $r, m$):**

1. Pick $k_r, k_m \leftarrow \mathbb{Z}_q$.
2. Send $T = g^{k_r} h^{k_m}$.
3. Receive challenge $e \leftarrow \mathbb{Z}_q$.
4. Compute
   $$
   s_r = k_r - e r \bmod q, \quad s_m = k_m - e m \bmod q.
   $$
5. Send $(s_r, s_m)$.

**Verifier:**
Check
$$
g^{s_r} h^{s_m} \stackrel{?}{=} T \cdot C^{e}.
$$

> 💡 **Intuition:** This is just a 2-dimensional Schnorr proof —
> you’re proving knowledge of two linked exponents.

---

## 2️⃣ Proof that the Committed Value Equals a Known Constant $m^*$

**Goal:** Prove that $m = m^*$ without revealing $r$.

Since
$$
C = g^{r} h^{m^*} \iff C \cdot h^{-m^*} = g^{r},
$$
this reduces to a simple Schnorr proof of knowledge of $r$.

Let $C' = C \cdot h^{-m^*} = g^{r}$.

**Protocol:**

1. Pick $k \leftarrow \mathbb{Z}_q$; send $T = g^{k}$.
2. Receive $e \leftarrow \mathbb{Z}_q$.
3. Compute $s = k - e r \bmod q$.
4. Send $s$.
5. Verifier checks
   $$
   g^{s} \stackrel{?}{=} T \cdot (C \cdot h^{-m^*})^{e}.
   $$

> 💡 **Intuition:** Subtracting $m^*$ from the commitment removes the message,
> leaving a plain Schnorr proof of the randomness $r$.

---

## 3️⃣ Proof that $m \in \{0,1\}$ — Bitness via OR of Two Σ-Protocols

We now combine two Σ-protocols into one **OR-proof**, showing that *one of two statements* holds without revealing which.

We want to prove that the committed message is a bit:
$$
m \in \{0,1\}.
$$
Equivalently, $C$ must satisfy either
$$
C = g^{r} \quad \text{or} \quad C = g^{r} h.
$$

That is:

* **Branch 0:** “$m=0$” and know $r$ ⇒ $C = g^{r}$.
* **Branch 1:** “$m=1$” and know $r$ ⇒ $C h^{-1} = g^{r}$.

**Public:** $(g, h, C)$
**Prover:** knows $r$ for one branch.

**Protocol Sketch:**

1. Define targets: $\text{target}_0 = C$, $ \text{target}_1 = C h^{-1}$.
2. Simulate one branch: choose random $ e_{\text{fake}}, s_{\text{fake}} \leftarrow \mathbb{Z}_q $,
   set
   <div> 
   \[
    T_{\text{fake}} = g^{s_{\text{fake}}}, \text{target}_{\text{fake}}^{e_{\text{fake}}}.
    \]
    </div>

3. On the real branch, pick $k$, compute $T_{\text{real}} = g^{k}$.
4. Send $(T_0, T_1)$.
5. Receive global $e \leftarrow \mathbb{Z}_q$; split $e = e_0 + e_1 \bmod q$.
6. Compute $s_{\text{real}} = k - e_{\text{real}} r \bmod q$.
7. Send $(e_0, e_1, s_0, s_1)$.

**Verifier:**

* Check $e = e_0 + e_1 \bmod q$.
* For each branch $b \in \{0,1\}$:
  $$
  g^{s_b} \stackrel{?}{=} T_b \cdot (\text{target}_b)^{e_b}.
  $$
  Accept if all hold.

> 💡 **Intuition:** You prove that your commitment opens to either 0 or 1.
> The real branch ties to your secret, the fake branch is simulated.
> The single global challenge glues both together securely.

