# claude_job_skills

Three Claude skills for a job search, with the three scripts they rely on and two templates you fill in yourself.

| Skill | What it does |
|---|---|
| `job-search` | Finds jobs: scans company career pages, AcademicTransfer, Indeed, LinkedIn, Euraxess and others, reads the full job description, scores it against your own criteria, and keeps an Excel tracker up to date |
| `job-apply` | Prepares one application: reads the vacancy and the team, gives you a fit analysis first, then tailors your CV and drafts a letter, then helps fill the web form and stops before submitting |
| `job-search-cn` | The same search for jobs in mainland China (campus and experienced-hire portals, Boss Zhipin, iGuopin and others) |

They come from a private setup that was used for several months of real job hunting. All personal content has been replaced with templates.

**The skills, the script messages and the tracker's column names are written in Chinese.** Application materials (CV, letters) are in English. If you do not read Chinese, this repository will be hard to use as it is. The full guide is in [README.zh-CN.md](README.zh-CN.md).

## Before you use it

- Written for someone based in the Netherlands. The sites, search parameters and remote-job rules assume that. Elsewhere the process still applies, but you need to swap in your local job sites.
- Written for machine learning, data and research jobs. The job-type vocabulary lives in the constants at the top of `tools/tracker.py`.
- Only the scripts have been tested in this anonymized version. The three skills have not been run end to end in this form. Issues are welcome.
- Job sites change. The skills record many site-specific endpoints and page structures as they were when written.
- The skills drive your own logged-in browser, read pages you can already see, pace their requests, and stop when a CAPTCHA appears. Whether automated access fits each site's terms of use is for you to judge.
- Nothing is submitted for you. Logging in, passwords, file uploads, consent boxes, CAPTCHAs and the final submit button are left to you.

## Requirements

- Claude with skills, a browser it can operate, and a shell in a folder on your computer. The author used the Claude desktop app with its built-in browser and the Claude in Chrome extension.
- Python 3 with `openpyxl`.
- LaTeX for the tailored CV. Overleaf is enough.

## Quick start

1. Create a `jobs` folder and copy in `tools/`, `profile/`, `templates/cv_master.tex` (as `cv_master.tex`) and, for the China search, `docs/cn_sites.md`. Add an empty `applications/` folder.
2. Fill in `profile/job_profile.md` (what you are looking for, how to score, search keywords, how your materials should read) and `profile/facts.md` (your facts, projects and numbers). Both ship with a fictional example.
3. Replace the content of `cv_master.tex` with your own, keeping the structure listed at the top of `tools/tailor_cv.py`.
4. Copy `tools/materials_config.example.json` to `tools/materials_config.json` and edit it.
5. Run `python3 tools/tracker.py init job_tracker.xlsx` inside the `jobs` folder.
6. Install the skills. In the Claude apps, zip each folder under `skills/` and upload it under Customize > Skills (see [Use skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude)). In Claude Code, copy the folders to `~/.claude/skills/` (see the [Claude Code docs](https://code.claude.com/docs/en/skills)).
7. Give Claude access to the `jobs` folder and ask it to start looking for jobs, or hand it a vacancy link and say you want to apply.

## Privacy

Your `profile/` files, `materials_config.json`, the tracker and `applications/` hold personal information. Keep them on your own machine and out of public repositories. The account table stores site, URL and username only, never passwords.

## License

MIT, see [LICENSE](LICENSE).
