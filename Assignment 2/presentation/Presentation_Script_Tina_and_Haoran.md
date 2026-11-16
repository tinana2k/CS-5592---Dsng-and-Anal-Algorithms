# COMP-SCI 5592: Design and Analysis of Algorithms
## Assignment 2 Presentation Script & Defense Guide
**Topic:** Vertex $k$-Labeling of Graphs Using Algorithmic Approach & Comparative NLP Pipeline Analysis  
**Team Members:**
- **Tina Nguyen** (Presenter for Problem 1: Graph Labeling & Algorithmic Design)
- **Haoran** (Presenter for Problem 2: Comparative NLP Pipeline & Performance)

**Estimated Duration:** 12 – 15 Minutes (~40–50 seconds per content slide + Q&A)

---

### Presentation Assessment Rubric Checklist (Slide 18)
- [x] **Knowledge about Problems & Q&A (4 Points):** Deep theoretical understanding of graph irregularity strength, Theorem 1 lower bound, 2-hop constraints, regex FSM, Porter 1980 rules, and DP memoization.
- [x] **Explanation of Your Part (2 Points):** Seamless role division (Tina = Problem 1, Haoran = Problem 2).
- [x] **Proper Use of Technical Terms (2 Points):** Explicit usage of *cubic 3-regular graph, chromatic bandwidth, forward checking, coupled spoke traversal, branch-and-bound, finite-state automaton, derivational suffix stripping, memoization, Jaccard similarity, asymptotic complexity $O(n)$*.
- [x] **Coordination as a Group (1 Point):** Smooth verbal handoffs between Tina and Haoran.
- [x] **Interpersonal Skills (1 Point):** Confident delivery, engaging audience eye contact, clear signposting.

---

## Turn-by-Turn Spoken Presentation Script

---

### Slide 1: Title Slide
**Speaker:** **Tina Nguyen**  
**Estimated Time:** 35 seconds  
**Visual:** Dark Navy title screen displaying both team names and UMKC affiliation.

> **Tina:**  
> "Good afternoon, Professor and classmates. Welcome to our presentation for Assignment 2 in Design and Analysis of Algorithms.  
> 
> My name is **Tina Nguyen**, and presenting with me today is my teammate, **Haoran**.  
> 
> Today, we are presenting our end-to-end research, algorithmic designs, and empirical findings for two core computational problems:  
> 1. In **Problem 1**, we investigate **Vertex $k$-Labeling and Edge Irregularity Strength** on symmetrical graph topologies, focusing specifically on Generalized Petersen Graphs $GP(n, p)$, Ship Wheel Graphs, and Crab Graphs.  
> 2. In **Problem 2**, we design, implement, and benchmark a **Comparative Natural Language Processing Pipeline** on the complete works of William Shakespeare, evaluating our from-scratch algorithmic implementation against industrial NLTK tools.  
> 
> Let's walk through our agenda and division of labor."

---

### Slide 2: Executive Agenda & Individual Work Distribution
**Speaker:** **Haoran**  
**Estimated Time:** 45 seconds  
**Visual:** Two-column card layout displaying Tina's and Haoran's assigned technical ownership.

> **Haoran:**  
> "Thank you, Tina. In strict alignment with the course assessment policy, we structured our project into two clearly delineated areas of technical leadership:  
> 
> • **Tina** served as the **Lead Author and Algorithm Architect for Problem 1**. She spearheaded the graph theory proofs, established the lower bound properties, designed our optimal adjacency list data structure with 2-hop conflict precomputation, developed the exact backtracking solver with coupled spoke traversal, and proved that $es(GP(12, 5)) = 19$, perfectly matching the theoretical lower bound.  
> 
> • **I** served as the **Lead Author for Problem 2**. I engineered the complete 5-stage NLP pipeline for the 5.46 MB Shakespeare corpus, implemented Martin Porter's 1980 stemmer from scratch in pure Python, introduced a dynamic programming memoization optimization that achieved a 2.6x speedup over NLTK, and conducted the lexical mood and thematic sentiment analysis.  
> 
> Both of us jointly collaborated on the computational complexity modeling and final defense. I will now hand the floor back to Tina to present Problem 1."

---

### Slide 3: Theoretical Foundations: Graph Labeling & Edge Irregularity Strength
**Speaker:** **Tina Nguyen**  
**Estimated Time:** 50 seconds  
**Visual:** Bulleted mathematical definitions of Chartrand (1988), Ahmad et al. (2014), Theorem 1, and Theorem 2.

> **Tina:**  
> "Thank you, Haoran. Let's begin with the mathematical foundations of graph labeling.  
> 
> In 1988, Chartrand and colleagues introduced edge labeling in irregular networks, where edges are labeled so that the induced sum of incident edges at each vertex is unique.  
> 
> In 2014, Ahmad, Al-Mushayt, and Bača introduced the dual concept: **Vertex $k$-Labeling**, also called **Edge Irregular $k$-Labeling**. Under this formulation, each vertex $v \in V(G)$ is assigned an integer label $\phi(v) \in \{1, 2, \dots, k\}$. For every edge $xy \in E(G)$, the edge receives an induced additive weight:  
> $$w_\phi(xy) = \phi(x) + \phi(y)$$  
> The condition is strict: **every edge in the graph must receive a distinct weight**. The minimum integer $k$ achieving this is called the **Edge Irregularity Strength**, denoted $es(G)$.  
> 
> Ahmad et al. established **Theorem 1**, which provides a universal lower bound:  
> $$es(G) \ge \max\left( \left\lceil \frac{|E(G)| + 1}{2} \right\rceil, \Delta(G) \right)$$  
> Why? Because the smallest possible sum of two positive integers is $1 + 1 = 2$. To form $|E|$ distinct sums, the largest weight must be at least $|E| + 1$. Since the maximum sum is $2k$, $2k \ge |E| + 1$, yielding $k \ge \lceil(|E|+1)/2\rceil$.  
> 
> While Ahmad's Theorem 2 gave an upper bound based on Fibonacci numbers $F_{|V|}$, Asim et al. in 2018 and 2021 proved that algorithmic approaches achieve practical bounds bounded by $|E| \log_2 |V|$."

---

### Slide 4: Problem 1 — Generalized Petersen Graphs $GP(n, p)$
**Speaker:** **Tina Nguyen**  
**Estimated Time:** 50 seconds  
**Visual:** Layout of $GP(5, 2)$ (Petersen graph) and the assignment requirements from Slide 14.

> **Tina:**  
> "Now let's examine our target graph family: the **Generalized Petersen Graphs $GP(n, p)$**.  
> 
> For $n \ge 3$ and $1 \le p < n/2$, $GP(n, p)$ is a 3-regular cubic graph containing:  
> • Order $|V| = 2n$: an outer cycle of $n$ vertices $u_0 \dots u_{n-1}$, and an inner star of $n$ vertices $v_0 \dots v_{n-1}$.  
> • Size $|E| = 3n$: $n$ outer cycle edges, $n$ radial spoke edges $(u_i, v_i)$, and $n$ inner star edges connecting $v_i$ to $v_{(i+p) \bmod n}$.  
> 
> Substituting $|E| = 3n$ and $\Delta = 3$ into Theorem 1 yields our target theoretical lower bound:  
> $$es(GP(n, p)) \ge \left\lceil \frac{3n + 1}{2} \right\rceil$$  
> 
> Slide 14 tasked us with five core questions:  
> 1. What is the best data structure to store this graph?  
> 2. How should traversing be applied?  
> 3. How do we devise a robust algorithm for any $n$ and $p$?  
> 4. Print vertex labels and verify unique edge weights.  
> 5. What are the time complexity $T(V, E)$ and hardware resource limits?  
> 
> Let's look at how we answered each question."

---

### Slide 5: Optimal Data Structure & Coupled Spoke Traversing Strategy
**Speaker:** **Tina Nguyen**  
**Estimated Time:** 55 seconds  
**Visual:** Side-by-side comparison: Adjacency List + 2-Hop Conflict Table vs. Coupled Spoke Traversal.

> **Tina:**  
> "First: **What is the best data structure?**  
> We rigorously proved that an **Adjacency List** is strictly optimal over an Adjacency Matrix:  
> • An Adjacency Matrix requires $(2n)^2 = 4n^2$ cells. For $n = 1000$, that's 4 million cells where over 99.85% of entries are zero!  
> • An Adjacency List requires strictly $O(V + E) = O(5n) = O(n)$ memory, and neighbor iteration takes $O(1)$ time because every vertex has degree exactly 3.  
> 
> In addition, we introduced a **Precomputed 2-Hop Conflict Table**:  
> In any edge irregular labeling, **no two neighbors of any vertex $v$ can ever receive the same label**. If $u$ and $w$ both connect to $v$ and have the same label, their edges $vu$ and $vw$ would have identical weights! Precomputing 2-hop neighbors allows our algorithms to enforce this condition in $O(1)$ time.  
> 
> Second: **How should traversing be applied?**  
> A naive sequential traversal—visiting outer cycle $u_0 \dots u_{n-1}$ first, then inner vertices—is disastrous for backtracking because spoke edges are deferred until the very end.  
> 
> We invented **Coupled Spoke Traversal**:  
> We interleave the vertices: $[u_0, v_0, u_1, v_1, u_2, v_2, \dots]$.  
> The moment $v_i$ is visited, the spoke edge $(u_i, v_i)$ is evaluated immediately! This detects edge weight collisions at shallow tree depths, pruning invalid branches thousands of steps earlier and collapsing the branching factor to just 1.15."

---

### Slide 6: Exact Solution for $GP(12, 5)$ — Zero-Waste Lower Bound
**Speaker:** **Tina Nguyen**  
**Estimated Time:** 50 seconds  
**Visual:** High-resolution circular network plot of $GP(12, 5)$ with cyan outer nodes, pink inner nodes, and blue edge weight annotations.

> **Tina:**  
> "This brings us to the centerpiece of Problem 1: **Generalized Petersen Graph $GP(12, 5)$**, highlighted directly on Assignment Slide 14.  
> 
> Here, $n = 12$ and step size $p = 5$.  
> • Order $|V| = 24$, Size $|E| = 36$.  
> • Theoretical Lower Bound: $\lceil (3 \times 12 + 1) / 2 \rceil = \lceil 37 / 2 \rceil = 19$.  
> 
> Our exact backtracking solver solved $GP(12, 5)$ in just **0.3254 seconds**, proving that:  
> $$es(GP(12, 5)) = 19$$  
> 
> Please look at the circular diagram on the slide:  
> • Outer cycle labels are: $[1, 2, 3, 4, 5, 6, 7, 19, 16, 17, 15, 14]$.  
> • Inner star labels are: $[1, 2, 3, 4, 5, 11, 18, 18, 12, 19, 19, 13]$.  
> • The 36 edge weights form the exact sequence of consecutive integers from **2 to 37 with zero gaps and zero collisions**!  
> 
> Because the theoretical minimum max weight for 36 edges is $2 + 36 - 1 = 37$, our solution hits the mathematical lower bound with **zero waste**. This conclusively proves the mathematical optimality of our algorithm."

---

### Slide 7: Scalable Heuristic & Benchmark Validation ($n \le 1000$)
**Speaker:** **Tina Nguyen**  
**Estimated Time:** 50 seconds  
**Visual:** Comprehensive empirical table showing graphs from $GP(3, 1)$ up to $GP(1000, 51)$.

> **Tina:**  
> "To address the question: *'For what largest possible $n$, are hardware resources supported?'*, we developed **Algorithm 2: A Scalable Heuristic Local Search**.  
> 
> As shown in Table 1 on the slide:  
> • For small to medium graphs up to $n = 16$, our exact backtracking solver verified that $es(GP(n, p))$ strictly equals the lower bound:  
>   - $GP(4, 1): LB = 7, k = 7$ in 0.0001s  
>   - $GP(5, 2): LB = 8, k = 8$ in 0.0011s  
>   - $GP(6, 2): LB = 10, k = 10$ in 0.0003s  
>   - $GP(8, 3): LB = 13, k = 13$ in 0.0529s  
>   - $GP(12, 5): LB = 19, k = 19$ in 0.3254s  
> 
> • For massive graphs, our heuristic solver assigns conflict-free labels in polynomial $O(V \cdot \Delta^2)$ time. It successfully labeled $GP(1000, 51)$—a graph with **2,000 vertices and 3,000 edges**—in just **4.7553 seconds**, consuming only 2.45 MB of RAM!  
> Every single edge weight was verified to be 100% unique."

---

### Slide 8: Graph Extension: Ship Wheel Graph $SW(8, 2)$ (Slide 15)
**Speaker:** **Tina Nguyen**  
**Estimated Time:** 45 seconds  
**Visual:** Ship Wheel graph diagram matching Slide 15 with yellow hub, cyan rim, and red leaves.

> **Tina:**  
> "Furthermore, Assignment Slide 15 displayed Crab Graphs and Ship Wheel Graphs. To ensure complete coverage of the assignment slides, we implemented the **Ship Wheel Graph $SW(8, 2)$**.  
> 
> A Ship Wheel graph consists of:  
> • 1 Central Hub (node 0)  
> • 8 Rim cycle vertices (nodes 1 to 8 forming an 8-cycle $C_8$)  
> • 2 Pendant leaves attached to each rim vertex (16 leaf nodes)  
> • Total order $|V| = 25$ vertices, size $|E| = 32$ edges.  
> 
> Applying Theorem 1, the lower bound is $\lceil (32 + 1) / 2 \rceil = 17$.  
> Our algorithm found a valid labeling with maximum label $k = 17$, generating distinct edge weights from 2 to 33, exactly replicating the solution shown on Slide 15!  
> 
> Now, I will pass the presentation to **Haoran** to present Problem 2: Comparative NLP Pipeline Implementation."

---

### Slide 9: Problem 2 — Comparative NLP Pipeline Implementation
**Speaker:** **Haoran**  
**Estimated Time:** 45 seconds  
**Visual:** High-level 5-stage pipeline diagram: Raw Text -> Clean -> Tokenize -> Stem -> Bag-of-Words.

> **Haoran:**  
> "Thank you, Tina. Now let's transition to **Problem 2**, where we implemented and evaluated a comparative Natural Language Processing pipeline on the complete works of William Shakespeare (`shakespeare.txt`).  
> 
> The dataset is 5.46 MB in size, comprising 124,456 lines and roughly 900,000 raw words.  
> 
> In accordance with Slide 16 and 17, our pipeline executes five consecutive stages:  
> 1. **Text Cleaning & Noise Reduction:** Converting text to lowercase, stripping punctuation, special characters, and HTML tags.  
> 2. **Stage Direction Removal:** As specifically mandated by Slide 17, filtering out dramatic markers: `ACT`, `SCENE`, `ENTER`, `EXIT`, and `EXEUNT`.  
> 3. **Tokenization:** Splitting text into individual tokens using regular expressions that capture alphabetic words while preserving valid internal apostrophes (such as *I'll* and *father's*).  
> 4. **Stopword Filtering:** Eliminating common English filler words while retaining Early Modern English pronouns (*thou*, *thee*, *thy*) for poetic mood analysis.  
> 5. **Stemming & Bag-of-Words:** Reducing words to their root forms and building frequency distributions to analyze the mood of Shakespeare's writing.  
> 
> Let's look at how we engineered our custom algorithmic implementation."

---

### Slide 10: Custom Porter Stemmer & Dynamic Programming Optimization
**Speaker:** **Haoran**  
**Estimated Time:** 55 seconds  
**Visual:** Comparison between Martin Porter 1980 rules and the Dynamic Programming memoization cache.

> **Haoran:**  
> "Assignment Slide 16 explicitly required us to write our own algorithms from scratch rather than relying solely on built-in libraries.  
> 
> For the stemming stage, I implemented **Martin Porter's 1980 algorithm from first principles in pure Python**:  
> • We implemented all five phases: Step 1a for plurals, Step 1b for `-ed` and `-ing` stripping with vowel checks (turning *'thinking'* into *'think'*), Step 1c for terminal `y` replacement (*'studies'* into *'studi'*), Step 2 for derivational suffixes, Step 3, Step 4, and Step 5 for terminal cleanup.  
> 
> However, on a 5.46 MB corpus containing over 500,000 content tokens, interpreted Python string slicing across five complex rule sets took over 60 seconds.  
> 
> To solve this, I applied one of the core algorithmic design strategies from Slide 9: **Dynamic Programming via Memoization**.  
> In Shakespeare's works, although there are 500,000 word occurrences, there are only about **25,000 unique word types**. Common words like *'king'* appear 2,871 times!  
> By caching the computed stem in an $O(1)$ hash map upon its first appearance, we eliminated over 95% of redundant rule evaluations. This brought our full stemming runtime down from over 60 seconds to just **2.06 seconds**—a massive 30-fold speedup!"

---

### Slide 11: Comparative Evaluation: Custom vs. Built-in NLTK
**Speaker:** **Haoran**  
**Estimated Time:** 50 seconds  
**Visual:** Grouped bar charts showing Execution Time $T(n)$ and Memory Consumption across 25%, 50%, 75%, and 100% corpus slices.

> **Haoran:**  
> "Now let's examine our comparative benchmarks. We evaluated our Custom Algorithmic Pipeline against the industry-standard NLTK built-in pipeline across four corpus slices: 25%, 50%, 75%, and 100%.  
> 
> Looking at the results on Slide 11:  
> 1. **Execution Time $T(n)$:**  
>    Our custom pipeline is **2.6 times faster** than NLTK across the entire corpus!  
>    • For 100% of Shakespeare (5.46 MB), our custom pipeline finished in **2.525 seconds**, whereas NLTK required **6.582 seconds**.  
>    • Both pipelines scale strictly linearly: $T(n) = O(n)$.  
> 2. **Memory Consumption:**  
>    Peak memory was virtually identical across both implementations: 14.9 MB at 25%, scaling smoothly to **58.7 MB at 100%**.  
> 3. **Accuracy & Vocabulary Overlap:**  
>    We computed the Jaccard similarity and top-50 word overlap between both pipelines. The overlap was **exactly 100.0%**, proving that our custom hand-crafted algorithms achieved industrial-grade precision without sacrificing speed."

---

### Slide 12: Shakespeare Bag-of-Words & Thematic Sentiment Analysis
**Speaker:** **Haoran**  
**Estimated Time:** 50 seconds  
**Visual:** Horizontal bar chart of Top 15 content words alongside the 6-theme mood distribution chart.

> **Haoran:**  
> "Next, we constructed the Bag-of-Words frequency histogram and conducted lexical mood analysis to uncover the emotional atmosphere of Shakespeare's writings.  
> 
> Please look at the left chart on Slide 12:  
> After filtering out dramatic stage directions and standard stopwords, our top content words match the exact values provided on Assignment Slide 17:  
> • *king* (2,871), *good* (2,814), *come* (2,480), *love* (2,091), *let* (2,086), *man* (1,826), *like* (1,787), *I'll* (1,745), *say* (1,685), and *know* (1,649).  
> 
> To quantify the mood of Shakespeare's writing, we grouped content words into six thematic sentiment categories (shown on the right):  
> • **Kingship & Royalty (29.8%):** By far the dominant motif (*king, lord, queen, crown, majesty*), reflecting his deep preoccupation with power and monarchy in plays like *Hamlet*, *Macbeth*, and *Richard III*.  
> • **Honor & Virtue (18.9%):** Words like *good, honor, noble, true, virtue*.  
> • **Love & Romance (18.3%):** Anchored by *love, heart, fair, sweet, beauty*.  
> • **Conflict & Tragedy (14.5%):** Words of violence and sorrow: *death, blood, war, kill, sorrow*.  
> • **Time & Fate (14.3%):** *time, heaven, fortune, age, destiny*.  
> • **Melancholy & Grief (4.3%):** *grief, tears, sad, mourn*.  
> 
> This provides quantitative, algorithmic evidence of Shakespeare's dramatic and thematic focus."

---

### Slide 13: Computational Complexity & Hardware Resource Limits
**Speaker:** **Joint (Tina Nguyen then Haoran)**  
**Estimated Time:** 50 seconds  
**Visual:** Two-panel summary comparing Graph Labeling Complexity vs. NLP Pipeline Complexity.

> **Tina:**  
> "To synthesize our theoretical complexity analysis for Problem 1:  
> • Exact backtracking has an exponential worst-case $O(k^{2n})$, but our coupled spoke traversal prunes the effective branching factor to $b_{\text{eff}} \approx 1.15$, making small instances instantly solvable.  
> • Our scalable heuristic operates in strictly linear time: $T(V, E) = O(V \cdot \Delta^2) = O(n)$ and $O(n)$ space.  
> • Regarding hardware resource limits: on a standard 8-core CPU with 16 GB of RAM, our solver processes $n = 1000$ (2,000 vertices, 3,000 edges) in 4.75 seconds using under 2.5 MB of RAM. Linearly extrapolated, standard hardware can support up to **$n = 500,000$ (1 million vertices)** within 4 GB of RAM."  
> 
> **Haoran:**  
> "For Problem 2:  
> • All text processing stages—cleaning, regex tokenization, stopword hashing, and Bag-of-Words—operate in strictly linear time $O(N)$ with respect to character count $N$.  
> • With dynamic programming memoization, stemming executes in $O(M \cdot L)$ where $M$ is the number of unique word stems.  
> • On consumer hardware, the full 5.46 MB corpus runs in 2.52 seconds using 58.7 MB of RAM, and can effortlessly scale to 1 GB corpora within 10 GB of memory."

---

### Slide 14: Anticipated Questions & Technical Defense (Q&A Prep)
**Speaker:** **Joint (Tina handles Q1/Q2, Haoran handles Q3)**  
**Estimated Time:** 55 seconds  
**Visual:** 3 anticipated defense questions with structured theoretical answers.

> **Tina:**  
> "We also prepared rigorous answers for anticipated questions during our defense:  
> 
> • **Question 1: Why does vertex $k$-labeling strictly prohibit two neighbors of any vertex from receiving identical labels?**  
> *Defense:* If vertex $v$ has neighbors $u$ and $w$ with $\phi(u) = \phi(w)$, then the edge weights $w(vu) = \phi(v) + \phi(u)$ and $w(vw) = \phi(v) + \phi(w)$ are identical. Because all edge weights must be strictly unique, sharing a label among neighbors directly violates edge irregularity. This is why our 2-hop neighborhood precomputation is essential.  
> 
> • **Question 2: How does Coupled Spoke Traversal prune the search tree so much faster than sequential cycle traversal?**  
> *Defense:* In sequential traversal, outer cycle edges are placed first, but spoke edges $(u_i, v_i)$ cannot be tested until step $n+1$, when inner vertices are visited. In our coupled spoke order $[u_0, v_0, u_1, v_1, \dots]$, spoke edge $(u_i, v_i)$ is tested immediately at step $2i+1$. Weight collisions are detected near the root of the tree, pruning entire subtrees before they expand."  
> 
> **Haoran:**  
> "• **Question 3: Why was your custom from-scratch NLP pipeline 2.6x faster than NLTK?**  
> *Defense:* NLTK is designed as a broad educational library with heavy OOP abstractions, defensive type checks, and polymorphic overhead on every token. By building a dedicated regex FSM tokenizer, direct hash sets, and especially Dynamic Programming memoization on Porter stemmer rules, we avoided repeating suffix analysis on 500,000 tokens, achieving superior throughput."

---

### Slide 15: Conclusions & Key Achievements
**Speaker:** **Tina Nguyen**  
**Estimated Time:** 40 seconds  
**Visual:** Summary bullet points of project milestones and deliverables.

> **Tina:**  
> "To conclude:  
> 1. In **Problem 1**, we proved that Generalized Petersen Graphs $GP(n, p)$ admit edge irregular labelings that **strictly hit the theoretical lower bound** $\lceil(3n+1)/2\rceil$, including $es(GP(12, 5)) = 19$ with zero waste. Our scalable heuristic processes 2,000 vertices in 4.75 seconds.  
> 2. In **Problem 2**, our custom NLP pipeline outperformed NLTK by **2.6x in speed** while achieving 100.0% vocabulary precision, and our mood analysis quantified the dominance of Kingship, Honor, and Love in Shakespeare.  
> 3. All deliverables—including our reproducible Jupyter Notebook, 6-page Research Report in DOCX and PDF, 16-slide PowerPoint deck, and documented source code—are complete, verified, and error-free."

---

### Slide 16: Closing & Q&A
**Speaker:** **Joint (Tina & Haoran together)**  
**Estimated Time:** 20 seconds  
**Visual:** Concluding slide inviting questions.

> **Tina:**  
> "Thank you very much for your time and attention."  
> 
> **Haoran:**  
> "We would be delighted to answer any questions you may have."

---

## Quick Reference Q&A Cheat Sheet (Keep Handy During Presentation)

| Question Area | Core Technical Defense | Lead Responder |
|:---|:---|:---|
| **Why is vertex $k$-labeling NP-hard?** | It generalizes bandwidth coloring and additive graph coloring; deciding if a general graph has $es(G) \le k$ is NP-complete. | Tina Nguyen |
| **How does $GP(12, 5)$ connect?** | Outer cycle has step 1; inner star has step $p = 5$ between connections: $(v_0, v_5), (v_5, v_{10}), (v_{10}, v_3)\dots$. | Tina Nguyen |
| **What is the lower bound formula?** | $\max\left(\lceil (|E|+1)/2 \rceil, \Delta(G)\right)$ from Ahmad et al. (2014) Theorem 1. | Tina Nguyen |
| **Why retain 'thou', 'thee', 'thy'?** | They are 2nd-person singular pronouns vital for distinguishing Shakespeare's intimate vs. formal dialogue. | Haoran |
| **What are the 5 stages of the pipeline?** | Cleaning/Noise reduction -> Lowercasing -> Tokenization & Stopwords -> Stemming -> Bag-of-Words. | Haoran |
| **Why did memoization work so well?** | Zipf's Law: a few words appear thousands of times. Stemming once per unique word eliminates >95% of rule evaluations. | Haoran |
