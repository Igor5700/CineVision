import pytest

from movielib.domain.errors import DomainValidationError
from movielib.domain.value_objects.balance import Balance
from movielib.domain.value_objects.telegram_id import TelegramId


def test_balance_accepts_non_negative_amounts() -> None:
    assert int(Balance(0)) == 0
    assert int(Balance(100)) == 100


def test_balance_rejects_negative_amounts() -> None:
    with pytest.raises(DomainValidationError):
        Balance(-1)


def test_telegram_id_accepts_positive_values() -> None:
    assert int(TelegramId(123)) == 123
    assert str(TelegramId(123)) == "123"


@pytest.mark.parametrize("value", [0, -1, -999])
def test_telegram_id_rejects_non_positive_values(value: int) -> None:
    with pytest.raises(DomainValidationError):
        TelegramId(value)
