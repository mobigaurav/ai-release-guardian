#!/bin/bash

# AI Release Guardian - Deployment & Demonstration Checklist
# Run this script to track progress through deployment steps

set -e

CHECKLIST_FILE="DEPLOYMENT_CHECKLIST.txt"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Initialize checklist
init_checklist() {
    cat > "$CHECKLIST_FILE" << 'EOF'
# AI Release Guardian - Deployment Checklist
# Check off items as you complete them

## PART 1: Prerequisites & Verification
- [ ] 1.1 Verify all tools installed (git, gh, aws, sam, python, docker)
- [ ] 1.2 Verify project structure and files
- [ ] 1.3 Verify all source files exist

## PART 2: GitHub Setup & Push
- [ ] 2.1 Create GitHub repository (or use existing)
- [ ] 2.2 Initialize local git repo and push code
- [ ] 2.3 Verify repository is live on GitHub

## PART 3: Configure GitHub Secrets
- [ ] 3.1 Set CLAUDE_API_KEY secret
- [ ] 3.2 Set JIRA_API_TOKEN secret (optional)
- [ ] 3.3 Verify all secrets are set

## PART 4: AWS Setup & SAM Deployment
- [ ] 4.1 Configure AWS credentials
- [ ] 4.2 Verify AWS credentials work
- [ ] 4.3 Create S3 bucket for SAM deployments
- [ ] 4.4 Verify SAM template exists
- [ ] 4.5 Build SAM project
- [ ] 4.6 Deploy SAM project to AWS
- [ ] 4.7 Verify Lambda function deployed
- [ ] 4.8 Get API Gateway endpoint
- [ ] 4.9 Configure Lambda environment variables

## PART 5: GitHub Webhook (Optional)
- [ ] 5.1 Create GitHub webhook for API endpoint
- [ ] 5.2 Verify webhook is working

## PART 6: Local Testing
- [ ] 6.1 Test Phase 2 orchestrator locally
- [ ] 6.2 Run local demo end-to-end

## PART 7: Create Test PR for Demo
- [ ] 7.1 Create feature branch and demo tests
- [ ] 7.2 Push to GitHub and create PR
- [ ] 7.3 Monitor GitHub Actions execution

## PART 8: Demonstration Scenarios
- [ ] 8.1 Verify GO decision (happy path)
- [ ] 8.2 Create and verify GATE decision (risky changes)
- [ ] 8.3 Create and verify NO-GO decision (failing tests)

## PART 9: Monitoring & Metrics
- [ ] 9.1 Collect workflow metrics
- [ ] 9.2 Track decision distribution
- [ ] 9.3 Measure QA velocity

## PART 10: Documentation
- [ ] 10.1 Document all API endpoints
- [ ] 10.2 Document decision thresholds used
- [ ] 10.3 Record team feedback
- [ ] 10.4 Plan next improvements

## FINAL VERIFICATION
- [ ] All workflows triggered successfully
- [ ] All decision paths tested (GO/GATE/NO-GO)
- [ ] Auto-merge working for GO decisions
- [ ] Metrics collected and documented
- [ ] Team trained on decision interpretation

EOF
    echo -e "${GREEN}✓ Checklist initialized${NC}"
}

# Display checklist
display_checklist() {
    echo ""
    echo -e "${BLUE}=== AI Release Guardian Deployment Checklist ===${NC}"
    echo ""
    cat "$CHECKLIST_FILE"
    echo ""
}

# Mark item as complete
mark_complete() {
    local item=$1
    if [ -z "$item" ]; then
        echo -e "${RED}✗ Usage: ./checklist.sh complete <item_number>${NC}"
        echo "  Example: ./checklist.sh complete 1.1"
        return
    fi
    
    # Replace [ ] with [x] for the item
    sed -i "" "s/- \[ \] $item/- [x] $item/g" "$CHECKLIST_FILE"
    echo -e "${GREEN}✓ Marked $item as complete${NC}"
    display_checklist
}

# Show progress
show_progress() {
    local total=$(grep -c "- \[" "$CHECKLIST_FILE")
    local completed=$(grep -c "- \[x\]" "$CHECKLIST_FILE")
    local percentage=$((completed * 100 / total))
    
    echo ""
    echo -e "${BLUE}=== Progress ===${NC}"
    echo "Completed: $completed / $total items ($percentage%)"
    echo ""
    
    # Progress bar
    local filled=$((percentage / 5))
    local empty=$((20 - filled))
    echo -n "["
    for ((i = 0; i < filled; i++)); do echo -n "="; done
    for ((i = 0; i < empty; i++)); do echo -n " "; done
    echo "] $percentage%"
    echo ""
}

# Show next steps
show_next() {
    echo ""
    echo -e "${BLUE}=== Recommended Next Steps ===${NC}"
    echo ""
    echo "1. Start with Part 1: Prerequisites & Verification"
    echo "   ./checklist.sh complete 1.1"
    echo "   ./checklist.sh complete 1.2"
    echo "   ./checklist.sh complete 1.3"
    echo ""
    echo "2. Then proceed to Part 2: GitHub Setup"
    echo "   Follow the sequence in DEPLOYMENT_AND_DEMO_PLAN.md"
    echo ""
    echo "3. For detailed instructions:"
    echo "   cat DEPLOYMENT_AND_DEMO_PLAN.md"
    echo ""
}

# Main script
if [ "$1" == "init" ]; then
    init_checklist
    display_checklist
    show_next
elif [ "$1" == "complete" ]; then
    mark_complete "$2"
    show_progress
elif [ "$1" == "progress" ]; then
    show_progress
elif [ "$1" == "show" ]; then
    display_checklist
    show_progress
elif [ "$1" == "help" ]; then
    echo "Usage: ./checklist.sh [command]"
    echo ""
    echo "Commands:"
    echo "  init       - Initialize checklist"
    echo "  show       - Display checklist and progress"
    echo "  progress   - Show only progress"
    echo "  complete   - Mark item as complete (requires item number)"
    echo "  help       - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./checklist.sh init           # Initialize checklist first"
    echo "  ./checklist.sh show           # Show full checklist"
    echo "  ./checklist.sh complete 1.1   # Mark item 1.1 as done"
    echo "  ./checklist.sh progress       # Show only progress bar"
else
    echo -e "${YELLOW}Welcome to AI Release Guardian Deployment!${NC}"
    echo ""
    echo "This script helps track your deployment progress."
    echo ""
    echo "To start:"
    echo "  ./checklist.sh init"
    echo ""
    echo "For help:"
    echo "  ./checklist.sh help"
    echo ""
fi
