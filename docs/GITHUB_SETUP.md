# Prepare your GitHub repository

Suggested repository name: `densha-de-go-2-ws-english`.

Create an empty repository under the account you choose. Extract the source ZIP, then from its root:

```sh
git init
git add .
git status --short
git commit -m "Prepare v0.4.17 English translation test prerelease"
git branch -M main
git remote add origin YOUR_REPOSITORY_GIT_URL
git push -u origin main
```

Replace `YOUR_REPOSITORY_GIT_URL` with your repository's actual URL. Review staged files before committing. The `.gitignore` excludes local ROMs, build outputs, emulator files and runtime dumps.

Create a release using tag `v0.4.17-test`, mark it as a pre-release, and use `docs/RELEASE_NOTES.md` as its description. Attach the cumulative BPS, incremental BPS/IPS if desired, and the release checksums. Include the separate release-assets ZIP for users who want the Python/BAT patch applicator.

No remote account, repository URL, repository publication, tag or release is created by this local preparation. Resolve the repository-wide licensing choice described in NOTICE.md before presenting all files under one license.
