import re
import os

# Define a robust lexicon for Indonesian financial sentiment
POSITIVE_WORDS = {
    "naik", "menguat", "untung", "laba", "bullish", "hijau", "beli", "tumbuh", 
    "lonjak", "melejit", "meningkat", "optimis", "cuan", "bagus", "positif", 
    "cerah", "rekor", "akuisisi", "ekspansi", "dividen", "sanjung", "rekomendasi beli",
    "menarik", "potensi", "terdongkrak", "membaik", "terangkat", "melaju"
}

NEGATIVE_WORDS = {
    "turun", "melemah", "rugi", "buntung", "bearish", "merah", "jual", "susut", 
    "anjlok", "terkoreksi", "koreksi", "menurun", "pesimis", "tekanan", "panik", 
    "negatif", "waspada", "pangkas", "inflasi", "buruk", "ambles", "merosot",
    "tertekan", "ambruk", "beban", "utang", "hancur", "defisit", "denda"
}

# Global pipeline variable for lazy loading
_hf_pipeline = None
_hf_model_loaded = False

def init_hf_pipeline():
    """
    Attempt to initialize the Hugging Face sentiment analysis pipeline.
    Falls back gracefully if transformers or torch is not installed, or downloading fails.
    """
    global _hf_pipeline, _hf_model_loaded
    if _hf_model_loaded:
        return _hf_pipeline
        
    try:
        from transformers import pipeline
        # Use a lightweight, popular Indonesian sentiment classifier model
        model_name = "w11wo/indonesian-roberta-base-sentiment-classifier"
        # Set a short timeout context if possible or just load it
        _hf_pipeline = pipeline(
            "sentiment-analysis", 
            model=model_name,
            tokenizer=model_name,
            device=-1 # Use CPU to avoid CUDA dependency issues
        )
        _hf_model_loaded = True
    except Exception as e:
        # Fallback to lexicon-based analyzer
        _hf_pipeline = None
        _hf_model_loaded = True # Mark as attempted so we don't try on every call
        print(f"HF pipeline load failed, falling back to Lexicon Sentiment Analysis. Error: {e}")
        
    return _hf_pipeline

def analyze_lexicon(text):
    """
    Fallback Indonesian Lexicon Sentiment Analyzer.
    """
    text_clean = re.sub(r'[^\w\s]', '', text.lower())
    words = text_clean.split()
    
    pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
    neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)
    
    # Check for specific multi-word phrases
    for phrase in ["rekomendasi beli", "kinerja cerah", "target naik", "rekor tertinggi"]:
        if phrase in text.lower():
            pos_count += 2
            
    for phrase in ["rekomendasi jual", "tekanan jual", "waspada koreksi", "rekor terendah"]:
        if phrase in text.lower():
            neg_count += 2
            
    total = pos_count + neg_count
    if total == 0:
        return "NEUTRAL", 0.0
        
    score = (pos_count - neg_count) / total
    
    if score > 0.15:
        label = "POSITIVE"
    elif score < -0.15:
        label = "NEGATIVE"
    else:
        label = "NEUTRAL"
        
    return label, score

def analyze_sentiment(text, use_hf=False):
    """
    Main sentiment analysis function.
    Returns:
        label (str): "POSITIVE", "NEGATIVE", or "NEUTRAL"
        score (float): Numeric score representing sentiment intensity.
                       For HF: confidence score (0 to 1).
                       For Lexicon: score from -1 to 1.
    """
    if not text or not isinstance(text, str):
        return "NEUTRAL", 0.0

    if use_hf:
        pipeline_obj = init_hf_pipeline()
        if pipeline_obj is not None:
            try:
                result = pipeline_obj(text)[0]
                # Label mapping depends on the model (e.g. w11wo uses label_0, label_1, label_2 or specific labels)
                # Let's map typical outputs
                label_raw = result['label'].upper()
                score = result['score']
                
                # Check for model-specific labels
                # 'w11wo/indonesian-roberta-base-sentiment-classifier' maps:
                # 0 -> positive, 1 -> neutral, 2 -> negative
                # or labels might be "LABEL_0", "LABEL_1", "LABEL_2"
                if "LABEL_0" in label_raw or "POS" in label_raw:
                    return "POSITIVE", score
                elif "LABEL_2" in label_raw or "NEG" in label_raw:
                    return "NEGATIVE", -score
                else:
                    return "NEUTRAL", 0.0
            except Exception as e:
                # Fall back to lexicon if inference fails
                pass
                
    # Default fallback to Lexicon
    return analyze_lexicon(text)
