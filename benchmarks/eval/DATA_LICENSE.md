# Data licence and attribution

`osm_sample.json` (and any corpus produced by `build_osm_corpus.py`) is a **derived database of OpenStreetMap data**.

> Contains information from OpenStreetMap, (c) OpenStreetMap contributors, made available under the
> [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/).
> Map data copyright: <https://www.openstreetmap.org/copyright>

What this means for you:

- The address labels in `osm_sample.json` (street, house number, city, state, postcode) are copied from the
  `addr:*` tags of OpenStreetMap objects, fetched via the Overpass API. The object id of every record is kept in
  its `source` field (for example `osm:way/12345`) so each label can be traced back to its OSM object.
- The sample is a derivative database under ODbL: if you redistribute it or a database derived from it, you must
  keep this attribution, offer the result under ODbL, and keep it open. The ODbL applies to the data in
  `osm_sample.json`, not to the MIT-licensed source code of this repository.
- The "renderings" (the messy input strings) are generated deterministically from the labels by string
  transformations; they are part of the same derived database.

Quality statement:

- The sample is **OSM-derived and NOT human-reviewed**. OSM tags are volunteer-entered. They contain typos,
  inconsistent abbreviation, local conventions and occasional wrong values. Disagreements between the engine and a
  label are therefore not always engine errors. See `docs/evaluation.md`.
- No personal data is intended to be in the sample, but it consists of real building addresses; do not use it to
  identify or contact individuals.

Fetching etiquette: the builder identifies itself with a descriptive `User-Agent` containing the project URL,
waits between requests, retries with back-off, queries small bounding boxes with small result limits, and caches
every response on disk. Please keep it that way and respect the
[Overpass usage policy](https://wiki.openstreetmap.org/wiki/Overpass_API#Public_Overpass_API_instances).
