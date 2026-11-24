"""Tests for the Factory SQLAlchemy model."""
import pathlib
import sys
import uuid

_db_dir = pathlib.Path(__file__).resolve().parent.parent
if str(_db_dir) not in sys.path:
    sys.path.insert(0, str(_db_dir))

from models.factory import Factory


class TestFactoryInstantiation:
    """Verify that Factory can be constructed with the expected Python types."""

    def _make(self, **overrides) -> Factory:
        defaults = dict(
            id=uuid.uuid4(),
            name="General Cigar Company",
        )
        defaults.update(overrides)
        return Factory(**defaults)

    def test_id_is_uuid(self):
        assert isinstance(self._make().id, uuid.UUID)

    def test_name_is_str(self):
        assert isinstance(self._make().name, str)

    def test_optional_fields_default_none(self):
        factory = Factory(id=uuid.uuid4(), name="Minimal Factory")
        assert factory.city is None
        assert factory.country is None
        assert factory.notes is None
        assert factory.deleted_at is None

    def test_city_stored(self):
        factory = self._make(city="Santiago")
        assert factory.city == "Santiago"

    def test_country_stored(self):
        factory = self._make(country="Dominican Republic")
        assert factory.country == "Dominican Republic"

    def test_notes_stored(self):
        factory = self._make(notes="Produces many premium brands")
        assert factory.notes == "Produces many premium brands"

    def test_tablename(self):
        assert Factory.__tablename__ == "factory"
