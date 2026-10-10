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

# VCS fields

| JSON field | Python property | Meaning |
| --- | --- | --- |
| `vcs:type` | `vcs_type` | Version-control system, e.g. `git`, `svn`, or a custom name. |
| `vcs:branch` | `branch` | Line of development, e.g. `main`. |
| `vcs:revision` | `revision` | Exact revision, e.g. a commit hash or changelist. |
| `vcs:tag` | `tag` | Release marker, e.g. `v1.0.0`. |

All four fields are optional nonempty strings in the [v0.1.0 schema](https://stac-extensions.github.io/vcs/v0.1.0/schema.json). Unknown `vcs:` fields are rejected; unrelated metadata is permitted. System names are not an enum. The schema applies these constraints to Catalogs, Collections, Item properties, Assets, Links, and `linkTemplates`.

Getters return `None` for missing fields; setters accept `None` to remove fields. Setters and `apply()` do not perform schema validation. Empty strings can be stored but fail subsequent validation.

The [versioned specification](https://github.com/stac-extensions/vcs/tree/v0.1.0) asks for at least one VCS field where the extension is used. The published JSON Schema does not enforce that requirement. Set at least one field for a meaningful reference.
