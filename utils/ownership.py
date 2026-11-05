'''Utility helpers for ownership verification across the backend.'''

from fastapi import HTTPException, status


def verify_owner(resource_user_id: int, current_user_id: int) -> None:
    """Raise 403 if the authenticated user does not own the resource.

    Args:
        resource_user_id: The ``user_id`` stored on the resource record.
        current_user_id: The ``id`` of the currently authenticated user.
    """
    if resource_user_id != current_user_id:
        # Do not reveal whether the resource exists – treat as forbidden.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to the requested resource is forbidden.",
        )

