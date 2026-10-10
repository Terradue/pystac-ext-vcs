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

# Scope, architecture, and validation

## Package structure

The distribution is `pystac-ext-vcs`; import the wrapper from `pystac.extensions.vcs`. The wheel excludes the shared namespace initializer owned by PySTAC.

`VcsExtension` uses PySTAC's `PropertiesExtension` and `ExtensionManagementMixin`. It wraps existing metadata dictionaries in place, preserving normal PySTAC serialization and cloning. No separate schema model or generated data class is needed. The authoritative contract remains the [published VCS v0.1.0 JSON Schema](https://stac-extensions.github.io/vcs/v0.1.0/schema.json).

`VCS_EXTENSION_HOOKS` identifies the schema and the Catalog, Collection, and Item object types. There are no previous extension identifiers. The package does not automatically register migration hooks or an `.ext.vcs` accessor.

## Validation boundaries

Property assignments, `apply()`, and serialization do not run JSON Schema validation. `apply()` updates fields sequentially and clears omitted values. It does not create repository links or resolve branches and tags.

Install `pystac[validation]` and call the owning STAC object's `validate()` to check the complete document. Schema retrieval may require network access or an application-configured schema cache. Tests cache the unmodified published extension schema locally and validate its contract without network access.

The schema permits absent fields but rejects nulls, empty strings, non-string values, and unknown `vcs:` keys in its defined field locations. The prose specification additionally asks for at least one field; see the [field reference](../reference/fields.md).
