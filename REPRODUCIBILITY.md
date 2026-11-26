# Reproducibility

Use Python 3.10 or later. From the repository root, run **python3 verification/src/replay.py**. The replay uses the standard library. It computes exact rational controller values, verifies finite witnesses by direct evaluation with an exact tail, cross-checks expression membership, and compares cutoff equality sets with the greatest and least set iterations. The expected [replay summary](verification/logs/replay.txt) is distributed.

Run **python3 -I scripts/verify_repository.py** to check the manifest, SHA-256 ledger and explorer bundle. Running the same command with **--stage** regenerates the local evidence ZIP and ledgers. [Build the manuscript](paper/BUILD.md) · [Rebuild the GIF](visualization/README.md)
