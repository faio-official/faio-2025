import pandas as pd
import numpy as np


def score(solution: pd.DataFrame, submission: pd.DataFrame, row_id_column_name: str) -> float:
    """
    Memory-efficient version using batch processing
    """
    
    # Convert submission to embedding dict
    feat_cols = [col for col in submission.columns if col.startswith('feature_')]
    embedding_dict = {}
    for _, row in submission.iterrows():
        img_id = row['image_name']
        vec = row[feat_cols].values.astype(np.float32)
        # Normalize for cosine similarity
        vec = vec / (np.linalg.norm(vec) + 1e-8)
        embedding_dict[img_id] = vec

    # Get gallery IDs and create separate lists
    all_image_ids = set(submission['image_name'].values)
    
    query_ids = set(solution['query'].values)
    gallery_ids = list(all_image_ids - query_ids)
    
    # Extract gallery embeddings as numpy array
    gallery_embeddings = np.array([embedding_dict[img_id] for img_id in gallery_ids 
                                   if img_id in embedding_dict])
    gallery_ids = [img_id for img_id in gallery_ids if img_id in embedding_dict]

    if len(gallery_embeddings) == 0:
        return 0.0
        
    if len(all_image_ids) != 20000:
        return 0.0
        
    hits = 0
    topK = 3
    total_queries = 0
    
    for _, row in solution.iterrows():
        q_id = row['query']
        true_gallery_id = row['answer']

        if q_id not in embedding_dict:
            continue

        q_vec = embedding_dict[q_id]  # [D,]
        
        # Efficient dot product (cosine similarity for normalized vectors)
        sims = np.dot(gallery_embeddings, q_vec)  # [G,]
        
        # Find top 3 most similar
        topK_indices = np.argpartition(sims, -topK)[-topK:]
        topK_indices = topK_indices[np.argsort(sims[topK_indices])[::-1]]
        topK_ids = [gallery_ids[i] for i in topK_indices]

        if true_gallery_id in topK_ids:
            hits += 1
        total_queries += 1

    hit_at_K = hits / total_queries if total_queries > 0 else 0.0
    return hit_at_K