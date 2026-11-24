"""Tests for the Vitola SQLAlchemy model."""
import pathlib
import sys
import uuid
from decimal import Decimal

_db_dir = pathlib.Path(__file__).resolve().parent.parent
if str(_db_dir) not in sys.path:
    sys.path.insert(0, str(_db_dir))

from models.vitola import Vitola


class TestVitolaInstantiation:
    """Verify that Vitola can be constructed with the expected Python types."""

    def _make(self, **overrides) -> Vitola:
        defaults = dict(
            id=uuid.uuid4(),
            name="Robusto",
        )
        defaults.update(overrides)
        return Vitola(**defaults)

    def test_id_is_uuid(self):
        assert isinstance(self._make().id, uuid.UUID)

    def test_name_is_str(self):
        assert isinstance(self._make().name, str)

    def test_optional_fields_default_none(self):
        vitola = Vitola(id=uuid.uuid4(), name="Minimal Vitola")
        assert vitola.length_inches is None
        assert vitola.ring_gauge is None

    def test_length_inches_stored(self):
        vitola = self._make(length_inches=Decimal("5.00"))
        assert vitola.length_inches == Decimal("5.00")

    def test_ring_gauge_stored(self):
        vitola = self._make(ring_gauge=50)
        assert vitola.ring_gauge == 50

    def test_tablename(self):
        assert Vitola.__tablename__ == "vitola"
