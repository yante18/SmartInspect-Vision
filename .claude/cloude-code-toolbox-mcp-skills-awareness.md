# Cloude Code ToolBox — MCP & Skills awareness

_Generated: 2026-05-21T01:16:44.143Z_

## How to use this report

- **Saved copy:** This file is **`.claude/cloude-code-toolbox-mcp-skills-awareness.md`** — refreshed whenever the toolbox runs an MCP & Skills scan (including on workspace open when auto-scan is enabled). It is meant for **Claude Code workspace context** together with `CLAUDE.md` (which gets a shorter replaceable summary when auto-merge is on).
- **MCP:** Lists **configured** servers from Claude Code config (`~/.claude.json` for user scope, `.mcp.json` for project scope). Use `/mcp` in the Claude Code panel to connect servers for your session.
- **Skills:** **On-disk** folders with `SKILL.md`. Claude Code does not auto-load them; attach `SKILL.md` or paths in chat when useful.
- **Task routing:** When the user’s request matches a server’s purpose (e.g. Confluence → Confluence/Atlassian MCP), prefer that **server id** from the tables below.

---

## MCP — workspace

Workspace `mcp.json` _(folder: SmartInspect-Vision)_

- **c:\Users\Administrator\Desktop\服务器\SmartInspect-Vision\.mcp.json** — _File missing_

_No active workspace servers in mcp.json._

## MCP — user profile

- **C:\Users\Administrator\.claude.json** — _File exists — servers defined_

| Server id | Kind | Detail |
|-----------|------|--------|
| brain-mcp | stdio | cmd /c python D:\brain\platform_functions.py |

## Skills (local `SKILL.md` folders)

### Project-scoped

_None found (or no workspace open)._

### User-scoped

- **alpha-expression-verifier** — `C:\Users\Administrator\.claude\skills\alpha-expression-verifier`
  - Verify the syntax of an alpha expression irrespective of field existence. Use when checking if an alpha expression string is syntactically valid, has correct function arguments, and properly matched parentheses.

- **brain-alpha-judge** — `C:\Users\Administrator\.claude\skills\brain-alpha-judge`
  - >-

- **brain-calculate-alpha-selfcorrQuick** — `C:\Users\Administrator\.claude\skills\brain-calculate-alpha-selfcorrQuick`
  - >-

- **brain-data-feature-engineering** — `C:\Users\Administrator\.claude\skills\brain-data-feature-engineering`
  - >-

- **brain-datafield-exploration-general** — `C:\Users\Administrator\.claude\skills\brain-datafield-exploration-general`
  - >-

- **brain-dataset-exploration-general** — `C:\Users\Administrator\.claude\skills\brain-dataset-exploration-general`
  - >-

- **brain-deepExplore** — `C:\Users\Administrator\.claude\skills\brain-deepExplore`
  - >-

- **brain-enhance-template** — `C:\Users\Administrator\.claude\skills\brain-enhance-template`
  - >-

- **brain-explain-alphas** — `C:\Users\Administrator\.claude\skills\brain-explain-alphas`
  - >-

- **brain-feature-implementation** — `C:\Users\Administrator\.claude\skills\brain-feature-implementation`
  - Implements WorldQuant Brain features from an idea markdown file. Downloads dataset and generates alpha expressions defined in the idea.

- **brain-how-to-pass-AlphaTest** — `C:\Users\Administrator\.claude\skills\brain-how-to-pass-AlphaTest`
  - >-

- **brain-improve-alpha-performance** — `C:\Users\Administrator\.claude\skills\brain-improve-alpha-performance`
  - >-

- **brain-inspectRawTemplate-create-Setting** — `C:\Users\Administrator\.claude\skills\brain-inspectRawTemplate-create-Setting`
  - >-

- **brain-makeSomeGem** — `C:\Users\Administrator\.claude\skills\brain-makeSomeGem`
  - >-

- **brain-nextMove-analysis** — `C:\Users\Administrator\.claude\skills\brain-nextMove-analysis`
  - >-

- **brain-simAlphasinBatch-and-track** — `C:\Users\Administrator\.claude\skills\brain-simAlphasinBatch-and-track`
  - >-

- **planning-with-files** — `C:\Users\Administrator\.claude\skills\planning-with-files`
  - Implements Manus-style file-based planning for complex tasks. Creates task_plan.md, findings.md, and progress.md. Use when starting complex multi-step tasks, research projects, or any task requiring >5 tool calls.

- **pull_BRAINSkill** — `C:\Users\Administrator\.claude\skills\pull_BRAINSkill`
  - Pulls valid Claude Skills from a ZIP URL (preferred), Git repository, or local directory. Only folders containing a strictly named SKILL.md file are imported.

- **wq-brain-alpha-optimization-v1** — `C:\Users\Administrator\.claude\skills\wq-brain-alpha-optimization-v1`
  - >-

---

## Suggested next steps

- **MCP:** Use this extension’s hub **MCP** tab, or `claude mcp list` in the terminal. In Claude Code, use `/mcp` to connect servers for the session.
- **Edit config:** Open `~/.claude.json` (user MCP) or `<workspace>/.mcp.json` (project MCP) via the extension commands.
- **Refresh this report:** run **Intelligence — scan MCP & Skills awareness** again after changing MCP config or adding skills.

_Report from Cloude Code ToolBox extension._
