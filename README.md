# Generate Breedbase Templates Skill

This repository contains an [Agent Skill](https://agentskills.io) that can be used to convert raw breeder data into breedbase upload templates using an AI Agent, such as Claude Code.

> [!WARNING]
> As with any AI-generated output, the generated upload templates should be thoroughly checked for mistakes and errors before adding the data to the database.

## Installation

The exact installation will depend on the AI Agent you are using.  These instructions are for installing a [Claude Code Skill](https://code.claude.com/docs/en/skills):

```
mkdir -p ~/.claude/skills/generate-breedbase-templates
git clone https://github.com/TriticeaeToolbox/generate-breedbase-templates-skill.git ~/.claude/skills/generate-breedbase-templates
```

## Usage

1) Create a directory containing the raw breeder data you want to convert ( `~/data/` )
2) Change to the directory ( `cd ~/data/` )
3) Start claude code in that directory ( `claude` )
4) Use the `/generate-breedbase-templates` command to run the skill.

## Output

After running the `/generate-breedbase-templates` command and following any prompts that the AI agent may ask, you should have an `upload_templates/` directory that contains the accessions, trials, and observations templates to upload to breedbase.  The agent should also create a `bin/` directory that contains the python scripts used to generate the upload templates and a `process.sh` script that can be used to re-run the template generation from the source data (note: these scripts are specific to the source data that was used to generate them).
