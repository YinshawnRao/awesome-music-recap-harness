# Cookie jar example

The short install path is in the root [README](../../README.md). This page
is the longer export / wrapper note.

`all_cookies.example.txt` is a **valid Netscape cookie file** filled with
obvious `PLACEHOLDER_NOT_A_SESSION_*` values. It is not a login. Comments
in the file label the YouTube/Google and Bilibili field families.

The full dual-platform yt-dlp flow **requires** a real user-exported jar
installed as repo-root `all_cookies.txt` (mode `0600`). That runtime file
is gitignored. Never commit it. Structure-only demo gates still run
without a jar.

## Install

```bash
cp examples/cookies/all_cookies.example.txt all_cookies.txt
chmod 0600 all_cookies.txt
```

Then either replace every `PLACEHOLDER_*` value in place, or overwrite the
file with a filtered candidate produced **outside** the repository:

```bash
# raw dump and candidate must live outside the repo
python3 tools/video/filter_cookie_jar.py /absolute/outside/raw.txt \
  --output /absolute/outside/candidate.txt
cp /absolute/outside/candidate.txt all_cookies.txt
chmod 0600 all_cookies.txt
python3 tools/video/check_yt_cookie.py
```

`check_yt_cookie.py` never prints cookie values. It **fails** the committed
example on purpose (`placeholder-value advisory`) until those tokens are
replaced. A missing `all_cookies.txt` is also a fail: downloads do not fall
back to an anonymous public path.

## Export from a browser

1. Sign into YouTube/Google and Bilibili in the same browser profile.
2. Use a Netscape `cookies.txt` exporter (for example “Get cookies.txt
   LOCALLY”). Save the file outside this repo and `chmod 0600` it.
3. Required names are listed in the example file comments and in
   `docs/mac-setup.md`.
4. Do not feed `--cookies-from-browser` to yt-dlp in this harness.

## Only allowed yt-dlp consumer

```bash
python3 tools/video/yt_dlp_readonly.py -- --skip-download --print id "<URL>"
```

The wrapper copies `all_cookies.txt` to a private `amrh-cookie-*` directory
**outside the repository** so yt-dlp cannot rewrite the canonical file.
Never run `yt-dlp --cookies all_cookies.txt` directly.
