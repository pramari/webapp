"""
Interactive Componeents for `webapp` package.
"""

from .likes import LikeCreateView, LikeDeleteView, LikeDetailView, LikeListView
from .following import (
    FollowingCreateView,
    FollowingDeleteView,
    FollowingDetailView,
    FollowingListView,
)

__all__ = [
    "LikeCreateView",
    "LikeDeleteView",
    "LikeDetailView",
    "LikeListView",
    "FollowingCreateView",
    "FollowingDeleteView",
    "FollowingDetailView",
    "FollowingListView",
]
