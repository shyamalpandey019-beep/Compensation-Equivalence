# src/score.py

def calculate_score(percentile: float, col_adjusted_usd: float) -> int:
    """
    Calculates a 0-100 score based on local market percentile (50% weight) 
    and global purchasing power (50% weight).
    """
    # Assuming $100,000 COL-Adjusted USD is a "perfect" 100 for the purchasing power half
    pp_points = (col_adjusted_usd / 100000.0) * 100
    
    # Cap purchasing power points at 100 so billionaires don't break the scale
    pp_points = min(pp_points, 100.0)
    
    # Blend the two metrics
    final_score = (percentile * 0.5) + (pp_points * 0.5)
    
    return int(final_score)