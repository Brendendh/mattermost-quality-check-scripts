# Spectral & IBM OpenAPI Validator — Setup and Usage

## Purpose
- Install `ibm-openapi-validator` (dev dependency) in your repo `api` folder and provide Spectral usage with the IBM ruleset. This file also explains how to re-enable (uncomment) rule overrides and how to handle renamed rule IDs after upgrading.

## Prerequisites
- Node.js and a package manager (`npm`, `yarn`, or `pnpm`).

## Install dev dependencies (run inside your repo `api` folder)

1. Change to your repo `api` folder:

```bash
cd api
```

2. Initialize `package.json` if needed:

```bash
npm init -y
```

3. Install the IBM validator and Spectral as dev dependencies:

```bash
# npm
npm install --save-dev ibm-openapi-validator

# yarn
yarn add -D ibm-openapi-validator

# pnpm
pnpm add -D ibm-openapi-validator
```

4. Create full YAML
```bash
make build
```

## Add useful npm scripts

- Edit `package.json` and add scripts for convenience (adjust spec path/glob as needed):

```json
"scripts": {
  "lint:openapi": "npx ibm-openapi-validator ./v4/html/static/*.yaml",
}
```

## Run the linter

```bash
npm run lint:openapi
```

Replace `./specs/*.yaml` with the path or glob to your OpenAPI spec(s).

## Uncommenting and keeping rule overrides

- Your repository already has a file at [api_standard_compliance/.spectral.yaml](.spectral.yaml) that extends the IBM ruleset and contains an example overrides block commented out.
- To re-enable those overrides, remove the leading `#` characters and ensure proper YAML indentation. Example uncommented block:

```yaml
extends: '@ibm-cloud/openapi-ruleset'

rules:
  operation-tags: off
  ibm-property-casing-convention: off
  ibm-accept-and-return-models: off
  operation-operationId: error
  operation-description: warn
  ibm-no-array-responses: off
  ibm-parameter-description: error
  ibm-parameter-casing-convention: info
  no-$ref-siblings: off
  ibm-enum-casing-convention: off
  ibm-path-segment-casing-convention: info
```

## Troubleshooting
- CLI not found: use `npx` (e.g., `npx ibm-openapi-validator`) so the local dev dependency is used.
- YAML errors after uncommenting: verify spacing and indentation; use `yamllint` or an editor with YAML support.

Notes
- Keep the commented overrides in `.spectral.yaml` as documentation and uncomment selectively when you intentionally want to override the defaults.
- Consult the `@ibm-cloud/openapi-ruleset` changelog for a mapping of old → new IDs when upgrading.

## Copy .spectral.yaml into Mattermost `api` folder

```bash
cp -v api_standard_compliance/.spectral.yaml /path/to/mattermost_repo_root/api/.spectral.yaml
```

If a file already exists at the destination, make a backup first:

```bash
cp /path/to/mattermost_repo_root/api/.spectral.yaml /path/to/mattermost_repo_root/api/.spectral.yaml.bak || true
cp -v api_standard_compliance/.spectral.yaml /path/to/mattermost_repo_root/api/.spectral.yaml
```

Verify the copy:

```bash
ls -l /path/to/mattermost_repo_root/api/.spectral.yaml
cat /path/to/mattermost_repo_root/api/.spectral.yaml
```