"""Enumssssssss
All the constants we might use
"""
import enum


class eStatus(enum.Enum):
    """Staus Constants
        Maps the _correct_ Status ids used in our db :)
        Please when creating your Statuses create them in this order:

        - name=pending then
        - name=started and so on...
        - name=ended
        - name=cancelled

    """
    PENDING = 1
    STARTED = 2
    ENDED = 3
    CANCELLED = 4
