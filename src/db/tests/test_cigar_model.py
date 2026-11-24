"""Tests for the Cigar SQLAlchemy model."""
import pathlib
import sys
import uuid
from decimal import Decimal

_db_dir = pathlib.Path(__file__).resolve().parent.parent
if str(_db_dir) not in sys.path:
    sys.path.insert(0, str(_db_dir))

from models.cigar import Cigar


class TestCigarInstantiation:
    """Verify that Cigar can be constructed with the expected Python types."""

    def _make(self, **overrides) -> Cigar:
        brand_id = uuid.uuid4()
        defaults = dict(
            id=uuid.uuid4(),
            name="Opus X",
            brand_id=brand_id,
        )
        defaults.update(overrides)
        return Cigar(**defaults)

    def test_id_is_uuid(self):
        assert isinstance(self._make().id, uuid.UUID)

    def test_name_is_str(self):
        assert isinstance(self._make().name, str)

    def test_brand_id_is_uuid(self):
        assert isinstance(self._make().brand_id, uuid.UUID)

    def test_optional_fields_default_none(self):
        cigar = Cigar(id=uuid.uuid4(), name="Minimal Cigar", brand_id=uuid.uuid4())
        assert cigar.factory_id is None
        assert cigar.vitola_id is None
        assert cigar.wrapper is None
        assert cigar.binder_origin is None
        assert cigar.filler_origin is None
        assert cigar.strength is None
        assert cigar.msrp is None
        assert cigar.description is None
        assert cigar.deleted_at is None

    def test_factory_id_stored(self):
        factory_id = uuid.uuid4()
        cigar = self._make(factory_id=factory_id)
        assert cigar.factory_id == factory_id

    def test_vitola_id_stored(self):
        vitola_id = uuid.uuid4()
        cigar = self._make(vitola_id=vitola_id)
        assert cigar.vitola_id == vitola_id

    def test_strength_stored(self):
        cigar = self._make(strength="medium")
        assert cigar.strength == "medium"

    def test_msrp_stored(self):
        cigar = self._make(msrp=Decimal("24.99"))
        assert cigar.msrp == Decimal("24.99")

    def test_tablename(self):
        assert Cigar.__tablename__ == "cigar"
