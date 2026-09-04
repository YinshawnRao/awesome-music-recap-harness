# 可选：百度网盘上传

不属于第一次跑通。从根目录 [README](../../../README.md) 开始。
本模块是**可选**的。工作台其余部分不依赖它。

只负责上传。从不附带 token。凭证来自环境变量，或 **git 外面**的密钥文件。

## 凭证

优先：`AMRH_BAIDU_CREDENTIALS_FILE` 指向一份权限 `0600` 的 JSON：

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "app_key": "...",
  "secret_key": "...",
  "app_name": "amrh"
}
```

或者设 `AMRH_BAIDU_ACCESS_TOKEN`（可选再加 `AMRH_BAIDU_APP_NAME`）。

在 [百度网盘开放平台](https://pan.baidu.com/union/doc/) 注册应用，OAuth 范围用 `basic,netdisk`。token 文件放在仓库外。

## 公开 API 形态（xpan）

小文件上传是文档里的三步：

1. `POST https://pan.baidu.com/rest/2.0/xpan/file?method=precreate`
2. `POST https://d.pcs.baidu.com/rest/2.0/pcs/superfile2`（4 MiB 分片）
3. `POST https://pan.baidu.com/rest/2.0/xpan/file?method=create`

远端路径应在 `/apps/<app_name>/` 下。

## 命令

```bash
python3 tools/delivery/baidu/upload.py --dry-run \
  --local renders/demo.mp4 --remote /apps/amrh/demo.mp4

# 有了真实 token 再做实际上传
python3 tools/delivery/baidu/upload.py \
  --local renders/demo.mp4 --remote /apps/amrh/demo.mp4
```

`--dry-run` 不联网，也不打印密钥。
