# FAISS Integration Strategy

## Overview
This document outlines the strategy for integrating Facebook AI Similarity Search (FAISS) into the Intelligent Event Photo Retrieval System. FAISS is used for efficient similarity search of face embeddings.

## Index Selection Strategy

The choice of FAISS index depends heavily on the dataset size and performance requirements.

### 1. Small Dataset (< 10k faces)
*   **Recommended Index**: `IndexFlatL2` (Exact Search)
*   **Why**: 
    *   **Accuracy**: Provides 100% precision (exact search).
    *   **Speed**: For <10k vectors, brute-force search is extremely fast on modern CPUs (sub-millisecond).
    *   **Memory**: Minimal overhead. Stores raw vectors.
*   **Implementation**: `index = faiss.IndexFlatL2(d)` where `d` is differentiation (512).

### 2. Medium Dataset (10k – 1M faces)
*   **Recommended Index**: `IndexIVFFlat` (Inverted File Index)
*   **Why**:
    *   **Speed**: Uses clustering (Voronoi cells) to narrow down the search space, avoiding a full scan.
    *   **Accuracy**: High accuracy, trade-off tunable via `nprobe` (number of clusters to search).
    *   **Training**: Requires a "training" phase to learn the cluster centroids.
*   **Implementation**:
    ```python
    quantizer = faiss.IndexFlatL2(d)
    index = faiss.IndexIVFFlat(quantizer, d, nlist=100) # nlist ≈ sqrt(N)
    index.train(vectors)
    index.add(vectors)
    ```

### 3. Large Dataset (1M+ faces)
*   **Recommended Index**: `IndexIVFPQ` (Product Quantization) or `IndexHNSW` (Hierarchical Navigable Small World)
*   **Why**:
    *   **IndexIVFPQ**: Compresses vectors (lossy), drastically reducing memory usage. Essential for fitting millions of vectors in RAM.
    *   **IndexHNSW**: Graph-based. Extremely fast search but uses more memory than IVF. Best if you have ample RAM and need low latency.
*   **Implementation**: `index = faiss.IndexHNSWFlat(d, 32)`

### Current Choice
For this project start, we use **`IndexFlatL2`** because:
1.  We prioritize maximum accuracy for face retrieval.
2.  Initial event datasets are likely <1M faces.
3.  It is the simplest to implement and debug.
4.  We can easily swap to `IndexIVFFlat` later without changing the API.

## Distance Metric: L2 vs Cosine Similarity

### L2 Distance (Euclidean)
*   Measures the straight-line distance between two points in vector space.
*   $d(u, v) = ||u - v||_2$
*   Lower value = More similar.
*   **Context**: FAISS is optimized for L2 search.

### Cosine Similarity
*   Measures the cosine of the angle between two vectors.
*   $similarity(u, v) = \frac{u \cdot v}{||u|| ||v||}$
*   Higher value (closer to 1) = More similar.
*   **Face Recognition**: Typically uses Cosine Similarity because it is robust to variations in vector magnitude (though FaceNet embeddings are usually normalized).

### The Bridge: L2 on Normalized Vectors
If vectors are **L2 Normalized** (length = 1), then L2 distance and Cosine Similarity are directly related:
$$ ||u - v||_2^2 = 2 (1 - \cos(\theta)) $$
*   Minimizing L2 distance is mathematically equivalent to maximizing Cosine Similarity for normalized vectors.

**Strategy**:
1.  **Normalize** all face embeddings to unit length (L2 norm = 1) immediately after generation.
2.  Use **`IndexFlatL2`** in FAISS.
3.  The search results will be effectively ranked by Cosine Similarity.
