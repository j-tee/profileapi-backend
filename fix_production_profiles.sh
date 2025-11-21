#!/bin/bash

# Production Profile Fix Script
# This script fixes the missing profile issue for existing users

echo "=================================="
echo "Profile Auto-Creation Deployment"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo -e "${RED}Error: manage.py not found. Are you in the project directory?${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Checking current profiles...${NC}"
python manage.py shell -c "from profiles.models import Profile; from accounts.models import User; print(f'Users: {User.objects.count()}, Profiles: {Profile.objects.count()}')"
echo ""

echo -e "${YELLOW}Step 2: Running profile sync (dry-run first)...${NC}"
python manage.py sync_user_profiles --dry-run
echo ""

read -p "Do you want to create the missing profiles? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo -e "${YELLOW}Step 3: Creating missing profiles...${NC}"
    python manage.py sync_user_profiles
    echo ""
    
    echo -e "${GREEN}✅ Profile sync complete!${NC}"
    echo ""
    
    echo -e "${YELLOW}Step 4: Verifying profiles...${NC}"
    python manage.py shell -c "from profiles.models import Profile; from accounts.models import User; print(f'Users: {User.objects.count()}, Profiles: {Profile.objects.count()}')"
    echo ""
    
    echo -e "${GREEN}=================================="
    echo "Deployment Complete!"
    echo "==================================${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Update your frontend to use the new login response format"
    echo "2. Implement profile completion flow"
    echo "3. Test login with existing users"
    echo ""
    echo "See AUTO_PROFILE_CREATION_GUIDE.md for frontend implementation details"
else
    echo -e "${YELLOW}Skipped profile creation${NC}"
    exit 0
fi
