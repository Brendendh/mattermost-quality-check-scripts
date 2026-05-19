# Measure Hooks — Usage

## Purpose
- Small Go utility that parses the Mattermost server plugin `Hooks` interface and prints the total number of unique plugin hooks supported.

## Prerequisites
- Go installed (1.16+). Verify with:

```bash
go version
```
- A local clone of the Mattermost repository.

## Quick start (run from Mattermost repo root)

1. From the root of the Mattermost repository, change into the `server` directory (the script expects `./public/plugin/hooks.go` relative to CWD):

```bash
cd /path/to/mattermost
cd server
```

2. Run the script using its path where you have this repository (replace `/path/to/measure_hooks` with the real path on your machine):

```bash
go run /path/to/measure_hooks/measure_hooks.go
```

Notes:
- The script expects `./public/plugin/hooks.go` to exist under the current working directory (that's why you should run it from `server`).
- If you prefer not to change directories, pass an explicit path by copying the script into `server` (see below) or by editing the script to accept a command-line flag (see "Customize file path").

Alternative: copy the script into `server`

```bash
cp /path/to/measure_hooks/measure_hooks.go /path/to/mattermost/server/
cd /path/to/mattermost/server
go run measure_hooks.go
```

## Build a small binary (optional)

```bash
cd /path/to/mattermost/server
go build -o measure_hooks /path/to/measure_hooks/measure_hooks.go
./measure_hooks
```

## Expected output
```
======================================
Total Unique Plugin Hooks Supported: 42
======================================
```
The number will vary depending on the version of `hooks.go` you parsed.

## Troubleshooting
- "failed to parse file": check the path you passed and that the file exists.
- Go tool errors: ensure your `GOMOD`/module settings are not interfering; this script only uses standard library packages so running with `go run` should work without extra dependencies.
