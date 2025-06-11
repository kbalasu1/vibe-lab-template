# Hackathon Judging System

This directory contains automation tools for judging hackathon submissions efficiently and consistently.

## Quick Start

1. **Prepare submissions list**: Edit `submissions.txt` to include GitHub repository URLs (one per line)
2. **Run judging**: `python judge_submissions.py submissions.txt`
3. **Review results**: Check the generated `judging_results/scores.md` file

## Files Overview

- `judge_submissions.py` - Main judging automation script
- `submissions.txt` - List of GitHub repositories to judge  
- `README.md` - This documentation file

## Judging Process

The script automatically:

### 1. Repository Exploration (1 min per submission)
- Clones the GitHub repository
- Reads README and project structure
- Analyzes code organization and documentation

### 2. Setup & Execution (2 min per submission)  
- Attempts to follow setup instructions
- Tries common installation patterns (pip, npm, make, etc.)
- Attempts to run the application using common patterns

### 3. Scoring (1 min per submission)
- Evaluates against all three category rubrics
- Assigns scores 1-10 for each subcategory
- Calculates total scores (max 40 per category)

## Output

The script generates:
- `judging_results/scores.md` - Formatted tables with rankings
- `judging_results/scores.json` - Raw scoring data for analysis

### Sample Output Format

```markdown
## Category 1: Best Problem

| Rank | Project | GitHub Repo | Problem Definition | Significance & Impact | Effectiveness | Learning & Craftsmanship | **Total** | Notes |
|------|---------|-------------|-------------------|---------------------|---------------|------------------------|-----------|-------|
| 1 | awesome-project | https://github.com/user1/awesome-project | 9 | 8 | 9 | 8 | **34/40** | Setup: ✅, Run: ✅, Time: 3.2s |
```

## Manual Judging for AI Agents

If you need to judge submissions manually (for more detailed analysis), follow this process:

### Setup
1. Clone the submission repository
2. Navigate to the project directory
3. Read the README thoroughly

### Exploration (1 minute)
- Understand the project structure
- Review code quality and organization
- Check for documentation completeness

### Setup & Testing (2 minutes)
- Follow the quickstart instructions
- Install dependencies
- Attempt to run the application
- Test basic functionality

### Scoring (1 minute)
- Use the detailed rubrics in the main judging files:
  - `../judging1-best-problem.md`
  - `../judging2-most-complete.md` 
  - `../judging3-most-creative.md`
- Score each subcategory 1-10
- Calculate totals for each category

## Customization

To customize the judging script:

### Adding New Setup Patterns
Edit the `setup_commands` list in `try_setup()`:
```python
setup_commands = [
    ("pip install -r requirements.txt", ["requirements.txt"]),
    ("your-custom-command", ["custom-file.txt"]),
    # Add more patterns...
]
```

### Adding New Run Patterns
Edit the `run_commands` list in `try_run_application()`:
```python
run_commands = [
    "python main.py",
    "your-custom-run-command",
    # Add more patterns...
]
```

### Enhanced Scoring Logic
Replace the placeholder scoring in `judge_submission()` with more sophisticated analysis:
- Natural language processing of README content
- Code complexity analysis
- Test coverage detection
- User interface quality assessment

## Time Management

- **4-minute hard limit** per submission
- Script automatically tracks and reports timing
- Designed for efficiency while maintaining thoroughness
- Can process multiple submissions in batch

## Error Handling

The script gracefully handles:
- Failed repository clones
- Setup/installation failures  
- Runtime errors
- Missing documentation
- Timeout scenarios

Failed submissions receive minimum scores but are still included in results.

## Security Notes

⚠️ **Warning**: This script clones and executes code from third-party repositories. Run only in isolated environments:
- Use containers or VMs
- Run with limited permissions
- Monitor for malicious code
- Review repositories before judging when possible

## Troubleshooting

### Common Issues

**"Failed to clone repository"**
- Check internet connection
- Verify repository URLs are correct and public
- Ensure git is installed and configured

**"Setup timeout"**
- Some installations may take longer than 60 seconds
- Increase timeout in `try_setup()` if needed
- Check for internet connectivity issues

**"No scores generated"**
- Verify submissions.txt format is correct
- Check that repository URLs are accessible
- Look for error messages in console output

### Getting Help

For issues with the judging system:
1. Check console output for detailed error messages
2. Review the `judging_results/` directory for partial results
3. Test individual repository cloning manually
4. Verify all dependencies are installed (git, python3, pip) 