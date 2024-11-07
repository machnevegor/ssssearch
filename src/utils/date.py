from datetime import datetime, timezone

__all__ = ("is_date_past",)


def is_date_past(date: datetime) -> bool:
    """
    Check if specified date is in the past.

    :param date: Date to compare with the current date.
    :return: True if the date is in the past; False otherwise.
    """
    return datetime.now(timezone.utc) > date
