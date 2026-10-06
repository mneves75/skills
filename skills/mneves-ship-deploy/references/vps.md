# VPS and container release checks

Checks for a release to a host you operate (Docker Compose, a self-hosted PaaS, or a system
service). The release contract is the same as on any platform: deploy a pushed commit, prove
it live, then tag. Each check ends on a condition you can observe.

## Before the deploy

**Confirm the project still runs on a host.** Deploy tooling outlives migrations: a
repository can keep a working `deploy.sh` for months after production moved to another
platform.
Done when the application repository's own deployment documentation and its latest release
record name the host path as the current one. When they name another platform, stop: this
file does not apply, and the host path is at most a rollback.

**Find the path production really uses.** A repository's `deploy.sh` can be older than the
way the service runs today, and running it can collide with the live container or start one
without its secrets.
Done when you have read, on the host, which image tag is running and which compose directory,
PaaS service or unit owns it, and that is the path your release command drives.

**Build off the host.** A small production host that builds its own image can time out and
leave orphan processes.
Done when the image is built elsewhere for the host's architecture and the release ships an
immutable tag or digest.

**A sync never deletes configuration.** `rsync --delete` aimed at the application directory
removes the environment file with everything else, which forces a key rotation.
Done when a `--dry-run` of the sync lists no deletion outside the release directory.

**Read the resolved Compose file.** Compose merges `ports` across files, so a base file and
an override can both bind one port.
Done when `docker compose config` shows one binding per published port.

**TLS terminates in one place.** An edge proxy and a host proxy that both terminate TLS
produce redirect loops or the wrong certificate.
Done when a request through the public name shows the expected certificate chain and no
redirect loop.

**Know what the backup covers.** A PaaS backup of its own database does not include an
application database that runs in your Compose stack.
Done when a restore point for the application's data exists and you can name where it is.

## Working on the host

- Tests run on a development machine or a staging host. A test suite that resets its
  repository does the same to a live checkout.
- Hand the user a command for the host as a full `ssh <host> '...'` line; a bare command runs
  on the machine where it is typed.
- Run long work inside a persistent terminal session on the host, so a dropped connection
  does not end it.
- A healthcheck addresses `127.0.0.1`. `localhost` can resolve to IPv6 while the service
  listens on IPv4 only.

## After the deploy

Done when `scripts/verify-live.sh` passes for the target: the service reports the released
commit (an image label or a `commit` field in its health response), the health body has its
expected fields, and the two controls behave. The rollback target is the previous image tag;
name it before the deploy, and remember that it reverts code and leaves data as it is.
