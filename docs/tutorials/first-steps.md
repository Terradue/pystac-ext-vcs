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

# Record a source revision

[Install the package](../how-to/install.md), then run this example:

```python
import pystac
from pystac.extensions.vcs import VcsExtension

catalog = pystac.Catalog("source", "Source-controlled catalog")
vcs = VcsExtension.ext(catalog, add_if_missing=True)
vcs.apply(vcs_type="git", branch="main", revision="abc123", tag="v1.0.0")

source = pystac.Link("vcs", "https://example.org/team/repository")
catalog.add_link(source)
VcsExtension.ext(source).apply(vcs_type="git", revision="abc123")

serialized = catalog.to_dict()
assert serialized["vcs:branch"] == "main"
assert VcsExtension.get_schema_uri() in serialized["stac_extensions"]
restored = pystac.Catalog.from_dict(serialized)
assert VcsExtension.ext(restored).revision == "abc123"
```

Collections use the same top-level fields; Items store VCS metadata in `properties`. Links and Assets store their own fields and do not inherit their owner's values. Use `VcsExtension.ext(target)` explicitly; no `target.ext.vcs` shortcut is registered.

Serialization does not perform validation. See [validation boundaries](../explanation/architecture.md#validation-boundaries).
