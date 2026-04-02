"""KIM CLI — thin client over the KIM daemon REST API."""

import click
from .client import DaemonClient


@click.group()
@click.option("--daemon", default="http://127.0.0.1:8765", envvar="KIM_DAEMON",
              show_default=True, help="KIM daemon base URL.")
@click.pass_context
def cli(ctx: click.Context, daemon: str) -> None:
    """Kapsule-Incus-Manager command-line interface."""
    ctx.ensure_object(dict)
    ctx.obj["client"] = DaemonClient(daemon)


# ── Containers ────────────────────────────────────────────────────────────────

@cli.group()
def container() -> None:
    """Manage containers."""


@container.command("list")
@click.option("--project", default="", help="Project name.")
@click.option("--remote",  default="", help="Remote name.")
@click.pass_context
def container_list(ctx: click.Context, project: str, remote: str) -> None:
    """List containers."""
    client: DaemonClient = ctx.obj["client"]
    client.get("/api/v1/instances", params={"type": "container",
                                             "project": project,
                                             "remote": remote})


@container.command("create")
@click.argument("name")
@click.option("--image",   required=True, help="Image to use (e.g. images:ubuntu/24.04).")
@click.option("--profile", multiple=True, help="Profile(s) to apply.")
@click.option("--project", default="",   help="Project name.")
@click.pass_context
def container_create(ctx: click.Context, name: str, image: str,
                     profile: tuple[str, ...], project: str) -> None:
    """Create a container."""
    client: DaemonClient = ctx.obj["client"]
    client.post("/api/v1/instances", json={
        "name": name, "image": image,
        "profiles": list(profile), "type": "container",
        "project": project,
    })


@container.command("start")
@click.argument("name")
@click.option("--project", default="")
@click.pass_context
def container_start(ctx: click.Context, name: str, project: str) -> None:
    """Start a container."""
    ctx.obj["client"].put(f"/api/v1/instances/{name}/state",
                          json={"action": "start", "project": project})


@container.command("stop")
@click.argument("name")
@click.option("--force/--no-force", default=False)
@click.option("--project", default="")
@click.pass_context
def container_stop(ctx: click.Context, name: str, force: bool, project: str) -> None:
    """Stop a container."""
    ctx.obj["client"].put(f"/api/v1/instances/{name}/state",
                          json={"action": "stop", "force": force, "project": project})


@container.command("restart")
@click.argument("name")
@click.option("--force/--no-force", default=False)
@click.option("--project", default="")
@click.pass_context
def container_restart(ctx: click.Context, name: str, force: bool, project: str) -> None:
    """Restart a container."""
    ctx.obj["client"].put(f"/api/v1/instances/{name}/state",
                          json={"action": "restart", "force": force, "project": project})


@container.command("delete")
@click.argument("name")
@click.option("--force/--no-force", default=False)
@click.option("--project", default="")
@click.pass_context
def container_delete(ctx: click.Context, name: str, force: bool, project: str) -> None:
    """Delete a container."""
    ctx.obj["client"].delete(f"/api/v1/instances/{name}",
                             params={"force": force, "project": project})


# ── VMs ───────────────────────────────────────────────────────────────────────

@cli.group()
def vm() -> None:
    """Manage virtual machines."""


@vm.command("list")
@click.option("--project", default="")
@click.option("--remote",  default="")
@click.pass_context
def vm_list(ctx: click.Context, project: str, remote: str) -> None:
    """List virtual machines."""
    ctx.obj["client"].get("/api/v1/instances",
                          params={"type": "virtual-machine",
                                  "project": project, "remote": remote})


# ── Networks ──────────────────────────────────────────────────────────────────

@cli.group()
def network() -> None:
    """Manage networks."""


@network.command("list")
@click.option("--project", default="")
@click.pass_context
def network_list(ctx: click.Context, project: str) -> None:
    """List networks."""
    ctx.obj["client"].get("/api/v1/networks", params={"project": project})


# ── Storage ───────────────────────────────────────────────────────────────────

@cli.group()
def storage() -> None:
    """Manage storage pools."""


@storage.command("list")
@click.pass_context
def storage_list(ctx: click.Context) -> None:
    """List storage pools."""
    ctx.obj["client"].get("/api/v1/storage-pools")


# ── Images ────────────────────────────────────────────────────────────────────

@cli.group()
def image() -> None:
    """Manage images."""


@image.command("list")
@click.option("--remote", default="")
@click.pass_context
def image_list(ctx: click.Context, remote: str) -> None:
    """List images."""
    ctx.obj["client"].get("/api/v1/images", params={"remote": remote})


# ── Profiles ──────────────────────────────────────────────────────────────────

@cli.group()
def profile() -> None:
    """Manage profiles."""


@profile.command("list")
@click.option("--project", default="")
@click.pass_context
def profile_list(ctx: click.Context, project: str) -> None:
    """List profiles."""
    ctx.obj["client"].get("/api/v1/profiles", params={"project": project})


# ── Projects ──────────────────────────────────────────────────────────────────

@cli.group()
def project() -> None:
    """Manage projects."""


@project.command("list")
@click.pass_context
def project_list(ctx: click.Context) -> None:
    """List projects."""
    ctx.obj["client"].get("/api/v1/projects")


# ── Cluster ───────────────────────────────────────────────────────────────────

@cli.group()
def cluster() -> None:
    """Manage cluster members."""


@cluster.command("list")
@click.pass_context
def cluster_list(ctx: click.Context) -> None:
    """List cluster members."""
    ctx.obj["client"].get("/api/v1/cluster/members")


# ── Remotes ───────────────────────────────────────────────────────────────────

@cli.group()
def remote() -> None:
    """Manage remote servers."""


@remote.command("list")
@click.pass_context
def remote_list(ctx: click.Context) -> None:
    """List configured remotes."""
    ctx.obj["client"].get("/api/v1/remotes")


# ── Operations ────────────────────────────────────────────────────────────────

@cli.group()
def operation() -> None:
    """Manage operations."""


@operation.command("list")
@click.pass_context
def operation_list(ctx: click.Context) -> None:
    """List running and recent operations."""
    ctx.obj["client"].get("/api/v1/operations")


@operation.command("cancel")
@click.argument("id")
@click.pass_context
def operation_cancel(ctx: click.Context, id: str) -> None:
    """Cancel a running operation."""
    ctx.obj["client"].delete(f"/api/v1/operations/{id}")


# ── Events ────────────────────────────────────────────────────────────────────

@cli.command("events")
@click.option("--type", "event_type", default="", help="Filter by event type.")
@click.pass_context
def events(ctx: click.Context, event_type: str) -> None:
    """Stream live events from the daemon."""
    ctx.obj["client"].stream_events(event_type)
