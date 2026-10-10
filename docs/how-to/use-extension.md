<!--
Copyright 2026 Terradue

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# Work with VCS metadata

## Update and clear fields

Continue from the [tutorial](../tutorials/first-steps.md):

```python
vcs = VcsExtension.ext(catalog)
vcs.branch = "develop"
vcs.tag = None
assert "vcs:tag" not in catalog.extra_fields
vcs.apply(vcs_type="svn", revision="1234")
assert vcs.branch is None
```

Missing fields return `None`; assigning `None` removes the field. `apply()` replaces all four fields, clearing any omitted arguments. Other metadata is preserved.

## Declare the extension

`VcsExtension.ext(target)` checks the schema declaration. Pass `add_if_missing=True` to add it to a Catalog, Collection, or Item, or to the owner of an Asset or Link. Repeated calls do not duplicate the declaration.

Use `VcsExtension.add_to(stac_object)`, `has_extension(stac_object)`, and `remove_from(stac_object)` to manage declarations directly. Removing a declaration does not delete stored fields.

## Attach Assets and Links

```python
import pystac
from pystac.extensions.vcs import VcsExtension

collection = pystac.Collection(
    "software", "Source code",
    pystac.Extent(
        pystac.SpatialExtent([[-180, -90, 180, 90]]),
        pystac.TemporalExtent([[None, None]]),
    ),
)
asset = pystac.Asset("https://example.org/source.zip")
collection.add_asset("source", asset)
VcsExtension.ext(asset, add_if_missing=True).apply(vcs_type="git", tag="v1.0")

link = pystac.Link("vcs", "https://example.org/repository")
collection.add_link(link)
VcsExtension.ext(link).revision = "abc123"
```

Attach the Asset or Link before using `add_if_missing=True`. An unowned Asset or Link can be wrapped with the default `False`, but its eventual owner must declare the extension. Values on owners are never inherited.

## Link templates

PySTAC stores `linkTemplates` as extra fields. Build a template with a standalone Link, then serialize it into the owning object's template list:

```python
template = pystac.Link("vcs", "https://example.org/{repository}")
VcsExtension.ext(template).apply(vcs_type="git", branch="main")
VcsExtension.add_to(collection)
collection.extra_fields["linkTemplates"] = [template.to_dict()]
```

This assignment replaces the template list. To edit an existing template, load its dictionary with `pystac.Link.from_dict()`, edit it using `VcsExtension.ext()`, and write `to_dict()` back to the list.

There is no dedicated summaries, item-asset-definition, or asset-template helper in this implementation; it covers the field locations explicitly constrained by the v0.1.0 JSON Schema.
