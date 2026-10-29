# GitHub deployment setup for LinuxonUSB.com (multilingual)

Everything below is done in the GitHub website. No terminal needed. GitHub changes its menus from time to time, so if a label differs slightly, look for the closest match.

## 0. How it works, and the one architecture decision

GitHub Pages allows **one custom domain per repository**. So a language on its own subdomain (`es.linuxonusb.com`) needs **its own Pages repository**. Two ways to do this, both built in. You choose per language in `i18n/languages.json` (`"mode"`).

| | `subdomain` (what you asked for) | `subdirectory` (simpler) |
|---|---|---|
| Address | `es.linuxonusb.com` | `linuxonusb.com/es/` |
| Extra repositories | 1 per language | none |
| Extra DNS records | 1 per language | none |
| Extra secrets | 1 token, shared | none |
| Failure points | more (token, each repo, each DNS record) | fewer |
| SEO | each subdomain is treated as its own site | ranking strength stays on one domain |

**My recommendation:** start with `subdirectory` if you only want it to work with the least setup, or start with `subdomain` for 1 or 2 languages and add more later. The default shipped is `subdomain`. To switch a language, change `"mode"` to `"subdirectory"` in `i18n/languages.json`. Nothing else changes.

### What the automation does

```
You edit the project  ->  GitHub Actions builds English  ->  builds 16 language editions
   ->  validates everything  ->  (only if valid)  ->  deploys English + each language
```

- **Design/template/CSS/catalog change:** every language is rebuilt from the new English site, so all of them update.
- **Product description or page text change:** the page's translation is marked **stale**. The language site automatically serves that page as an English `noindex` page (so Google never sees an out-of-date translation presented as current). A GitHub Issue titled "Translations need review" lists the stale pages.
- **A page with no translation yet:** shown in English with translated menus/footer, `noindex`, canonical pointing to the English page. It is not in the language sitemap and has no hreflang tags. Once a matching translation file exists it becomes a real translated page automatically.
- **Failed build/validation:** nothing is deployed and the live sites stay as they were. A GitHub Issue "Website deployment failed" is opened with a link to the error.

## 1. What you must do once (manual) vs. what is automated

| Manual, one time | Automated afterwards |
|---|---|
| Upload this project to your main repository | Building English and all languages |
| Turn on GitHub Pages for the main repo (Source: GitHub Actions) | Hreflang, canonical URLs, sitemaps, robots.txt, CNAME files |
| Create one repo per subdomain language you want live | Validation and blocking bad deploys |
| Create one access token and save it as a secret | Deploying main site and each language |
| Save each language repo name as a Variable | Skipping languages with no changes |
| Add DNS records at your domain provider | Opening Issues for failures and stale translations |
| Turn on Pages + HTTPS in each language repo | |

## 2. Upload the project to the main repository

1. On github.com click **+** (top right) > **New repository**. Choose a name you like (this is your **main repository**), set **Public** (Actions minutes and Pages are free for public repos; see section 12), click **Create repository**.
2. Unzip `linuxonusb-site-v6.zip` on your computer. Open the folder `linuxonusb-site-ready`.
3. In the new repository click **uploading an existing file**. Drag in **the contents** of `linuxonusb-site-ready` (all files and folders, not the outer folder itself). Commit to `main`.
4. **Hidden folder warning:** the folder `.github` starts with a dot and some file managers hide it (Mac: press Cmd+Shift+. in Finder; Windows: View > Show > Hidden items). If it does not upload, create the two workflow files by hand: **Add file > Create new file**, type `.github/workflows/deploy.yml` as the name (typing `/` makes folders), paste the file's contents, commit. Repeat for `translation-export.yml`. Also create `.gitignore` the same way if it is missing.

The zip contains no `dist/` folder on purpose: GitHub builds it fresh every time.

## 3. Enable GitHub Pages for the main site

1. Main repo > **Settings** > **Pages**.
2. Under **Build and deployment** set **Source** to **GitHub Actions**.
3. Under **Custom domain** enter `linuxonusb.com` and **Save**. (The project already ships a `CNAME` file for this.)
4. Later, tick **Enforce HTTPS** once it becomes available (section 9).

## 4. Allow Actions to run

Main repo > **Settings** > **Actions** > **General**:
- **Actions permissions:** *Allow all actions and reusable workflows* (the workflows only use official `actions/*` actions).
- **Workflow permissions:** *Read repository contents permission* is enough. Each job requests extra rights itself (Pages deploy, creating Issues) and nothing more.

Also check **Settings > Environments > github-pages**. If **Deployment branches** is restricted, make sure `main` is allowed.

## 5. Create the language repositories (subdomain mode only)

Skip this whole section if you use `subdirectory` mode.

For each language you want live (start with one to test):

1. **+ > New repository.** Any name you like, for example `my-site-es`. **Public.** Tick **Add a README** (this creates the `main` branch). Create it.
2. Write down the name as `YOURNAME/REPONAME`.

Languages are: es, fr, de, pt, it, nl, pl, tr, ru, ar, hi, id, vi, zh-CN, ja, ko. Their subdomains are `es`, `fr`, ... and `zh` for zh-CN (see `i18n/languages.json`).

## 6. Create the deployment token and save it as a secret

The main repo needs permission to write into the language repos. Use one **fine-grained personal access token** limited to just those repos.

1. github.com > your profile picture > **Settings** > **Developer settings** > **Personal access tokens** > **Fine-grained tokens** > **Generate new token**.
2. Name: `linuxonusb-language-deploy`. Expiration: the longest offered (it will expire; see section 13).
3. **Repository access:** *Only select repositories* and pick **only the language repositories**. Not the main repo.
4. **Permissions > Repository permissions:** **Contents: Read and write**. (Metadata: Read is added automatically.) Nothing else.
5. **Generate token** and copy it now (it is shown once).
6. Main repo > **Settings** > **Secrets and variables** > **Actions** > **Secrets** tab > **New repository secret**. Name exactly `LANG_DEPLOY_TOKEN`, paste the token, **Add secret**.

Never put the token in a file in the project. The workflow reads it only from this secret and hides it in logs.

If you later add language repos, edit the token (Developer settings) to include them.

## 7. Tell the automation which repo belongs to which language

Main repo > **Settings** > **Secrets and variables** > **Actions** > **Variables** tab > **New repository variable**. One per live language:

| Variable name | Value (example format) |
|---|---|
| `TARGET_REPO_ES` | `YOURNAME/REPONAME` |
| `TARGET_REPO_FR` | `YOURNAME/REPONAME` |
| `TARGET_REPO_DE`, `_PT`, `_IT`, `_NL`, `_PL`, `_TR`, `_RU`, `_AR`, `_HI`, `_ID`, `_VI`, `_JA`, `_KO` | same format |
| `TARGET_REPO_ZH_CN` | `YOURNAME/REPONAME` (note the underscore) |

A language with **no** variable is simply not deployed, and the English site will not link to it (it keeps the Google Translate option for that language). Optional variable `TARGET_BRANCH` (default `main`) if your language repos publish from another branch.

## 8. Enable Pages in each language repository

For every language repo: **Settings > Pages** > **Source: Deploy from a branch** > Branch **main**, folder **/ (root)** > **Save**. Then, under **Custom domain**, enter the subdomain (for example `es.linuxonusb.com`) and **Save**. The deployed site includes the matching `CNAME` file, so the setting stays in place after each deploy.

## 9. DNS records and HTTPS

At your domain provider's DNS page:

| Type | Name/Host | Value |
|---|---|---|
| CNAME | `es` | `YOURNAME.github.io` |
| CNAME | `fr` | `YOURNAME.github.io` |
| ...one per live language | `zh` for zh-CN | `YOURNAME.github.io` |

Use your own GitHub username (not an organisation's, unless the repos live in one). Do not add a path. Your apex domain `linuxonusb.com` keeps whatever records it already has for GitHub Pages (GitHub's four A records, `185.199.108.153`, `.109.153`, `.110.153`, `.111.153`; check GitHub's current list at docs.github.com, "Managing a custom domain for your GitHub Pages site").

DNS can take minutes to hours. In each repo's **Settings > Pages** wait for "DNS check successful", then tick **Enforce HTTPS** (GitHub issues the certificate itself; this can take up to about 24 hours). Do the same for the main repo.

## 10. Test the first deployment

1. Main repo > **Actions** tab > **Build, validate and deploy** > **Run workflow** (branch `main`).
2. Open the run. You should see: Build and validate (green), Deploy main site, then one **Deploy xx** job per live language.
3. Read the run's **Summary** page: it shows a translation status table.
4. Visit `https://linuxonusb.com/` and `https://es.linuxonusb.com/` (once DNS and HTTPS are ready). On a language site you should see translated menus and footer; pages not yet translated show English content and are marked noindex.
5. Make a tiny change (for example a price in `catalog/products.json` via the web editor) and commit. A new run should start by itself.

## 11. Adding real translations (no terminal)

Page bodies are not machine-translated automatically (that would need a paid API). The structure supports translations you supply:

1. Main repo > **Actions** > **Export translation stubs** > **Run workflow**. Enter a language (for example `es`), leave pages as `stale,missing` and a limit (for example 20).
2. Download the artifact `translation-stubs-es`. Each JSON file has English text with instructions. Translate the values (you, a translator, or an AI assistant), keeping keys, HTML entities and `source_hash` unchanged.
3. In the main repo **Add file > Upload files**, upload them into `i18n/pages/es/` (create the folders by typing the path). Commit.
4. The next run publishes those pages as real translated pages with hreflang and sitemap entries. When the English page changes later, the hash no longer matches and the page is flagged stale automatically.

The menu/footer translations in `i18n/ui/*.json` were drafted by Claude and **have not been reviewed by native speakers**. Please have them checked before promoting the languages.

## 12. Free-tier notes

- **Public repositories:** GitHub Actions minutes and Pages are free. **Private repositories on a free plan** get a monthly Actions allowance (2,000 minutes at the time of writing) and Pages from a private repo is not available on Free plans. Keep repos public, or check current limits at docs.github.com/billing.
- Each run takes a few minutes. README-only edits do not trigger it. Pushes while a deploy is running queue rather than pile up. Languages with no changes are not re-pushed.
- GitHub Pages limits (check current values): site up to 1 GB, soft 100 GB/month bandwidth, 10 builds/hour for branch-based Pages. Each language edition here is about 17 MB.
- No paid services or APIs are used.

## 13. Maintenance

- **Token expiry:** the fine-grained token expires. When language deploys start failing with "Cannot read" or authentication errors, create a new token (section 6) and replace the secret `LANG_DEPLOY_TOKEN`.
- Action versions are pinned to major versions of official GitHub actions.

## 14. Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| Whole run fails at **Validate** | Nothing was deployed (this is intended). Open the step; each line starts with `::error::` and names the file. Fix and commit. |
| `Secret LANG_DEPLOY_TOKEN is not set` | Section 6, step 6: name must be exactly `LANG_DEPLOY_TOKEN`, under *Secrets*, not *Variables*. |
| `must look like owner/repository` | Variable value is wrong (section 7). |
| `Cannot read OWNER/REPO` | Repo name typo, or the token does not include that repo, or the token expired. |
| `Permission denied` / 403 on push | Token lacks **Contents: Read and write**, or does not include that repo. |
| Main deploy fails: "Pages not enabled" / environment error | Section 3 Source must be *GitHub Actions*; check *Environments > github-pages* branch rules. |
| Language site shows 404 | Language repo Pages not enabled (section 8), or branch name differs from `TARGET_BRANCH`. |
| `es.linuxonusb.com` certificate error / HTTPS box greyed | DNS not propagated yet or wrong CNAME value; wait, re-save the custom domain. |
| Language site changes but custom domain disappears | The `CNAME` file is deployed automatically; check the deployed repo root contains `CNAME`. |
| Translation page not appearing in language sitemap | Its `source_hash` does not match (stale). See the Issue "Translations need review" and re-export. |
| Nothing runs after a commit | Only changes to source folders trigger runs (not README/docs). Use **Run workflow** manually. |
| `Issue` was not created | Settings > Actions > General > Workflow permissions must not block issue creation; repo Issues must be enabled (Settings > General > Features). |

## 15. What has and has not been tested

Tested locally by Claude (Linux, Python 3): the English build, all 16 language builds, the validator (including deliberate breakage), stale/fresh/missing translation handling, subdirectory mode, and the language-repository push script against a local bare git repository (first deploy, no-change skip, update, unreachable repo, bad repo name).

**Not tested on GitHub** (not possible from here): the workflow files were parsed as valid YAML but have never run on GitHub; token authentication, Pages deployment, DNS, HTTPS and Issue creation are untested. Expect to read one run log and possibly fix a small thing the first time.
