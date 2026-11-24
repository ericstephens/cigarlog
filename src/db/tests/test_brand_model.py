"""Tests for the Brand SQLAlchemy model."""
import pathlib
import sys
import uuid

_db_dir = pathlib.Path(__file__).resolve().parent.parent
if str(_db_dir) not in sys.path:
    sys.path.insert(0, str(_db_dir))

from models.brand import Brand


class TestBrandInstantiation:
    """Verify that Brand can be constructed with the expected Python types."""

    def _make(self, **overrides) -> Brand:
        defaults = dict(
            id=uuid.uuid4(),
            name="Arturo Fuente",
        )
        defaults.update(overrides)
        return Brand(**defaults)

    def test_id_is_uuid(self):
        assert isinstance(self._make().id, uuid.UUID)

    def test_name_is_str(self):
        assert isinstance(self._make().name, str)

    def test_optional_fields_default_none(self):
        brand = Brand(id=uuid.uuid4(), name="Minimal Brand")
        assert brand.country is None
        assert brand.website is None
        assert brand.notes is None
        assert brand.deleted_at is None

    def test_country_stored(self):
        brand = self._make(country="Dominican Republic")
        assert brand.country == "Dominican Republic"

    def test_website_stored(self):
        brand = self._make(website="https://arturo-fuente.com")
        assert brand.website == "https://arturo-fuente.com"

    def test_notes_stored(self):
        brand = self._make(notes="Family-owned since 1912")
        assert brand.notes == "Family-owned since 1912"

    def test_tablename(self):
        assert Brand.__tablename__ == "brand"
