#!/bin/bash
#
# Setup script for GitHub branch protection rules
# This script configures main branch protection according to issue #11
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Repository owner - update this if needed
REPO_OWNER="PagePalApp"
REPO_NAME="epub-cfi-toolkit"

echo -e "${YELLOW}Setting up branch protection for ${REPO_OWNER}/${REPO_NAME}${NC}"

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed.${NC}"
    echo "Please install it from https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}Error: Not authenticated with GitHub CLI.${NC}"
    echo "Please run: gh auth login"
    exit 1
fi

# Check if user has admin access to the repository
echo "Checking repository permissions..."
REPO_PERMS=$(gh api repos/${REPO_OWNER}/${REPO_NAME} --jq '.permissions.admin')
if [ "$REPO_PERMS" != "true" ]; then
    echo -e "${RED}Error: You need admin access to this repository to set up branch protection.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Repository permissions verified${NC}"

# Create the branch protection rule
echo "Creating branch protection rule for main branch..."

# First, let's check if a rule already exists
EXISTING_RULES=$(gh api repos/${REPO_OWNER}/${REPO_NAME}/rulesets --jq '.[].name' 2>/dev/null | grep -c "Main Branch Protection" || echo "0")

if [ "$EXISTING_RULES" -gt 0 ]; then
    echo -e "${YELLOW}Warning: Branch protection rules already exist. This will create an additional ruleset.${NC}"
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted by user."
        exit 0
    fi
fi

# Create the ruleset JSON configuration
RULESET_CONFIG=$(cat <<EOF
{
  "name": "Main Branch Protection",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["refs/heads/main"],
      "exclude": []
    }
  },
  "rules": [
    {
      "type": "deletion"
    },
    {
      "type": "non_fast_forward"
    },
    {
      "type": "pull_request",
      "parameters": {
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_approving_review_count": 1,
        "required_review_thread_resolution": false
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "required_status_checks": [
          {
            "context": "build",
            "integration_id": null
          },
          {
            "context": "test (3.8)",
            "integration_id": null
          },
          {
            "context": "test (3.9)",
            "integration_id": null
          },
          {
            "context": "test (3.10)",
            "integration_id": null
          },
          {
            "context": "test (3.11)",
            "integration_id": null
          },
          {
            "context": "test (3.12)",
            "integration_id": null
          }
        ]
      }
    }
  ],
  "bypass_actors": [
    {
      "actor_id": $(gh api user --jq '.id'),
      "actor_type": "User",
      "bypass_mode": "always"
    }
  ]
}
EOF
)

# Apply the ruleset
echo "Applying branch protection ruleset..."
RULESET_RESPONSE=$(gh api repos/${REPO_OWNER}/${REPO_NAME}/rulesets \
  --method POST \
  --input <(echo "$RULESET_CONFIG") \
  2>&1)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Branch protection ruleset created successfully!${NC}"
    echo
    echo "Branch protection is now active with the following rules:"
    echo "• Pull requests required before merging"
    echo "• 1 approval required (except for repository owner)"
    echo "• All CI status checks must pass"
    echo "• Branch deletions prevented"
    echo "• Force pushes prevented"
    echo "• Dismiss stale reviews when new commits are pushed"
    echo
    echo -e "${YELLOW}Note: The repository owner ($(gh api user --jq '.login')) can bypass these rules.${NC}"
else
    echo -e "${RED}Error creating branch protection rule:${NC}"
    echo "$RULESET_RESPONSE"
    exit 1
fi

echo -e "${GREEN}Branch protection setup complete!${NC}"