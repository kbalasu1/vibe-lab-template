#!/usr/bin/env python3
"""
AI-Based Hackathon Judging Script

This script automates the judging process for hackathon submissions.
It clones repositories, follows setup instructions, runs applications,
and scores them according to the defined rubrics.

Usage:
    python judge_submissions.py submissions.txt

Where submissions.txt contains one GitHub repo URL per line.
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict

@dataclass
class SubmissionScore:
    project_name: str
    github_repo: str
    category1_scores: Dict[str, int]  # subcategory -> score
    category2_scores: Dict[str, int]
    category3_scores: Dict[str, int]
    category1_total: int
    category2_total: int
    category3_total: int
    notes: str = ""

class HackathonJudge:
    def __init__(self, output_dir: str = "judging_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.scores: List[SubmissionScore] = []
        
    def clone_repository(self, repo_url: str, target_dir: str) -> bool:
        """Clone a GitHub repository"""
        try:
            subprocess.run(
                ["git", "clone", repo_url, target_dir], 
                check=True, 
                capture_output=True, 
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to clone {repo_url}: {e}")
            return False
    
    def read_readme(self, project_dir: str) -> str:
        """Read and return README content"""
        readme_files = ["README.md", "README.txt", "readme.md", "readme.txt"]
        for readme in readme_files:
            readme_path = Path(project_dir) / readme
            if readme_path.exists():
                try:
                    return readme_path.read_text(encoding='utf-8')
                except UnicodeDecodeError:
                    return readme_path.read_text(encoding='latin-1')
        return ""
    
    def try_setup(self, project_dir: str) -> Tuple[bool, str]:
        """Attempt to follow setup instructions"""
        original_dir = os.getcwd()
        setup_log = []
        
        try:
            os.chdir(project_dir)
            
            # Common setup patterns
            setup_commands = [
                # Python
                ("pip install -r requirements.txt", ["requirements.txt"]),
                ("pip install -e .", ["setup.py", "pyproject.toml"]),
                # Node.js
                ("npm install", ["package.json"]),
                ("yarn install", ["yarn.lock"]),
                # Other
                ("make install", ["Makefile"]),
                ("cargo build", ["Cargo.toml"]),
            ]
            
            for command, indicators in setup_commands:
                if any(Path(indicator).exists() for indicator in indicators):
                    try:
                        result = subprocess.run(
                            command.split(), 
                            capture_output=True, 
                            text=True, 
                            timeout=60
                        )
                        setup_log.append(f"Ran: {command}")
                        setup_log.append(f"Exit code: {result.returncode}")
                        if result.returncode != 0:
                            setup_log.append(f"Error: {result.stderr}")
                            return False, "\n".join(setup_log)
                    except subprocess.TimeoutExpired:
                        setup_log.append(f"Timeout running: {command}")
                        return False, "\n".join(setup_log)
                    except Exception as e:
                        setup_log.append(f"Failed to run {command}: {e}")
                        return False, "\n".join(setup_log)
            
            return True, "\n".join(setup_log)
            
        finally:
            os.chdir(original_dir)
    
    def try_run_application(self, project_dir: str) -> Tuple[bool, str]:
        """Attempt to run the application"""
        original_dir = os.getcwd()
        run_log = []
        
        try:
            os.chdir(project_dir)
            
            # Common run patterns
            run_commands = [
                "python main.py",
                "python app.py", 
                "python -m src",
                "npm start",
                "npm run dev",
                "make run",
                "cargo run",
                "./run.sh"
            ]
            
            for command in run_commands:
                try:
                    # Try to run for 10 seconds to see if it starts
                    result = subprocess.run(
                        command.split(),
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    run_log.append(f"Tried: {command}")
                    run_log.append(f"Exit code: {result.returncode}")
                    if result.stdout:
                        run_log.append(f"Output: {result.stdout[:200]}...")
                    if result.returncode == 0:
                        return True, "\n".join(run_log)
                except subprocess.TimeoutExpired:
                    run_log.append(f"Started successfully: {command}")
                    return True, "\n".join(run_log)
                except Exception:
                    continue
            
            return False, "\n".join(run_log)
            
        finally:
            os.chdir(original_dir)
    
    def judge_submission(self, repo_url: str) -> SubmissionScore:
        """Judge a single submission with 4-minute time limit"""
        start_time = time.time()
        project_name = repo_url.split('/')[-1].replace('.git', '')
        temp_dir = self.output_dir / f"temp_{project_name}"
        
        print(f"\n🔍 Judging: {project_name}")
        print(f"Repository: {repo_url}")
        
        # Initialize scores
        score = SubmissionScore(
            project_name=project_name,
            github_repo=repo_url,
            category1_scores={"problem_definition": 1, "significance_impact": 1, "effectiveness": 1, "learning_craftsmanship": 1},
            category2_scores={"scope_coverage": 1, "robustness_testing": 1, "documentation_reproducibility": 1, "code_quality": 1},
            category3_scores={"originality_innovation": 1, "vibe_polish": 1, "effective_execution": 1, "storytelling_presentation": 1},
            category1_total=4,
            category2_total=4,
            category3_total=4
        )
        
        # 1. Repository Exploration (1 min)
        if not self.clone_repository(repo_url, str(temp_dir)):
            score.notes = "Failed to clone repository"
            return score
        
        readme_content = self.read_readme(str(temp_dir))
        
        # 2. Setup & Execution (2 min)
        setup_success, setup_log = self.try_setup(str(temp_dir))
        run_success, run_log = self.try_run_application(str(temp_dir))
        
        # 3. Quick Analysis and Scoring (1 min)
        # This is where you would implement the actual scoring logic
        # For now, we'll use placeholder scoring based on basic criteria
        
        # Check time limit
        elapsed = time.time() - start_time
        if elapsed > 240:  # 4 minutes
            print(f"⏰ Time limit exceeded ({elapsed:.1f}s)")
        
        # Basic scoring logic (to be enhanced)
        if readme_content:
            if "problem" in readme_content.lower():
                score.category1_scores["problem_definition"] = 6
            if setup_success:
                score.category2_scores["documentation_reproducibility"] = 7
            if run_success:
                score.category2_scores["robustness_testing"] = 7
                score.category3_scores["effective_execution"] = 7
        
        # Calculate totals
        score.category1_total = sum(score.category1_scores.values())
        score.category2_total = sum(score.category2_scores.values())
        score.category3_total = sum(score.category3_scores.values())
        
        score.notes = f"Setup: {'✅' if setup_success else '❌'}, Run: {'✅' if run_success else '❌'}, Time: {elapsed:.1f}s"
        
        # Cleanup
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except:
            pass
        
        print(f"✅ Scored: Category1={score.category1_total}/40, Category2={score.category2_total}/40, Category3={score.category3_total}/40")
        return score
    
    def save_scores(self):
        """Save scores to markdown tables"""
        scores_file = self.output_dir / "scores.md"
        
        # Sort by scores for each category
        cat1_sorted = sorted(self.scores, key=lambda x: x.category1_total, reverse=True)
        cat2_sorted = sorted(self.scores, key=lambda x: x.category2_total, reverse=True)
        cat3_sorted = sorted(self.scores, key=lambda x: x.category3_total, reverse=True)
        
        with open(scores_file, 'w') as f:
            f.write("# Hackathon Judging Results\n\n")
            
            # Category 1: Best Problem
            f.write("## Category 1: Best Problem\n\n")
            f.write("| Rank | Project | GitHub Repo | Problem Definition | Significance & Impact | Effectiveness | Learning & Craftsmanship | **Total** | Notes |\n")
            f.write("|------|---------|-------------|-------------------|---------------------|---------------|------------------------|-----------|-------|\n")
            
            for i, score in enumerate(cat1_sorted, 1):
                f.write(f"| {i} | {score.project_name} | {score.github_repo} | "
                       f"{score.category1_scores['problem_definition']} | "
                       f"{score.category1_scores['significance_impact']} | "
                       f"{score.category1_scores['effectiveness']} | "
                       f"{score.category1_scores['learning_craftsmanship']} | "
                       f"**{score.category1_total}/40** | {score.notes} |\n")
            
            # Category 2: Most Complete
            f.write("\n## Category 2: Most Complete\n\n")
            f.write("| Rank | Project | GitHub Repo | Scope Coverage | Robustness & Testing | Documentation & Reproducibility | Code Quality | **Total** | Notes |\n")
            f.write("|------|---------|-------------|----------------|-------------------|---------------------------|--------------|-----------|-------|\n")
            
            for i, score in enumerate(cat2_sorted, 1):
                f.write(f"| {i} | {score.project_name} | {score.github_repo} | "
                       f"{score.category2_scores['scope_coverage']} | "
                       f"{score.category2_scores['robustness_testing']} | "
                       f"{score.category2_scores['documentation_reproducibility']} | "
                       f"{score.category2_scores['code_quality']} | "
                       f"**{score.category2_total}/40** | {score.notes} |\n")
            
            # Category 3: Most Creative
            f.write("\n## Category 3: Most Creative\n\n")
            f.write("| Rank | Project | GitHub Repo | Originality & Innovation | Vibe & Polish | Effective Execution | Storytelling & Presentation | **Total** | Notes |\n")
            f.write("|------|---------|-------------|-------------------------|---------------|-------------------|---------------------------|-----------|-------|\n")
            
            for i, score in enumerate(cat3_sorted, 1):
                f.write(f"| {i} | {score.project_name} | {score.github_repo} | "
                       f"{score.category3_scores['originality_innovation']} | "
                       f"{score.category3_scores['vibe_polish']} | "
                       f"{score.category3_scores['effective_execution']} | "
                       f"{score.category3_scores['storytelling_presentation']} | "
                       f"**{score.category3_total}/40** | {score.notes} |\n")
        
        print(f"\n📊 Scores saved to: {scores_file}")
        
        # Also save raw JSON data
        json_file = self.output_dir / "scores.json"
        with open(json_file, 'w') as f:
            json.dump([asdict(score) for score in self.scores], f, indent=2)

def main():
    if len(sys.argv) != 2:
        print("Usage: python judge_submissions.py submissions.txt")
        print("Where submissions.txt contains one GitHub repo URL per line")
        sys.exit(1)
    
    submissions_file = sys.argv[1]
    if not Path(submissions_file).exists():
        print(f"Error: {submissions_file} not found")
        sys.exit(1)
    
    # Read submissions
    with open(submissions_file, 'r') as f:
        repo_urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    print(f"🏆 Starting judging process for {len(repo_urls)} submissions")
    
    judge = HackathonJudge()
    
    for i, repo_url in enumerate(repo_urls, 1):
        print(f"\n{'='*60}")
        print(f"📋 Judging submission {i}/{len(repo_urls)}")
        
        try:
            score = judge.judge_submission(repo_url)
            judge.scores.append(score)
        except Exception as e:
            print(f"❌ Error judging {repo_url}: {e}")
            # Add a failed score
            project_name = repo_url.split('/')[-1].replace('.git', '')
            failed_score = SubmissionScore(
                project_name=project_name,
                github_repo=repo_url,
                category1_scores={"problem_definition": 1, "significance_impact": 1, "effectiveness": 1, "learning_craftsmanship": 1},
                category2_scores={"scope_coverage": 1, "robustness_testing": 1, "documentation_reproducibility": 1, "code_quality": 1},
                category3_scores={"originality_innovation": 1, "vibe_polish": 1, "effective_execution": 1, "storytelling_presentation": 1},
                category1_total=4,
                category2_total=4,
                category3_total=4,
                notes=f"Failed to judge: {str(e)}"
            )
            judge.scores.append(failed_score)
    
    judge.save_scores()
    print(f"\n🎉 Judging complete! Results saved to judging_results/")

if __name__ == "__main__":
    main() 