# Presentation Script — Assignment 2
**COMP-SCI 5592: Design & Analysis of Algorithms**  
**Topic:** Vertex $k$-Labeling of Graphs Using Algorithmic Approach & Comparative NLP Pipeline Analysis  
**Presenters:**
- **Tina Nguyen** (tinanguyen@umkc.edu) — Lead: Graph Labeling & Algorithms (Problem 1)
- **Haoran** (hzwkg@umsystem.edu) — Lead: NLP Pipeline & Performance (Problem 2)

**Duration:** ~12–15 Minutes (includes defense & Q&A)

---

### Slide 1: Title Slide
**Speaker: Tina Nguyen**

> "Good afternoon, Professor and classmates. I am **Tina Nguyen**, and presenting with me today is my teammate, **Haoran**.
>
> Today, we present our algorithmic designs, formal proofs, and empirical benchmarks for Assignment 2 in Design and Analysis of Algorithms:
> 1. In **Problem 1**, we investigate **Vertex $k$-Labeling and Edge Irregularity Strength** on Generalized Petersen Graphs $GP(n, p)$, evaluating exact constraint backtracking and a scalable greedy algorithm against theoretical lower and upper bounds.
> 2. In **Problem 2**, we implement and evaluate a from-scratch **Comparative Natural Language Processing Pipeline** on Shakespeare's Complete Works, examining how Dynamic Programming memoization yields a 2.6x speedup over NLTK.
>
> Let's look at our agenda and division of labor."

---

### Slide 2: Executive Agenda & Work Distribution
**Speaker: Haoran**

> "Thank you, Tina. In strict adherence to the assessment rubric, we established an equitable, specialized distribution of roles:
>
> • **Tina led Problem 1 (Graph Labeling):** She proved the theoretical lower bounds, designed the optimal Adjacency List representation with 2-hop conflict precomputation, implemented the Exact Backtracking solver with coupled spoke traversal, proved $es(GP(12, 5)) = 19$, engineered the $O(n)$ linear-time Greedy Heuristic, and verified the Ship Wheel graph $SW(8, 2)$ from Slide 15.
>
> • **I led Problem 2 (Comparative NLP):** I developed the end-to-end 5-stage NLP pipeline for the 5.46 MB Shakespeare corpus, implemented Martin Porter's 1980 stemmer from scratch in pure Python, introduced Dynamic Programming memoization that achieved a 30x speedup in stemming, benchmarked our pipeline against NLTK across 25% to 100% corpus slices, and conducted the lexical mood vectorization.
>
> Both of us jointly modeled the computational complexity and prepared the technical defense. I will now hand the floor to Tina for Problem 1."

---

### Slide 3: Graph Labeling Theory & Mathematical Bounds
**Speaker: Tina Nguyen**

> "Thank you, Haoran. Let's begin with the mathematical theory of graph labeling.
>
> In 2014, Ahmad, Al-Mushayt, and Bača introduced **Vertex $k$-Labeling**, also called **Edge Irregular $k$-Labeling**. We assign positive integer labels $\phi(v) \in \{1, 2, \dots, k\}$ to each vertex such that each edge receives an induced additive weight:
> $$w(xy) = \phi(x) + \phi(y)$$
> The strict constraint is that **every edge weight must be unique**. The minimum integer $k$ achieving this is the **Edge Irregularity Strength**, denoted $es(G)$.
>
> Ahmad et al. established **Theorem 1**, giving the universal lower bound:
> $$es(G) \ge \max\left( \left\lceil \frac{|E(G)| + 1}{2} \right\rceil, \Delta(G) \right) = O(n)$$
> Why? Because the smallest possible edge weight is $1 + 1 = 2$. With $|E|$ distinct weights, the largest weight must be at least $|E| + 1$. Since the maximum weight is at most $2k$, we have $2k \ge |E| + 1$, yielding $k \ge \lceil(|E|+1)/2\rceil$.
>
> Furthermore, while Ahmad's Theorem 2 established an exponential Fibonacci upper bound $O(\phi^{|V|})$, Asim et al. (2018/2021) proved that algorithmic approaches achieve a practical logarithmic upper bound:
> $$es(G) \le |E| \log_2 |V| = O(n \log n)$$
> This $O(n \log n)$ bound provides a much tighter guarantee for real-world algorithms."

---

### Slide 4: Problem 1 — Generalized Petersen Graphs $GP(n, p)$
**Speaker: Tina Nguyen**

> "Our primary target graph family is the **Generalized Petersen Graph $GP(n, p)$**.
>
> For $n \ge 3$ and $1 \le p < n/2$, $GP(n, p)$ is a 3-regular cubic graph containing:
> • Order $|V| = 2n$: an outer cycle of $n$ vertices $u_0 \dots u_{n-1}$, and an inner star of $n$ vertices $v_0 \dots v_{n-1}$.  
> • Size $|E| = 3n$: $n$ outer cycle edges, $n$ radial spokes $(u_i, v_i)$, and $n$ inner star edges $(v_i, v_{(i+p) \bmod n})$.
>
> Substituting $|E| = 3n$ and $\Delta = 3$ into Theorem 1 yields our theoretical lower bound:
> $$es(GP(n, p)) \ge \left\lceil \frac{3n + 1}{2} \right\rceil$$
>
> Slide 14 tasked us with four core questions:
> 1. What is the best data structure to store this graph?
> 2. What algorithm design method should we use?
> 3. What is the optimal traversal technique?
> 4. What are the time complexity $T(V, E)$ and hardware resource limits?
>
> Let's look at how we answered each question."

---

### Slide 5: Algorithmic Methods: Brute Force vs. Backtracking vs. Greedy
**Speaker: Tina Nguyen**

> "To solve vertex $k$-labeling, we analyzed three algorithmic paradigms:
>
> 1. **Why Pure Brute Force Fails:**
> An exhaustive brute-force search generates all $k^{|V|} = k^{2n}$ possible vertex assignments. For $GP(12, 5)$ where $k=19$ and $|V|=24$, the state space contains $19^{24} \approx 6.2 \times 10^{30}$ states! Testing each state takes $O(|E|)$ time, making pure brute force completely intractable.
>
> 2. **Method 1: Constraint Backtracking with Pruning (Algorithm 1):**
> Instead of brute force, we designed a constraint satisfaction branch-and-bound solver with two key pruning innovations:
> • **2-Hop Conflict Table:** In any edge-irregular labeling, **no two neighbors of any vertex can ever share a label**—otherwise their incident edges would produce identical weights. Precomputing 2-hop neighbors allows $O(1)$ pruning of forbidden candidate labels.
> • **Coupled Spoke Traversal:** Instead of traversing the outer cycle first, we interleave vertices: $[u_0, v_0, u_1, v_1, \dots]$. The spoke edge $(u_i, v_i)$ is evaluated immediately at step $2i+1$ instead of step $n+1$. Weight collisions are detected at shallow depths, collapsing the effective branching factor from 19 to just $b_{\text{eff}} \approx 1.15$!
>
> 3. **Method 2: Greedy Constructive Heuristic (Algorithm 2):**
> For massive graphs ($n$ up to 1000), backtracking encounters deadlocks. We implemented a **Greedy Algorithm**:
> It visits vertices in canonical order and greedily assigns the smallest integer $val \ge 1$ that satisfies two invariants: (1) no label sharing with 2-hop neighbors, and (2) no edge weight collision.
>
> **Time Complexity of the Greedy Method:**
> Because GP graphs are 3-regular ($\Delta = 3$ is constant), checking 2-hop neighbors takes $\le 6 = O(1)$ operations, and checking incident edges takes $\le 3 = O(1)$ operations.
> Therefore, the Greedy Algorithm runs in strictly **linear time: $T(V, E) = O(|V| \cdot \Delta^2) = \mathbf{O(n)}$**, and takes $\mathbf{O(n)}$ space!"

---

### Slide 6: Exact Solution: $GP(12, 5) = 19$ (Zero-Waste Optimal)
**Speaker: Tina Nguyen**

> "This brings us to the centerpiece of Problem 1: **Generalized Petersen Graph $GP(12, 5)$**, highlighted directly on Assignment Slide 14.
>
> Here, $n = 12$ and step size $p = 5$.
> • Order $|V| = 24$, Size $|E| = 36$, Degree $\Delta = 3$.
> • Theoretical Lower Bound: $\lceil (3 \times 12 + 1) / 2 \rceil = \lceil 37 / 2 \rceil = 19$.
>
> Our exact backtracking solver solved $GP(12, 5)$ in just **0.3118 seconds**, proving that:
> $$es(GP(12, 5)) = 19$$
>
> Please observe the circular diagram on the slide:
> • Outer cycle labels: $[1, 2, 3, 4, 5, 6, 7, 19, 16, 17, 15, 14]$.
> • Inner star labels: $[1, 2, 3, 4, 5, 11, 18, 18, 12, 19, 19, 13]$.
> • The 36 edge weights form the exact sequence of consecutive integers from **2 to 37 with zero gaps and zero collisions**!
>
> The theoretical minimum max weight for 36 edges is $2 + 36 - 1 = 37$. Our largest label sum is $19 + 18 = 37$—an exact match! This proves our solution achieves **zero-waste mathematical optimality**."

---

### Slide 7: Empirical Benchmarks & Lower Bound Optimality
**Speaker: Tina Nguyen**

> "We benchmarked our algorithms across orders from $n = 3$ to $n = 1000$ (2,000 vertices and 3,000 edges).
>
> Looking at the results in Table 1:
> • **Lower Bound Optimality:** For all tested graphs with $n \ge 4$, our exact backtracking algorithm provably hits the theoretical lower bound:
>   - $GP(4, 1): LB = 7, k = 7$ in 0.0001s
>   - $GP(5, 2): LB = 8, k = 8$ in 0.0004s
>   - $GP(6, 2): LB = 10, k = 10$ in 0.0002s
>   - $GP(8, 3): LB = 13, k = 13$ in 0.0201s
>   - $GP(10, 3): LB = 16, k = 16$ in 0.0394s
>   - $GP(12, 5): LB = 19, k = 19$ in 0.3118s
>
> • **The Known Exception $GP(3, 1)$:**
> For $GP(3, 1)$, the lower bound formula gives $\lceil 10/2 \rceil = 5$, but exact backtracking proved that no valid labeling exists with $k=5$. The minimum valid labeling is $k=6$. This is because $GP(3, 1)$ is the triangular prism ($K_3 \square K_2$), where tight symmetry constraints force $es > \text{LB}$.
>
> • **Linear Scalability of the Greedy Algorithm:**
> For massive instances, our Greedy Heuristic scales in strictly linear time $O(n)$:
> It labeled $GP(1000, 51)$—a graph with **2,000 vertices and 3,000 edges**—in just **2.38 seconds**, using only 2.45 MB of RAM! Every single edge weight was verified to be 100% unique."

---

### Slide 8: Extension: Ship Wheel Graph $SW(8, 2)$ (Slide 15)
**Speaker: Tina Nguyen**

> "Assignment Slide 15 also displayed Crab Graphs and Ship Wheel Graphs. To ensure complete coverage, we modeled and solved the **Ship Wheel Graph $SW(8, 2)$**:
> • 1 Central Hub (node 0) with degree 8 linked to all rim nodes.
> • 8 Rim cycle vertices (nodes 1..8) forming an 8-cycle $C_8$.
> • 2 Pendant leaves on each rim node (16 leaves).
> • Total order $|V| = 25$ vertices, size $|E| = 32$ edges.
>
> Applying Theorem 1:
> $$es(SW(8, 2)) \ge \max\left(\left\lceil \frac{32 + 1}{2} \right\rceil, 8\right) = \max(17, 8) = 17$$
>
> Our exact solver proved that **$k = 17$ is optimal**, producing 32 distinct edge weights from 2 to 33, exactly replicating the solution on Slide 15!
>
> I will now hand over to **Haoran** to present Problem 2: Comparative NLP Pipeline Implementation."

---

### Slide 9: Problem 2 — Shakespeare NLP Pipeline Architecture
**Speaker: Haoran**

> "Thank you, Tina. For **Problem 2**, we implemented and evaluated a comparative Natural Language Processing pipeline on Shakespeare's Complete Works (`shakespeare.txt`).
>
> The dataset is 5.46 MB, containing 124,456 lines and approximately 900,000 raw words.
>
> Following Slides 16 and 17, our pipeline executes five consecutive stages:
> 1. **Text Cleaning & Normalization:** Lowercasing, stripping punctuation, special characters, and HTML tags in $O(N)$ linear time.
> 2. **Stage Direction Removal:** Per Slide 17's mandate, filtering out dramatic markers: `ACT`, `SCENE`, `ENTER`, `EXIT`, and `EXEUNT` in $O(N)$ time.
> 3. **Tokenization:** A Deterministic Regex FSM `[a-z]+(?:'[a-z]+)?` capturing words while preserving internal apostrophes (such as *I'll* and *father's*) in $O(N)$ time.
> 4. **Stopword Filtering:** Hash-table filtering with $O(1)$ lookups, removing filler words while retaining Early Modern English pronouns (*thou*, *thee*, *thy*) for poetic mood analysis.
> 5. **Stemming & Bag-of-Words:** Morphological suffix stripping and term frequency histogram generation.
>
> Let's examine the algorithmic design of our custom implementation."

---

### Slide 10: NLP Methods: Naive Brute Force vs. DP Memoization
**Speaker: Haoran**

> "Assignment Slide 16 explicitly required us to write our own algorithms from scratch rather than relying solely on black-box libraries.
>
> For the stemming stage, I implemented **Martin Porter's 1980 algorithm from first principles in pure Python**:
> • Step 1a for plurals, Step 1b for `-ed` and `-ing` stripping with vowel checks, Step 1c for terminal `y` replacement, Step 2 for derivational suffixes, and Steps 3, 4, and 5 for terminal cleanup.
>
> **The Algorithmic Challenge (Naive Brute Force):**
> If we apply suffix stripping rules naively to every token in the 5.46 MB corpus, we perform $O(W \cdot L_{\text{avg}})$ operations on over 500,000 content words. Common words like *'king'* appear 2,871 times and would be stemmed thousands of times redundantly. Naive execution took over **60 seconds**!
>
> **The Algorithmic Solution: Dynamic Programming with Memoization:**
> We leveraged a fundamental linguistic property known as **Zipf's Law**:
> In natural language, although there are 500,000 word occurrences, Shakespeare uses only about **$M \approx 25,000$ unique word types**!
>
> By caching `memo[word] = stem(word)` in an $O(1)$ Hash Table on its first encounter, rule evaluation is executed only $M$ times ($O(M \cdot L_{\text{avg}})$). Subsequent encounters are instant $O(1)$ cache hits.
>
> **Empirical Impact:**
> Memoization eliminated over **95% of redundant rule evaluations**, reducing stemming runtime from $>60$ seconds to just **2.06 seconds**—a 30-fold speedup!"

---

### Slide 11: Comparative Evaluation: Custom vs. Built-in NLTK
**Speaker: Haoran**

> "We benchmarked our Custom Algorithmic Pipeline against the industry-standard NLTK built-in pipeline across four corpus slices: 25%, 50%, 75%, and 100%.
>
> As shown on Slide 11:
> 1. **Execution Time $T(n)$:**  
> Our custom pipeline is **2.6 times faster** than NLTK! On the full 5.46 MB corpus, our pipeline finished in **2.52 seconds**, compared to **6.58 seconds** for NLTK.
> 2. **Memory Footprint:**  
> Peak memory was virtually identical across both implementations: 14.9 MB at 25%, scaling smoothly to **58.7 MB at 100%**.
> 3. **Accuracy & Vocabulary Overlap:**  
> Top-50 vocabulary agreement was **exactly 100.0%**, proving our from-scratch implementation achieved industrial-grade precision without sacrificing performance.
> 4. **Linear Scalability:**  
> Both pipelines exhibited strictly linear time complexity $O(N)$ with text volume."

---

### Slide 12: Bag-of-Words & Thematic Mood Analysis
**Speaker: Haoran**

> "Next, we constructed the Bag-of-Words frequency ranking and conducted lexical mood vectorization.
>
> Looking at the left chart on Slide 12:  
> After filtering dramatic stage directions and stopwords, our top content words match the exact values on Assignment Slide 17:
> • *king* (2,871), *good* (2,814), *come* (2,480), *love* (2,091), *let* (2,086), *man* (1,826), *like* (1,787), *I'll* (1,745), *say* (1,685), and *know* (1,649).
>
> To quantify the emotional atmosphere of Shakespeare's writing, we classified content words into six thematic sentiment categories (shown on the right):
> • **Kingship & Royalty (29.8%):** By far the dominant motif (*king, lord, queen, crown, majesty*), reflecting his deep preoccupation with monarchy in plays like *Hamlet*, *Macbeth*, and *Richard III*.
> • **Honor & Virtue (18.9%):** Words like *good, honor, noble, true, virtue*.
> • **Love & Romance (18.3%):** Anchored by *love, heart, fair, sweet, beauty*.
> • **Conflict & Tragedy (14.5%):** Words of war and sorrow: *death, blood, war, kill, sorrow*.
> • **Time & Fate (14.3%):** *time, heaven, fortune, age, destiny*.
> • **Melancholy & Grief (4.3%):** *grief, tears, sad, mourn*.
>
> This provides quantitative, algorithmic evidence of Shakespeare's dramatic focus."

---

### Slide 13: Summary of Algorithmic Methods & Time Complexity $T(n)$
**Speaker: Joint (Tina Nguyen then Haoran)**

> **Tina:**  
> "To synthesize our theoretical and empirical complexity analysis:
> Look at Table 2 on Slide 13 comparing all algorithms and paradigms:
> • For **Exact Graph Labeling**, pure brute force is $O(k^{2n})$ (impossible). Our **Constraint Backtracking** prunes the search space with 2-hop conflicts and coupled spoke traversal, achieving an effective branching factor of $b_{\text{eff}} \approx 1.15$ and solving $GP(12, 5)$ in 0.31s.
> • For **Scalable Graph Labeling**, our **Greedy Constructive Heuristic** runs in strictly **linear time: $O(|V| \cdot \Delta^2) = \mathbf{O(n)}$**, solving 2,000 vertices in 2.38 seconds.
> • For theoretical bounds: Theorem 1 lower bound is $\mathbf{O(n)}$, while Asim's algorithmic upper bound is $|E| \log_2 |V| = \mathbf{O(n \log n)}$."
>
> **Haoran:**  
> "• For **NLP Stemming**, naive brute force is $O(W \cdot L_{\text{avg}}) > 60$s. Our **Dynamic Programming Memoization** reduces this to $\mathbf{O(M \cdot L_{\text{avg}} + W) = O(W)}$ linear time, processing the entire 5.46 MB corpus in 2.52 seconds.
> • In summary: both problems achieve strictly **linear time complexity $O(n)$ in practice**—Problem 1 via Greedy Constructive search, and Problem 2 via Dynamic Programming Memoization!"

---

### Slide 14: Q&A Technical Defense Preparation (Rubric: 4 Points)
**Speaker: Joint (Tina handles Q1 & Q2, Haoran handles Q3)**

> **Tina:**  
> "We also prepared rigorous answers for anticipated defense questions:
>
> • **Question 1: Why does vertex $k$-labeling prohibit two neighbors of any vertex from receiving identical labels?**  
> *Defense:* If vertex $v$ has neighbors $u$ and $w$ with $\phi(u) = \phi(w)$, then edge weights $w(vu) = \phi(v) + \phi(u)$ and $w(vw) = \phi(v) + \phi(w)$ are identical. Because all edge weights must be strictly distinct, sharing a label directly violates edge irregularity. Precomputing 2-hop neighborhoods enforces this condition in $O(1)$ time.
>
> • **Question 2: How does Coupled Spoke Traversal prune the search tree so much faster than sequential cycle traversal?**  
> *Defense:* In sequential traversal, outer cycle edges are placed first, but spoke edges $(u_i, v_i)$ cannot be tested until step $n+1$. In our coupled spoke order $[u_0, v_0, u_1, v_1, \dots]$, spoke edge $(u_i, v_i)$ is tested immediately at step $2i+1$. Weight collisions are detected near the root of the tree, pruning entire subtrees before they expand."
>
> **Haoran:**  
> "• **Question 3: Why was your custom from-scratch NLP pipeline 2.6x faster than NLTK?**  
> *Defense:* NLTK is designed as a general educational library with heavy OOP abstractions, defensive type checks, and polymorphic overhead on every token. By building a dedicated regex FSM tokenizer, direct hash sets, and especially Dynamic Programming memoization on Porter stemmer rules, we eliminated 95% of redundant computation."

---

### Slide 15: Conclusions & Key Achievements
**Speaker: Tina Nguyen**

> "To conclude:
> 1. In **Problem 1**, we proved that Generalized Petersen Graphs $GP(n, p)$ strictly hit the theoretical lower bound $\lceil(3n+1)/2\rceil$ with zero waste for all $n \ge 4$, including $es(GP(12, 5)) = 19$ and Ship Wheel $SW(8, 2) = 17$. Our greedy heuristic runs in strictly linear $O(n)$ time and labels 2,000 vertices in 2.38 seconds.
> 2. In **Problem 2**, our custom NLP pipeline outperformed NLTK by **2.6x in speed** while maintaining 100.0% vocabulary precision, and our mood analysis quantified the dominance of Kingship, Honor, and Love in Shakespeare.
> 3. All deliverables—including our reproducible Jupyter Notebook, Research Report in DOCX and PDF, 16-slide PowerPoint deck, and documented source code—are complete, verified, and error-free."

---

### Slide 16: Closing & Q&A
**Speaker: Tina & Haoran together**

> **Tina:** "Thank you very much for your time and attention."  
> **Haoran:** "We would be delighted to answer any questions."

---

## Quick Reference Q&A Cheat Sheet (Keep Handy During Presentation)

| Question Area | Core Technical Defense | Lead Responder |
|:---|:---|:---|
| **What method did you use for exact labeling?** | Constraint Satisfaction Backtracking with Forward Checking & Coupled Spoke Traversal (pruned branch-and-bound). | Tina Nguyen |
| **Why not pure Brute Force for graphs?** | Brute force has $O(k^{2n})$ states (over $10^{30}$ for $GP(12,5)$); backtracking prunes $b_{\text{eff}}$ to 1.15. | Tina Nguyen |
| **What method did you use for large graphs?** | Greedy Constructive Algorithm with 2-Hop Conflict Avoidance; runs in strictly linear $O(n)$ time. | Tina Nguyen |
| **What are the theoretical bounds on $es(G)$?** | Lower Bound: $\lceil (3n+1)/2 \rceil = O(n)$ (Theorem 1); Upper Bound: $|E| \log_2 |V| = O(n \log n)$ (Asim). | Tina Nguyen |
| **Why is $GP(3,1)$ an exception?** | Triangular prism ($K_3 \square K_2$) has 9 edges with high symmetry; no valid labeling exists for $k \le 5$, so $es = 6 > LB = 5$. | Tina Nguyen |
| **How was $SW(8,2)$ solved?** | Hub degree 8, 8 rim nodes, 16 leaves; exact backtracking finds $k = 17$, matching lower bound with distinct weights 2..33. | Tina Nguyen |
| **What method was used for NLP Stemming?** | Martin Porter 1980 stemmer from scratch, optimized via **Dynamic Programming with Memoization**. | Haoran |
| **Why did memoization work so well?** | Zipf's Law: out of 500,000 tokens, only ~25,000 are unique. Caching stems on first encounter eliminates >95% of rule evaluations. | Haoran |
| **What is the NLP time complexity?** | All stages (cleaning, FSM regex, hash filtering, memoized stemming, BoW) are strictly linear $O(N)$ with text size. | Haoran |
| **Why retain 'thou', 'thee', 'thy'?** | Shakespeare's 2nd-person pronouns are crucial for distinguishing intimate vs. formal address in poetic mood analysis. | Haoran |
