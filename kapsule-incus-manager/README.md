# Kapsule-Incus-Manager

Unified Incus container and VM management — Qt6/QML desktop UI, web UI, and
CLI with full feature parity across all three frontends.

See [ARCHITECTURE.md](ARCHITECTURE.md) for design decisions and component
boundaries.

## Components

| Component | Path | Description |
|---|---|---|
| Daemon | `daemon/` | Python system service — control plane for all frontends |
| QML UI | `ui-qml/` | Qt6/QML desktop application (primary UI) |
| Web UI | `ui-web/` | React/TypeScript browser interface |
| CLI | `cli/` | Command-line interface |
| Profiles | `profiles/` | Bundled Incus profile library (GPU, audio, display, ROCm) |

## Quick Start (development)

```sh
make install-dev   # install all Python and Node dependencies
make daemon        # install daemon in editable mode
make cli           # install CLI in editable mode
make web           # build web UI
make qml           # build QML app (requires Qt6 dev packages)
```

Run the daemon:

```sh
kim-daemon
```

The web UI is served at http://127.0.0.1:8765 once the daemon is running.

## Requirements

- Python >= 3.11
- Node.js >= 20 (web UI)
- Qt6 >= 6.6 with QtDeclarative and QtWebSockets (QML UI)
- Incus installed and accessible

## License

- Daemon, CLI, QML app: GPL-3.0-or-later
- `libkim-qt`: LGPL-2.1-or-later
- Web UI: Apache-2.0
- Profiles: MIT
