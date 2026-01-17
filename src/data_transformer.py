"""Transform Instagram Graph API data to the format expected by the RAG model."""

import json
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path

from instagram_api import extract_hashtags, calculate_engagement_rate


class InstagramDataTransformer:
    """
    Transform Instagram Graph API responses to the format expected by the RAG pipeline.

    Expected format (from sample_posts.json):
    {
        "id": "post_001",
        "caption": "...",
        "media_type": "reel" | "photo" | "carousel",
        "timestamp": "2025-01-10T08:30:00Z",
        "metrics": {
            "likes": 1250,
            "comments": 87,
            "shares": 45,
            "saves": 320,
            "reach": 15000,
            "impressions": 18500,
            "engagement_rate": 11.3
        },
        "hashtags": ["tag1", "tag2"],
        "media_url": "https://..."
    }
    """

    # Map Instagram API media types to our format
    MEDIA_TYPE_MAP = {"IMAGE": "photo", "VIDEO": "reel", "CAROUSEL_ALBUM": "carousel"}

    def __init__(self, follower_count: int = 0):
        """
        Initialize the transformer.

        Args:
            follower_count: Follower count for engagement rate calculation.
        """
        self.follower_count = follower_count

    def transform_post(
        self, api_post: Dict[str, Any], post_index: int = 1
    ) -> Dict[str, Any]:
        """
        Transform a single post from Instagram API format to our format.

        Args:
            api_post: Post data from Instagram Graph API.
            post_index: Index for generating post ID.

        Returns:
            Transformed post dictionary.
        """
        # Extract insights if available
        insights = api_post.get("insights", {})
        if isinstance(insights, dict) and "data" in insights:
            # Parse insights data
            insights_dict = {}
            for insight in insights["data"]:
                insights_dict[insight["name"]] = insight["values"][0]["value"]
        else:
            insights_dict = {}

        # Get basic metrics
        likes = api_post.get("like_count", 0)
        comments = api_post.get("comments_count", 0)
        reach = insights_dict.get("reach", 0)
        impressions = insights_dict.get("impressions", 0)
        saves = insights_dict.get("saved", 0)

        # Calculate engagement (Instagram doesn't provide shares directly)
        # Using engagement from insights if available, otherwise calculate
        engagement_total = insights_dict.get("engagement", likes + comments)

        # Calculate engagement rate
        if self.follower_count > 0:
            engagement_rate = calculate_engagement_rate(
                likes, comments, self.follower_count
            )
        else:
            # Fallback: calculate based on reach if available
            if reach > 0:
                engagement_rate = round((engagement_total / reach) * 100, 2)
            else:
                engagement_rate = 0.0

        # Extract hashtags from caption
        caption = api_post.get("caption", "")
        hashtags = extract_hashtags(caption)

        # Map media type
        api_media_type = api_post.get("media_type", "IMAGE")
        media_type = self.MEDIA_TYPE_MAP.get(api_media_type, "photo")

        # Generate post ID
        post_id = api_post.get("id", f"post_{post_index:03d}")

        # Build transformed post
        transformed = {
            "id": post_id,
            "caption": caption,
            "media_type": media_type,
            "timestamp": api_post.get("timestamp", datetime.now().isoformat()),
            "metrics": {
                "likes": likes,
                "comments": comments,
                "shares": 0,  # Not available from Instagram API
                "saves": saves,
                "reach": reach,
                "impressions": impressions,
                "engagement_rate": engagement_rate,
            },
            "hashtags": hashtags,
            "media_url": api_post.get("media_url", api_post.get("permalink", "")),
        }

        return transformed

    def transform_posts(self, api_posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform multiple posts.

        Args:
            api_posts: List of posts from Instagram API.

        Returns:
            List of transformed posts.
        """
        transformed_posts = []

        for i, post in enumerate(api_posts, 1):
            try:
                transformed = self.transform_post(post, i)
                transformed_posts.append(transformed)
            except Exception as e:
                print(f"Warning: Failed to transform post {i}: {e}")
                continue

        return transformed_posts

    def transform_profile(self, api_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform profile data from Instagram API to our format.

        Expected format (from influencer_profile.json):
        {
            "username": "marie_lifestyle",
            "followers": 45000,
            "following": 890,
            "bio": "...",
            "niche": "lifestyle",
            "avg_engagement_rate": 8.5,
            "posting_frequency": "5 posts/week",
            "account_type": "creator",
            "joined_date": "2022-03-15"
        }

        Args:
            api_profile: Profile data from Instagram Graph API.

        Returns:
            Transformed profile dictionary.
        """
        transformed = {
            "username": api_profile.get("username", "unknown"),
            "followers": api_profile.get("followers_count", 0),
            "following": api_profile.get("follows_count", 0),
            "bio": api_profile.get("biography", ""),
            "niche": self._infer_niche(api_profile.get("biography", "")),
            "avg_engagement_rate": 0.0,  # Will be calculated from posts
            "posting_frequency": "N/A",  # Will be calculated from posts
            "account_type": "creator",
            "joined_date": datetime.now().strftime("%Y-%m-%d"),
        }

        # Update follower count for engagement calculations
        self.follower_count = transformed["followers"]

        return transformed

    def _infer_niche(self, bio: str) -> str:
        """
        Infer account niche from bio.

        Args:
            bio: Instagram bio text.

        Returns:
            Inferred niche category.
        """
        bio_lower = bio.lower()

        # Simple keyword matching
        niche_keywords = {
            "lifestyle": ["lifestyle", "life", "daily", "quotidien"],
            "fitness": ["fitness", "gym", "workout", "health", "sport"],
            "fashion": ["fashion", "style", "mode", "clothing"],
            "food": ["food", "cooking", "recipe", "cuisine", "chef"],
            "travel": ["travel", "voyage", "explore", "wanderlust"],
            "beauty": ["beauty", "makeup", "skincare", "beauté"],
            "tech": ["tech", "technology", "developer", "coding"],
            "business": ["business", "entrepreneur", "startup", "marketing"],
            "photography": ["photographer", "photography", "photo"],
        }

        for niche, keywords in niche_keywords.items():
            if any(keyword in bio_lower for keyword in keywords):
                return niche

        return "general"

    def calculate_profile_stats(
        self, profile: Dict[str, Any], posts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate additional profile statistics from posts.

        Args:
            profile: Profile dictionary.
            posts: List of posts.

        Returns:
            Updated profile with calculated stats.
        """
        if not posts:
            return profile

        # Calculate average engagement rate
        engagement_rates = [
            post["metrics"]["engagement_rate"]
            for post in posts
            if post["metrics"]["engagement_rate"] > 0
        ]

        if engagement_rates:
            profile["avg_engagement_rate"] = round(
                sum(engagement_rates) / len(engagement_rates), 2
            )

        # Calculate posting frequency
        if len(posts) >= 2:
            # Get date range
            timestamps = [post["timestamp"] for post in posts]
            dates = sorted(
                [datetime.fromisoformat(ts.replace("Z", "+00:00")) for ts in timestamps]
            )

            # Calculate days between first and last post
            days_diff = (dates[-1] - dates[0]).days

            if days_diff > 0:
                posts_per_week = (len(posts) / days_diff) * 7
                profile["posting_frequency"] = f"{posts_per_week:.1f} posts/week"

        return profile

    def save_to_json(
        self,
        posts: List[Dict[str, Any]],
        profile: Dict[str, Any],
        posts_output_path: Path,
        profile_output_path: Path,
    ):
        """
        Save transformed data to JSON files.

        Args:
            posts: Transformed posts.
            profile: Transformed profile.
            posts_output_path: Output path for posts JSON.
            profile_output_path: Output path for profile JSON.
        """
        # Wrap posts in the expected format
        posts_data = {"posts": posts}

        # Save posts
        with open(posts_output_path, "w", encoding="utf-8") as f:
            json.dump(posts_data, f, indent=2, ensure_ascii=False)

        print(f"✓ Saved {len(posts)} posts to {posts_output_path}")

        # Save profile
        with open(profile_output_path, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)

        print(f"✓ Saved profile to {profile_output_path}")


def transform_instagram_data(
    api_profile: Dict[str, Any],
    api_posts: List[Dict[str, Any]],
    output_dir: Path = None,
) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    High-level function to transform Instagram API data.

    Args:
        api_profile: Profile data from Instagram API.
        api_posts: List of posts from Instagram API.
        output_dir: Optional directory to save JSON files.

    Returns:
        Tuple of (profile, posts).
    """
    transformer = InstagramDataTransformer()

    # Transform profile
    profile = transformer.transform_profile(api_profile)

    # Transform posts
    posts = transformer.transform_posts(api_posts)

    # Calculate additional stats
    profile = transformer.calculate_profile_stats(profile, posts)

    # Save if output directory provided
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        posts_path = output_dir / "sample_posts.json"
        profile_path = output_dir / "influencer_profile.json"

        transformer.save_to_json(posts, profile, posts_path, profile_path)

    return profile, posts
