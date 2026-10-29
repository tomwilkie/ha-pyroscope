# Repository purpose

`ha-pyroscope` is a Home Assistant custom integration, installed through HACS, that runs the
Pyroscope Python SDK (`pyroscope-io`) inside Home Assistant Core and sends continuous profiles to
a Pyroscope server or Grafana Cloud Profiles. [README.md](README.md) is the user documentation.

# Layout

| Path | Contents |
|---|---|
| `custom_components/pyroscope/__init__.py` | Starts the profiler on entry setup and stops it on unload |
| `custom_components/pyroscope/config_flow.py` | The setup form (URL, credentials, service name) and the options flow (sample rate, memory profiling) |
| `custom_components/pyroscope/strings.json` | UI strings. `translations/en.json` is an identical copy |
| `custom_components/pyroscope/manifest.json` | Integration manifest, including the pinned `pyroscope-io` version and the release version |
| `hacs.json` | HACS metadata, including the minimum Home Assistant version |
| `tests/` | `pytest-homeassistant-custom-component` tests |
| `.github/workflows/` | `ci.yml` (ruff and pytest), `validate.yml` (hassfest and the HACS action), `release.yml` (GitHub release on a `v*` tag) |

# Design rules

- **The SDK is process-global.** `pyroscope.configure` profiles the whole Python process, and a
  second call would replace the first. The manifest sets `single_config_entry`, so keep it.
- **Call the SDK from the executor.** `configure` and `shutdown` start and join native threads
  and do network I/O, so they run through `hass.async_add_executor_job`, never on the event loop.
- **Options changes reload the entry.** The options flow subclasses `OptionsFlowWithReload`,
  which unloads (`shutdown`) and sets up (`configure`) again. The SDK supports this cycle in one
  process.
- **Don't send identifying tags.** Tags are visible to anyone who can read the profiles. Don't
  add `hass.config.location_name`, the external URL or anything else that can identify the home.
- **Keep `strings.json` and `translations/en.json` identical.** Custom integrations get no
  build step that generates translations, so `%key:...%` references don't resolve. Write literal
  strings in both.
- **Keep the manifest keys ordered** as hassfest expects: `domain`, `name`, then the rest
  alphabetically.

# Development

Use `uv` with Python 3.14, the version Home Assistant requires:

```sh
uv venv -p 3.14
uv pip install -r requirements_test.txt
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Tests patch `custom_components.pyroscope.pyroscope` through the `mock_pyroscope` fixture, so
they never start the real profiler. Run all four commands before you commit, because CI runs the
same ones.

To try a change on a real instance, copy `custom_components/pyroscope/` into the instance's
`/config/custom_components/` and restart Home Assistant.

# Dependencies

- `pyroscope-io` is pinned in both `manifest.json` and `requirements_test.txt`. Bump them
  together. Before you bump it, check that PyPI has `musllinux` wheels for the new version on
  the Python version current Home Assistant uses, because the Home Assistant container runs
  Alpine and cannot build the Rust extension.
- `pytest-homeassistant-custom-component` pins a Home Assistant release. Dependabot opens weekly
  pull requests for it, for `ruff` and for the GitHub Actions.

# Releases

HACS offers users the GitHub releases. To release:

1. Bump `version` in `custom_components/pyroscope/manifest.json` and commit it.
2. Tag the commit `v<version>` and push the tag.

`release.yml` fails if the tag and the manifest version differ, and otherwise creates the
release with generated notes.

# Git workflow

Commit directly to `main`. Commit messages follow `<area>: <lowercase summary>`, for example
`config_flow: validate the url scheme` or `ci: pin ruff`, with a body explaining why when the
change is not self-evident.

This repo is public. Before every commit, check the change for credentials, Pyroscope or Grafana
Cloud tokens, instance IDs, home addresses and public IP addresses. Test data uses
`profiles.example.com` and placeholder credentials such as `test-token`.
