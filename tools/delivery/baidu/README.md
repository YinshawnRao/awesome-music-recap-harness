# 可选：百度网盘上传

不属于第一次跑通。从根目录 [README](../../../README.md) 开始。
本模块是**可选**的。工作台其余部分不依赖它。只负责**上传**，不下载、不删文件、不改分享。

凭证永远在仓库外。git 里不能有 token、`.env`、或 `*credentials*.json`。

## 发现命令

```bash
python3 tools/cli.py baidu-upload --help
```

和直接跑 `python3 tools/delivery/baidu/upload.py --help` 一样。推荐走 `tools/cli.py`，根目录 README 也只写这一条。

## 凭证（仓库外）

优先：`AMRH_BAIDU_CREDENTIALS_FILE` 指向一份权限 **`0600`** 的 JSON，放在家目录或别的 git 外面的路径：

```bash
mkdir -p "$HOME/.config/amrh"
# 用编辑器写入 token，不要把这个文件放进仓库
chmod 0600 "$HOME/.config/amrh/baidu.json"
export AMRH_BAIDU_CREDENTIALS_FILE="$HOME/.config/amrh/baidu.json"
```

JSON 长这样（值换成你自己的，不要提交）：

```json
{
  "access_token": "替换成你的 access_token",
  "refresh_token": "可选",
  "app_key": "可选",
  "secret_key": "可选",
  "app_name": "amrh"
}
```

或者只设环境变量：`AMRH_BAIDU_ACCESS_TOKEN`（可选再加 `AMRH_BAIDU_APP_NAME`）。

在 [百度网盘开放平台](https://pan.baidu.com/union/doc/) 注册应用，OAuth 范围用 `basic,netdisk`。权限不是 `0600` 时，工具会拒绝读文件，并且**从不打印密钥**。

## 空跑（不联网、不要 token）

确认本地文件在、远端路径会落到 `/apps/<app_name>/` 下：

```bash
python3 tools/cli.py baidu-upload -- --dry-run \
  --local examples/top-ranking-demo/renders/top-ranking-demo.mp4 \
  --remote /apps/amrh/top-ranking-demo.mp4
```

`--dry-run` 不算实际上传。缺成片时把 `--local` 换成仓库里任意小文件（例如 `README.md`）也能看计划。CI 就是这样空跑的。

输出是一份计划 JSON：`steps = precreate → superfile2 → create`，外加一行
`BAIDU UPLOAD: DRY-RUN (no network, no secrets printed)`。

## 只上传（有了真实 token）

```bash
python3 tools/cli.py baidu-upload -- \
  --local examples/top-ranking-demo/renders/top-ranking-demo.mp4 \
  --remote /apps/amrh/top-ranking-demo.mp4
```

也可以 `--credentials-file "$HOME/.config/amrh/baidu.json"`，不必 export。远端路径如果不以 `/apps/` 开头，会自动补成 `/apps/<app_name>/...`。

成功：`BAIDU UPLOAD: PASS remote=/apps/amrh/...`。失败只打印错误类型，不打印 token。

## 公开 API 形态（xpan）

小文件上传是文档里的三步：

1. `POST https://pan.baidu.com/rest/2.0/xpan/file?method=precreate`
2. `POST https://d.pcs.baidu.com/rest/2.0/pcs/superfile2`（4 MiB 分片）
3. `POST https://pan.baidu.com/rest/2.0/xpan/file?method=create`

远端路径应在 `/apps/<app_name>/` 下。
