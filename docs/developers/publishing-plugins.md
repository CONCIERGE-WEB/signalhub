# Publishing plugins

1. Pass `signalhub validate` and `contract-check`
2. Ship folder with `plugin.yaml`, code, README, LICENSE of the plugin
3. Document required `permissions` and ToS notes for any external source
4. Consumers install by copying into `SIGNALHUB_PLUGINS_DIR` or `./plugins`

Core upgrades should not require plugin code changes if they stay on RFC-0001 `contract_version` 1.x.
