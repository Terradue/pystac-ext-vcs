# Copyright 2026 Terradue
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Read and write VCS v0.1.0 metadata on PySTAC objects, assets, and links.

Use ``VcsExtension.ext(target, add_if_missing=True)`` to declare the extension
on a STAC object or the owner of an asset or link before setting its fields.
"""

from __future__ import annotations

from typing import ClassVar, Generic, Literal, TypeVar

from pystac.extensions.base import ExtensionManagementMixin, PropertiesExtension
from pystac.extensions.hooks import ExtensionHooks

import pystac

SCHEMA_URI = "https://stac-extensions.github.io/vcs/v0.1.0/schema.json"
TYPE_PROP = "vcs:type"
BRANCH_PROP = "vcs:branch"
REVISION_PROP = "vcs:revision"
TAG_PROP = "vcs:tag"

T = TypeVar("T", bound="pystac.Catalog | pystac.Item | pystac.Asset | pystac.Link")


class VcsExtension(
    Generic[T],
    PropertiesExtension,
    ExtensionManagementMixin[pystac.Catalog | pystac.Collection | pystac.Item],
):
    """Access version-control metadata stored directly on a PySTAC target.

    Catalogs and Collections store fields at the top level; Items use their
    properties. Assets and Links use their own extra fields, without inheriting
    metadata from their owners. Use ``ext()`` to check the schema declaration.

    Attributes:
        obj: The target whose metadata is mutated by this wrapper.
    """

    name: Literal["vcs"] = "vcs"

    def __init__(self, obj: T) -> None:
        """Wrap a target's metadata without checking its extension declaration."""
        self.obj = obj
        if isinstance(obj, pystac.Item):
            self.properties = obj.properties
        elif isinstance(obj, (pystac.Catalog, pystac.Asset, pystac.Link)):
            self.properties = obj.extra_fields
        else:
            raise pystac.ExtensionTypeError(self._ext_error_message(obj))

    def apply(
        self,
        vcs_type: str | None = None,
        branch: str | None = None,
        revision: str | None = None,
        tag: str | None = None,
    ) -> None:
        """Replace all four VCS fields in place, clearing omitted fields.

        Args:
            vcs_type: Version-control system name, such as ``git`` or ``svn``.
            branch: Line of development, such as ``main``.
            revision: Exact revision identifier, such as a commit hash.
            tag: Release marker, such as ``v1.0.0``.

        Values are serialized as supplied; call STAC validation separately to
        enforce the schema's nonempty-string constraints.
        """
        self.vcs_type = vcs_type
        self.branch = branch
        self.revision = revision
        self.tag = tag

    @property
    def vcs_type(self) -> str | None:
        """The version-control system name, or None when absent."""
        return self._get_property(TYPE_PROP, str)

    @vcs_type.setter
    def vcs_type(self, value: str | None) -> None:
        self._set_property(TYPE_PROP, value)

    @property
    def branch(self) -> str | None:
        """The line of development, or None when absent."""
        return self._get_property(BRANCH_PROP, str)

    @branch.setter
    def branch(self, value: str | None) -> None:
        self._set_property(BRANCH_PROP, value)

    @property
    def revision(self) -> str | None:
        """The exact revision identifier, or None when absent."""
        return self._get_property(REVISION_PROP, str)

    @revision.setter
    def revision(self, value: str | None) -> None:
        self._set_property(REVISION_PROP, value)

    @property
    def tag(self) -> str | None:
        """The release marker, or None when absent."""
        return self._get_property(TAG_PROP, str)

    @tag.setter
    def tag(self, value: str | None) -> None:
        self._set_property(TAG_PROP, value)

    @classmethod
    def get_schema_uri(cls) -> str:
        """Return the VCS v0.1.0 schema identifier."""
        return SCHEMA_URI

    @classmethod
    def ext(cls, obj: T, add_if_missing: bool = False) -> VcsExtension[T]:
        """Wrap a target after checking its VCS extension declaration.

        Args:
            obj: Catalog, Collection, Item, Asset, or Link to extend.
            add_if_missing: Add the schema URI to the target or its owner.
                Unowned Assets and Links can be wrapped only when False.

        Raises:
            pystac.ExtensionNotImplemented: If the target or its owner has no
                VCS declaration and ``add_if_missing`` is False.
            pystac.STACError: If adding the declaration to an unowned target.
            pystac.ExtensionTypeError: If the target type is unsupported.
        """
        if isinstance(obj, (pystac.Catalog, pystac.Item)):
            cls.ensure_has_extension(obj, add_if_missing)
        elif isinstance(obj, (pystac.Asset, pystac.Link)):
            cls.ensure_owner_has_extension(obj, add_if_missing)
        else:
            raise pystac.ExtensionTypeError(cls._ext_error_message(obj))
        return cls(obj)

    def __repr__(self) -> str:
        return f"<VcsExtension {self.obj!r}>"


class VcsExtensionHooks(ExtensionHooks):
    """Identify VCS metadata for PySTAC extension migration hooks."""

    schema_uri = SCHEMA_URI
    prev_extension_ids: ClassVar[set[str]] = set()
    stac_object_types: ClassVar[set[pystac.STACObjectType]] = {
        pystac.STACObjectType.CATALOG,
        pystac.STACObjectType.COLLECTION,
        pystac.STACObjectType.ITEM,
    }


VCS_EXTENSION_HOOKS: ExtensionHooks = VcsExtensionHooks()
