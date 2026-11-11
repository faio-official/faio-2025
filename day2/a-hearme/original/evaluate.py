import pandas as pd
import pandas.api.types

class ParticipantVisibleError(Exception):
    """Visible error for Kaggle participants."""
    pass

def score(solution: pd.DataFrame, submission: pd.DataFrame, row_id_column_name: str) -> float:
    """
    Music recommendation system - custom metric.
    
    Description:
    Number of users: 1500
    For each user, we take their predicted top-50 tracks (submission).
    Total number of rows: 75,000
    If the user actually listened to the track (solution contains ‘share’ from 0.0 to 1.0),
    we account for the actual listening share.
    0 - didn’t listen, 0.5 - half listened, 1 - fully listened.
    We sum across all 50 tracks and average across users.
    Returns the mean normalized metric  value (float, 0-1).
    """
    # Remove the row ID column
    del solution[row_id_column_name]
    del submission[row_id_column_name]
    
    # Structure validation
    required_cols = {"user_id", "item_id", "rank"}
    if set(submission.columns) != required_cols:
        raise ParticipantVisibleError(f"Submission must have columns: {required_cols}")
    
    # Check number of users
    num_users = submission["user_id"].nunique()
    if num_users != 1500:
        raise ParticipantVisibleError(f"Submission must have exactly 5000 users, found {num_users}")
    
    # Check number of tracks per user
    user_counts = submission.groupby("user_id").size()
    if not all(user_counts == 50):
        raise ParticipantVisibleError("Each user must have exactly 50 recommendations.")
    
    # Check uniqueness and range of ranks
    for user_id, user_df in submission.groupby("user_id"):
        ranks = set(user_df["rank"])
        if ranks != set(range(1, 51)):
            raise ParticipantVisibleError(f"Invalid rank values for user {user_id}")
    
    # Check for required columns in solution
    expected_solution_cols = {"user_id", "item_id", "share"}
    if not expected_solution_cols.issubset(solution.columns):
        raise ParticipantVisibleError(f"Solution must have columns: {expected_solution_cols}")
    
    # Merge predictions with ground truth data
    final = pd.merge(submission, solution, on=["user_id", "item_id"], how="left")
    
    # Fill NaN for unlistened tracks
    final["share"] = final["share"].fillna(0)
    
    # Sum of listening shares per user
    user_scores = final.groupby("user_id")["share"].sum()
    
    # Final metric (average sum of listens)
    metric = user_scores.mean() / 50
    
    # Validate return value
    if not pd.api.types.is_number(metric) or not pd.notnull(metric) or metric < 0:
        raise ParticipantVisibleError("Metric computation failed or returned invalid value.")
    
    return float(metric)