# At the threshold

[Download the offline explorer ZIP](https://raw.githubusercontent.com/DannyExperiments/finite-language-distance-attainment/v1.0.0/visualization/finite-language-distance-attainment-explorer.zip). Extract it and open index.html. Move the cutoff and rotation sliders, or drag either tree to rotate it.

The alphabet is $\{a,b\}$. For both comparisons, the left expression is $\{a,b\}\cdot X$. At a node labeled by a nonempty word, membership on the left is the membership of the word's parent in $X$. The empty word $\epsilon$ always disagrees and contributes $1/2$.

- With target $\{\epsilon,a,b\}$, take $X=\{\epsilon\}$. Only the root disagrees, so the distance is exactly $1/2$.
- With target $\Sigma^*$, take $X$ to contain all words through depth $h$. The output agrees at depths $1$ through $h+1$ and disagrees thereafter. The full distance is $1/2+2^{-h-2}$. Every finite $X$ misses some word, which causes a nonempty word to disagree. The infimum $1/2$ is never attained.

Gold nodes disagree and blue nodes agree. The drawing includes levels zero through four. The exact costs account for every level of the infinite tree. At $h=0,1,2$ the full target costs $3/4$, $5/8$, and $9/16$. These examples illustrate the equality test. The paper proves the algorithm for every pair in the stated grammar.

Rebuild from the repository root with **python3 visualization/render.py** using Python 3 and Pillow. Use the option **--font-dir** to select a folder containing Arial or DejaVu Sans. The [independent mathematical replay](../verification/src/replay.py) verifies the displayed costs by direct evaluation.
