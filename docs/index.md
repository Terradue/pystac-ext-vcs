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

# VCS PySTAC extension

`pystac-ext-vcs` provides `VcsExtension` for version-control references on PySTAC Catalogs, Collections, Items, Assets, and Links.

The wrapper targets the [VCS v0.1.0 schema](https://stac-extensions.github.io/vcs/v0.1.0/schema.json). Its four optional fields describe the version-control system, branch, exact revision, and release tag. System names are open strings, so Git, Subversion, and other systems are supported.

```bash
python -m pip install pystac-ext-vcs
```

- [Record a source revision](tutorials/first-steps.md).
- [Update fields, assets, links, and templates](how-to/use-extension.md).
- [Look up VCS fields](reference/fields.md).
- [Browse the Python API](reference/api.md).
- [Understand architecture and validation](explanation/architecture.md).
