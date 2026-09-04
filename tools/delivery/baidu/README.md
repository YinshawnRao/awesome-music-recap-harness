# Optional Baidu Netdisk upload

This module is **optional**. The rest of the harness does not depend on it.

It is upload-only. It never ships tokens. Credentials come from environment
variables or a secret file **outside git**.

## Credentials

Preferred: `AMRH_BAIDU_CREDENTIALS_FILE` pointing at a `0600` JSON file:

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "app_key": "...",
  "secret_key": "...",
  "app_name": "amrh"
}
```

Or set `AMRH_BAIDU_ACCESS_TOKEN` (and optionally `AMRH_BAIDU_APP_NAME`).

Register an app on the [Baidu Netdisk Open Platform](https://pan.baidu.com/union/doc/)
and complete OAuth with scope `basic,netdisk`. Keep the token file off the repo.

## Public API pattern (xpan)

Small-file upload is the documented three-step flow:

1. `POST https://pan.baidu.com/rest/2.0/xpan/file?method=precreate`
2. `POST https://d.pcs.baidu.com/rest/2.0/pcs/superfile2` (4 MiB slices)
3. `POST https://pan.baidu.com/rest/2.0/xpan/file?method=create`

Remote paths should live under `/apps/<app_name>/`.

## Commands

```bash
python3 tools/delivery/baidu/upload.py --dry-run \
  --local renders/demo.mp4 --remote /apps/amrh/demo.mp4

# Live upload only after a real token is present
python3 tools/delivery/baidu/upload.py \
  --local renders/demo.mp4 --remote /apps/amrh/demo.mp4
```

`--dry-run` never talks to the network and never prints secrets.
