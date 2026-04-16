#!/usr/bin/env python3
"""
adr_cli_poc.py

POC CLI for ADR compliance using CrewAI, without ChromaDB.

Usage:
    python adr_cli_poc.py --repo ./sample_repo --adrs-dir ./adrs --adr-files adr-001.md adr-002.md --out output/report.md --repo-summary-out output/repo_summary.md

If you do not provide --adr-files, the script will use all the .md files inside --adrs-dir.

Output files are written to the output folder located next to this script.
"""

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task
from crewai_tools import DirectoryReadTool, FileReadTool


# ---------------------------------------------------------------------
# Paths and environment
# ---------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = Path("output")  # relative to SCRIPT_DIR after chdir

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise EnvironmentError(
        "OPENAI_API_KEY not found. Add it to your .env file or environment."
    )
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

LLM_MODEL = "gpt-4.1-mini"


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def collect_adr_files(adrs_dir: Path, adr_files: list[str] | None) -> list[Path]:
    """
    If the user passes --adr-files, use only those files.
    Otherwise, use all .md files under the ADR directory.
    """
    if adr_files:
        resolved = []
        for item in adr_files:
            p = Path(item)
            if not p.is_absolute():
                p = adrs_dir / p
            resolved.append(p)
        return resolved

    return sorted(adrs_dir.glob("*.md"))


def load_adr_bundle(adr_paths: list[Path]) -> str:
    """
    Load ADR contents into one single text block.
    This keeps the POC simple and avoids ChromaDB.
    """
    chunks = []
    for path in adr_paths:
        if path.exists():
            content = path.read_text(encoding="utf-8", errors="ignore")
            chunks.append(
                f"\n{'=' * 80}\n"
                f"ADR FILE: {path.name}\n"
                f"PATH: {path}\n"
                f"{'=' * 80}\n"
                f"{content}\n"
            )
    return "\n".join(chunks)


def build_crew(repo_path: str, adr_bundle: str, repo_summary_out: str, compliance_out: str) -> Crew:
    """
    Build the CrewAI crew with 5 agents:
    1) Repo analyst
    2) Code finder
    3) ADR expert
    4) Researcher
    5) Reporting analyst
    """
    repo_dir_tool = DirectoryReadTool(directory=repo_path)
    file_tool = FileReadTool()

    # 1) Independent repository summary agent
    repo_analyst = Agent(
    role="Repository Analyst",
    goal=(
        "Produce a newcomer-friendly Markdown guide that explains what the repository is for, "
        "how it is structured, how the main components fit together, and which areas matter most "
        "for architecture and compliance review."
    ),
    backstory=(
        "You are a senior technical analyst and onboarding writer. "
        "You quickly understand unfamiliar repositories, identify the major modules and entry points, "
        "and explain the system architecture in a way that helps a new developer get oriented fast. "
        "You focus on the overall purpose of the codebase, the responsibilities of each major folder or module, "
        "the data and request flow, and the parts of the repo that are most important for security, compliance, "
        "or architecture analysis."
    ),
    tools=[repo_dir_tool, file_tool],
    verbose=True,
    llm=LLM_MODEL,
    allow_delegation=False,
    )
    code_finder = Agent(
        role="Code Finder Assistant",
        goal="Identify the source files, directories, and configuration artifacts most relevant to ADR and security compliance review.",
        backstory=(
            "You are a repository intelligence specialist with strong experience navigating complex, multi-service codebases. "
            "Your job is to rapidly locate the files, modules, and configuration surfaces most likely to contain architecture, "
            "security, privacy, and compliance-relevant behavior. You understand how applications are typically structured across "
            "frontend, backend, infrastructure, and build layers, and you know how to distinguish core application logic from "
            "supporting files that are unlikely to influence compliance posture. You are disciplined about prioritization: you "
            "focus first on entry points, authentication and authorization paths, data handling code, persistence layers, logging, "
            "API boundaries, client-side storage, security headers, and deployment/configuration files. You do not guess; you trace."
        ),
        tools=[repo_dir_tool, file_tool],
        verbose=True,
        llm=LLM_MODEL,
        allow_delegation=False
    )

    adrs_expert = Agent(
        role="ADR Expert",
        goal="Extract enforceable architecture, security, and design rules from ADRs and convert them into review-ready controls.",
        backstory=(
            "You are a senior software architect with deep experience reviewing architecture decision records, platform standards, "
            "and engineering governance documents. Your responsibility is to read ADRs carefully, identify binding decisions, "
            "exceptions, assumptions, and constraints, and translate them into explicit, testable rules that can be used by other "
            "agents during code review. You are precise about scope and language: you distinguish mandatory requirements from "
            "preferences, infer intent only when supported by the text, and preserve the original meaning of the architecture "
            "decision while making it operational. You are especially attentive to security controls, data handling requirements, "
            "service boundaries, trust assumptions, access patterns, and prohibited implementation practices."
        ),
        verbose=True,
        llm=LLM_MODEL,
        allow_delegation=False
    )

    researcher = Agent(
        role="Senior QA Engineer",
        goal="Inspect code and configuration for violations of the extracted rules, using evidence-based analysis to identify security and compliance anomalies.",
        backstory=(
            "You are a senior application security and quality reviewer who specializes in comparing implementation details against "
            "formal architecture and security requirements. You examine source code, configuration, and deployment artifacts with a "
            "defensive mindset, looking for concrete indicators of risk such as insecure data storage, unsafe DOM usage, weak input "
            "handling, auth bypass patterns, logging of sensitive data, unsafe deserialization, permissive security settings, and "
            "other violations of approved design constraints. You work from evidence, not intuition: every suspected issue must be "
            "grounded in the code and supported by contextual details. You are careful to identify both direct violations and "
            "likely weak points that warrant validation."
        ),
        tools=[file_tool],
        verbose=True,
        llm=LLM_MODEL,
        allow_delegation=False
    )

    finding_validator = Agent(
        role="Finding Validation and Triage Specialist",
        goal="Validate candidate findings, reduce false positives, assign severity, and classify each issue by risk category.",
        backstory=(
            "You are a security triage specialist responsible for confirming whether a suspected issue is real, actionable, and "
            "sufficiently supported by the evidence. You examine the surrounding code paths, usage context, and data flow to "
            "separate confirmed findings from harmless patterns, intentional exceptions, or incomplete signals. You are highly "
            "methodical: you verify preconditions, confirm impact, determine exploitability, and assess whether the issue is a "
            "true compliance violation, a conditional risk, or a false positive. You also normalize findings into consistent "
            "severity categories and risk labels so the final report is trustworthy, concise, and suitable for engineering and "
            "security stakeholders."
        ),
        tools=[file_tool],
        verbose=True,
        llm=LLM_MODEL,
        allow_delegation=False
    )

    suggestion_analyst = Agent(
        role="Sr Software Engineer",
        goal="Analyze validated findings and generate precise, context-aware remediation suggestions that align with security best practices and existing code patterns.",
        backstory=(
            "You are a senior software engineer and application security expert specializing in secure code remediation. "
            "Your responsibility is to take validated security and compliance findings and translate them into clear, "
            "actionable, and efficient code-level fixes. You carefully analyze the surrounding code context, including "
            "frameworks, libraries, coding style, and architectural patterns, to ensure that your recommendations are "
            "practical and consistent with the existing implementation. You avoid generic advice; instead, you provide "
            "specific guidance such as safer APIs, improved validation logic, secure storage mechanisms, proper "
            "authentication and authorization patterns, and defensive coding techniques. When appropriate, you propose "
            "refactored code snippets, configuration changes, or architectural adjustments. You also explain the reasoning "
            "behind each recommendation, including the risk being mitigated and any trade-offs involved, ensuring that "
            "developers can confidently apply the fix."
        ),
        tools=[file_tool],
        verbose=True,
        llm=LLM_MODEL,
        allow_delegation=False
    )

    reporting_analyst = Agent(
        role="Compliance Reporting Analyst",
        goal="Produce a structured Markdown report summarizing findings, evidence, severity, and recommended remediation.",
        backstory=(
            "You are a technical reporting specialist who transforms validated security and compliance findings into clear, "
            "well-structured documentation. You write for both engineers and decision-makers, balancing precision with readability. "
            "You know how to present evidence, summarize risk, explain impact, and recommend remediation in a way that is actionable "
            "without being vague or alarmist. You organize results by severity, category, and affected area, and you ensure the final "
            "report maintains a professional audit-ready tone. Your output is consistent, traceable, and suitable for review, "
            "tracking, and follow-up."
        ),
        verbose=True,
        llm=LLM_MODEL,
        allow_delegation=False
    )

    tasks = [
        Task(
            description=f"""
You are the Repository Analyst.

Analyze the repository at:
{repo_path}

Your job:
- determine what this repository is about
- describe its concrete purpose
- identify the main modules/files
- summarize any API, endpoints, or public functions if present
- mention the main dependencies or architecture patterns if obvious
- write the result as an independent report, without using ADR findings from later tasks

Focus on:
- what the repo does
- who or what it is for
- the most important files
- a brief summary of the API or interface

Write the output in clean Markdown.
""",
            agent=repo_analyst,
            expected_output="A standalone Markdown summary of the repository and its API.",
            memory=False,
            output_file=repo_summary_out,
        ),
        Task(
            description=f"""
You are the Code Finder Agent.

Scan the repository at:
{repo_path}

Your job:
- list the source files that are relevant to ADR compliance review
- ignore obvious non-source noise
- identify whether key files are present
- return a concise file inventory

Format your answer as:
- file path
- why it matters
- found / missing
""",
            agent=code_finder,
            expected_output="A concise mapping of each file => found/missing",
            memory=True,
        ),
        Task(
            description=f"""
You are the ADR Expert Agent.

Review the following ADRs and extract the architectural rules and constraints.

ADR CONTENT:
{adr_bundle}

Your job:
- extract architecture decisions
- turn them into reviewable compliance rules
- flag prohibited patterns
- flag required patterns

Return the rules as a clear checklist that another agent can apply to code review.
""",
            agent=adrs_expert,
            expected_output="Structured compliance rules extracted from ADR documentation",
            memory=True,
        ),
        Task(
            description="""
You are the Senior Quality Assurance Engineer.

Compare the code inventory from the Code Finder Agent against the rules from the ADR Expert Agent.

Your job:
- identify ADR violations
- include the file path
- include the specific rule violated
- include a short code snippet or evidence
- explain why it is a violation
- recommend the fix

If a file appears compliant, say so briefly.
If evidence is incomplete, say what is missing.
""",
            agent=researcher,
            expected_output="A structured list of code files => ADR violations => code snippet => recommended fix",
            memory=True,
        ),
        Task(
            description="""
You are the Report Analyst.

Write a final Markdown report based on the previous findings.

Your report must include:
- title
- executive summary
- compliance verdict
- section per file
- ADR involved
- evidence/snippet
- recommended fix
- final action list

Write it cleanly so it can be saved as a .md file.
""",
            agent=reporting_analyst,
            expected_output="A neat Markdown-based Non-Compliance Report covering each file, ADR, snippet, recommended fix.",
            memory=False,
            output_file=compliance_out,
        ),
    ]

    return Crew(
        agents=[repo_analyst, code_finder, adrs_expert, researcher,suggestion_analyst, reporting_analyst],
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )


def main():
    # Force relative paths to be resolved from the folder containing this script
    os.chdir(SCRIPT_DIR)

    parser = argparse.ArgumentParser(description="ADR compliance CLI POC with CrewAI")
    parser.add_argument("--repo", required=True, help="Path to the repository to analyze")
    parser.add_argument(
        "--adrs-dir",
        default="./adrs",
        help="Folder containing ADR markdown files",
    )
    parser.add_argument(
        "--adr-files",
        nargs="*",
        default=None,
        help="Optional explicit ADR files to use, relative to --adrs-dir or absolute paths",
    )
    parser.add_argument(
        "--out",
        default="output/report.md",
        help="Markdown compliance output path relative to this script",
    )
    parser.add_argument(
        "--repo-summary-out",
        default="output/repo_summary.md",
        help="Markdown repository summary output path relative to this script",
    )

    args = parser.parse_args()

    repo_path = Path(args.repo)
    adrs_dir = Path(args.adrs_dir)
    out_path = Path(args.out)
    repo_summary_out = Path(args.repo_summary_out)

    if not repo_path.exists():
        raise FileNotFoundError(f"Repo path not found: {repo_path}")

    if not adrs_dir.exists():
        raise FileNotFoundError(f"ADR directory not found: {adrs_dir}")

    adr_paths = collect_adr_files(adrs_dir, args.adr_files)
    if not adr_paths:
        raise FileNotFoundError(
            f"No ADR files found. Put .md files in {adrs_dir} or pass --adr-files"
        )

    missing = [str(p) for p in adr_paths if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing ADR files:\n" + "\n".join(missing))

    adr_bundle = load_adr_bundle(adr_paths)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    repo_summary_out.parent.mkdir(parents=True, exist_ok=True)

    crew = build_crew(str(repo_path), adr_bundle, str(repo_summary_out), str(out_path))

    result = crew.kickoff(
        inputs={
            "repo_path": str(repo_path),
            "adrs_dir": str(adrs_dir),
            "adr_files": [str(p) for p in adr_paths],
            "repo_summary_out": str(repo_summary_out),
            "compliance_out": str(out_path),
        }
    )

    report_text = str(result).strip()
    if not report_text.startswith("#"):
        report_text = "# ADR Compliance Report\n\n" + report_text

    # Safety net: if the output_file wasn't written for some reason, write it here too.
    if not out_path.exists():
        out_path.write_text(report_text, encoding="utf-8")

    print("\n=== ADR CLI POC finished ===")
    print("ADRs used:")
    for p in adr_paths:
        print(f" - {p}")
    print(f"\nRepository summary saved to: {repo_summary_out}")
    print(f"Compliance report saved to: {out_path}")
    print("\n=== Crew output ===\n")
    print(report_text)


if __name__ == "__main__":
    main()