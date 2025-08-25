# Branch Protection Setup

This document explains how to set up GitHub branch protection rules for the main branch to ensure code quality and review processes.

## Overview

Branch protection rules prevent direct pushes to the main branch and enforce quality gates through required status checks and pull request reviews.

## Requirements

The branch protection setup addresses the requirements from issue #11:

- **Required Status Checks**: All CI checks must pass before merging
- **Pull Request Reviews**: One approval required for most contributors
- **Owner Bypass**: Repository owner can merge without approval
- **Protection Against**: Force pushes and branch deletion

## Quick Setup

### Automated Setup

Use the provided script to automatically configure branch protection:

```bash
# Make the script executable
chmod +x setup-branch-protection.sh

# Run the setup script
./setup-branch-protection.sh
```

### Prerequisites

1. **GitHub CLI**: Install from [cli.github.com](https://cli.github.com/)
2. **Authentication**: Run `gh auth login`
3. **Admin Access**: You need admin permissions on the repository

## Manual Setup

If you prefer to set up branch protection manually through GitHub's web interface:

### Step 1: Access Repository Settings

1. Go to your repository on GitHub
2. Click **Settings** tab
3. Select **Rules** > **Rulesets** from the left sidebar

### Step 2: Create New Ruleset

1. Click **New ruleset** > **New branch ruleset**
2. Set **Ruleset name**: "Main Branch Protection"
3. Set **Enforcement status**: Active

### Step 3: Configure Target Branches

1. Under **Target branches**, click **Add target**
2. Select **Include by pattern**
3. Enter pattern: `main`

### Step 4: Add Rules

Add the following rules:

#### Restrict Deletions
- Check **Restrict deletions**

#### Restrict Force Pushes
- Check **Restrict pushes that create files**

#### Require Pull Request
- Check **Require a pull request before merging**
- Set **Required approvals**: 1
- Check **Dismiss stale pull request approvals when new commits are pushed**

#### Require Status Checks
- Check **Require status checks to pass before merging**
- Check **Require branches to be up to date before merging**
- Add the following status checks:
  - `build`
  - `test (3.8)`
  - `test (3.9)`  
  - `test (3.10)`
  - `test (3.11)`
  - `test (3.12)`

### Step 5: Configure Bypass Permissions

1. Under **Bypass list**, click **Add bypass**
2. Select **Users** and add the repository owner
3. Set **Bypass mode**: Always

### Step 6: Save Ruleset

Click **Create** to activate the branch protection rules.

## Ruleset Configuration Details

The branch protection ruleset includes:

### Protection Rules

| Rule | Purpose | Configuration |
|------|---------|---------------|
| **Deletion Protection** | Prevents branch deletion | Always active |
| **Force Push Protection** | Prevents rewriting history | Always active |
| **Pull Request Required** | Enforces code review | 1 approval required |
| **Status Checks** | Ensures CI passes | All test jobs + build must pass |

### Required Status Checks

The following CI checks must pass before merging:

- **test (3.8)**: Python 3.8 compatibility tests
- **test (3.9)**: Python 3.9 compatibility tests  
- **test (3.10)**: Python 3.10 compatibility tests
- **test (3.11)**: Python 3.11 compatibility tests
- **test (3.12)**: Python 3.12 compatibility tests
- **build**: Package building and validation

### Bypass Configuration

- **Repository Owner**: Can bypass all rules and merge without approval
- **All Other Contributors**: Must follow standard review process

## Verification

After setup, verify the protection is working:

1. **Check Rules**: Go to Settings > Rules and confirm the ruleset is active
2. **Test Protection**: Try pushing directly to main (should be blocked)
3. **Test PR Flow**: Create a test PR and confirm status checks are required

## Troubleshooting

### Common Issues

#### "You need admin access" Error
**Problem**: Script fails with permission error  
**Solution**: Ensure you have admin access to the repository

#### Status Checks Not Found
**Problem**: Required status checks don't appear in the ruleset  
**Solution**: Status checks only appear after they've run at least once. Create a test PR first.

#### Script Authentication Error
**Problem**: `gh auth status` fails  
**Solution**: Run `gh auth login` and follow the authentication flow

### GitHub CLI Issues

If you encounter GitHub CLI issues:

```bash
# Check CLI version
gh --version

# Re-authenticate
gh auth logout
gh auth login

# Verify repository access
gh repo view PagePalApp/epub-cfi-toolkit
```

## Updating Rules

To modify the branch protection rules:

1. **Via Script**: Update the `RULESET_CONFIG` in `setup-branch-protection.sh`
2. **Via Web**: Go to Settings > Rules > Edit the existing ruleset
3. **Via API**: Use `gh api` commands to update the ruleset

## Related Documentation

- [GitHub Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets)
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution workflow
- [CODE_STYLE.md](../CODE_STYLE.md) - Code style requirements

## Security Considerations

The branch protection setup ensures:

- **Code Quality**: All changes must pass CI checks
- **Peer Review**: Code changes require approval (except owner)
- **History Preservation**: Force pushes and deletions prevented
- **Controlled Access**: Only authorized users can bypass rules

This configuration balances security with maintainer flexibility while ensuring all contributions meet quality standards.