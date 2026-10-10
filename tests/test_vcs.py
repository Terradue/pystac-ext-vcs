from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from pystac.validation.stac_validator import JsonSchemaSTACValidator

import pystac
from pystac.extensions.vcs import SCHEMA_URI, VCS_EXTENSION_HOOKS, VcsExtension


@pytest.fixture(params=["catalog", "collection", "item"])
def stac_object(request: pytest.FixtureRequest) -> pystac.Catalog | pystac.Item:
    if request.param == "catalog":
        return pystac.Catalog("example", "Example catalog")
    if request.param == "collection":
        return pystac.Collection(
            "example",
            "Example collection",
            pystac.Extent(
                pystac.SpatialExtent([-180, -90, 180, 90]),
                pystac.TemporalExtent([None, None]),
            ),
        )
    return pystac.Item("example", None, None, datetime(2026, 1, 1, tzinfo=timezone.utc), {})


@pytest.fixture
def validator() -> JsonSchemaSTACValidator:
    validator = JsonSchemaSTACValidator()
    schema_path = Path(__file__).parent / "data" / "vcs-v0.1.0-schema.json"
    validator.schema_cache[SCHEMA_URI] = json.loads(schema_path.read_text())
    return validator


def test_extension_management(stac_object: pystac.Catalog | pystac.Item) -> None:
    with pytest.raises(pystac.ExtensionNotImplemented):
        VcsExtension.ext(stac_object)
    extension = VcsExtension.ext(stac_object, add_if_missing=True)
    assert extension.obj is stac_object
    VcsExtension.add_to(stac_object)
    assert stac_object.stac_extensions == [SCHEMA_URI]
    assert VcsExtension.has_extension(stac_object)
    VcsExtension.remove_from(stac_object)
    assert not VcsExtension.has_extension(stac_object)


def test_fields_round_trip(
    stac_object: pystac.Catalog | pystac.Item, validator: JsonSchemaSTACValidator
) -> None:
    extension = VcsExtension.ext(stac_object, add_if_missing=True)
    assert (extension.vcs_type, extension.branch, extension.revision, extension.tag) == (
        None,
        None,
        None,
        None,
    )
    extension.apply(vcs_type="custom-vcs", branch="main", revision="abc123", tag="v1.0")
    serialized = stac_object.to_dict()
    fields = serialized["properties"] if isinstance(stac_object, pystac.Item) else serialized
    assert {key: value for key, value in fields.items() if key.startswith("vcs:")} == {
        "vcs:type": "custom-vcs",
        "vcs:branch": "main",
        "vcs:revision": "abc123",
        "vcs:tag": "v1.0",
    }
    validator.validate_extension(serialized, stac_object.STAC_OBJECT_TYPE, "1.1.0", SCHEMA_URI)
    restored = VcsExtension.ext(type(stac_object).from_dict(serialized))
    assert (restored.vcs_type, restored.branch, restored.revision, restored.tag) == (
        "custom-vcs",
        "main",
        "abc123",
        "v1.0",
    )
    clone = VcsExtension.ext(stac_object.clone())
    clone.branch = "other"
    assert extension.branch == "main"
    assert "VcsExtension" in repr(extension)


def test_apply_and_removal(stac_object: pystac.Catalog | pystac.Item) -> None:
    extension = VcsExtension.ext(stac_object, add_if_missing=True)
    extension.properties["other:field"] = "preserved"
    extension.apply("git", "main", "abc", "v1")
    extension.apply(branch="next")
    assert (extension.vcs_type, extension.branch, extension.revision, extension.tag) == (
        None,
        "next",
        None,
        None,
    )
    extension.branch = None
    extension.branch = None
    assert not any(key.startswith("vcs:") for key in extension.properties)
    assert extension.properties["other:field"] == "preserved"
    assert VcsExtension.has_extension(stac_object)


@pytest.mark.parametrize(
    "target",
    [pystac.Asset("https://example.com/repo"), pystac.Link("vcs", "https://example.com/repo")],
)
def test_unowned_targets(target: pystac.Asset | pystac.Link) -> None:
    extension = VcsExtension.ext(target)
    extension.tag = "v1"
    assert target.extra_fields["vcs:tag"] == "v1"
    with pytest.raises(pystac.STACError, match="no owner"):
        VcsExtension.ext(target, add_if_missing=True)


@pytest.mark.parametrize("target_kind", ["asset", "link"])
def test_owned_targets(
    stac_object: pystac.Catalog | pystac.Item,
    target_kind: str,
    validator: JsonSchemaSTACValidator,
) -> None:
    target: pystac.Asset | pystac.Link
    if target_kind == "asset":
        if not isinstance(stac_object, (pystac.Item, pystac.Collection)):
            pytest.skip("Catalogs do not expose an assets API")
        target = pystac.Asset("https://example.com/repo")
        stac_object.add_asset("source", target)
    else:
        target = pystac.Link("vcs", "https://example.com/repo")
        stac_object.add_link(target)
    with pytest.raises(pystac.ExtensionNotImplemented):
        VcsExtension.ext(target)
    extension = VcsExtension.ext(target, add_if_missing=True)
    VcsExtension.ext(stac_object).branch = "parent"
    assert extension.branch is None
    extension.apply("git", "main", "abc", "v1")
    assert target.to_dict()["vcs:branch"] == "main"
    restored = type(target).from_dict(target.to_dict())
    assert VcsExtension.ext(restored).revision == "abc"
    validator.validate_extension(
        stac_object.to_dict(), stac_object.STAC_OBJECT_TYPE, "1.1.0", SCHEMA_URI
    )


@pytest.mark.parametrize("field", ["vcs:type", "vcs:branch", "vcs:revision", "vcs:tag"])
@pytest.mark.parametrize("invalid_value", ["", None, 42, [], {}])
def test_schema_rejects_invalid_fields(
    stac_object: pystac.Catalog | pystac.Item,
    validator: JsonSchemaSTACValidator,
    field: str,
    invalid_value: object,
) -> None:
    extension = VcsExtension.ext(stac_object, add_if_missing=True)
    extension.properties[field] = invalid_value
    with pytest.raises(pystac.STACValidationError):
        validator.validate_extension(
            stac_object.to_dict(), stac_object.STAC_OBJECT_TYPE, "1.1.0", SCHEMA_URI
        )


def test_schema_rejects_unknown_fields(
    stac_object: pystac.Catalog | pystac.Item, validator: JsonSchemaSTACValidator
) -> None:
    extension = VcsExtension.ext(stac_object, add_if_missing=True)
    extension.properties["vcs:unknown"] = "invalid"
    with pytest.raises(pystac.STACValidationError):
        validator.validate_extension(
            stac_object.to_dict(), stac_object.STAC_OBJECT_TYPE, "1.1.0", SCHEMA_URI
        )


def test_link_template(validator: JsonSchemaSTACValidator) -> None:
    catalog = pystac.Catalog("example", "Example catalog")
    VcsExtension.add_to(catalog)
    template = pystac.Link("vcs", "https://example.com/{repository}")
    VcsExtension.ext(template).apply("git", branch="main")
    catalog.extra_fields["linkTemplates"] = [template.to_dict()]
    validator.validate_extension(catalog.to_dict(), catalog.STAC_OBJECT_TYPE, "1.1.0", SCHEMA_URI)


def test_hooks() -> None:
    assert VCS_EXTENSION_HOOKS.schema_uri == SCHEMA_URI
    assert VCS_EXTENSION_HOOKS.prev_extension_ids == set()
    assert VCS_EXTENSION_HOOKS.stac_object_types == {
        pystac.STACObjectType.CATALOG,
        pystac.STACObjectType.COLLECTION,
        pystac.STACObjectType.ITEM,
    }


def test_schema_allows_no_fields(
    stac_object: pystac.Catalog | pystac.Item, validator: JsonSchemaSTACValidator
) -> None:
    VcsExtension.add_to(stac_object)
    validator.validate_extension(
        stac_object.to_dict(), stac_object.STAC_OBJECT_TYPE, "1.1.0", SCHEMA_URI
    )


@pytest.mark.parametrize("location", ["assets", "links", "linkTemplates"])
@pytest.mark.parametrize("field", ["vcs:branch", "vcs:unknown"])
def test_schema_rejects_invalid_nested_fields(
    validator: JsonSchemaSTACValidator, location: str, field: str
) -> None:
    catalog = pystac.Catalog("example", "Example catalog")
    VcsExtension.add_to(catalog)
    serialized = catalog.to_dict()
    fields = {"href": "https://example.com/repo", "rel": "vcs", field: ""}
    serialized[location] = {"source": fields} if location == "assets" else [fields]
    with pytest.raises(pystac.STACValidationError):
        validator.validate_extension(serialized, catalog.STAC_OBJECT_TYPE, "1.1.0", SCHEMA_URI)
