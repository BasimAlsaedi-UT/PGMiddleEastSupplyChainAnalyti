# GitHub Push Commands

## Complete Setup and Push

Run these commands in your terminal from the `streamlit_app` directory:

```bash
# 1. Initialize Git repository
git init

# 2. Configure git to use generic user info
git config --local user.name "PG Analytics"
git config --local user.email "analytics@pg.com"

# 3. Add the remote repository
git remote add origin https://github.com/BasimAlsaedi-UT/PGMiddleEastSupplyChainAnalyti.git

# 4. Add all files to staging
git add .

# 5. Check what will be committed (verify no Excel files)
git status

# 6. Create initial commit
git commit -m "Initial commit: P&G Supply Chain Analytics Dashboard"

# 7. Set main branch
git branch -M main

# 8. Push to GitHub
git push -u origin main
```

## If you get authentication errors:

### Option 1: Personal Access Token (Recommended)
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token with `repo` permissions
3. Use the token as password when prompted

### Option 2: GitHub CLI
```bash
# Install GitHub CLI
# Windows: winget install --id GitHub.cli
# Mac: brew install gh
# Linux: see https://github.com/cli/cli/blob/trunk/docs/install_linux.md

# Authenticate
gh auth login

# Push using gh
gh repo clone BasimAlsaedi-UT/PGMiddleEastSupplyChainAnalyti
```

## Verify Files Before Pushing

Check that sensitive files are excluded:
```bash
# List files that will be committed
git ls-files

# Ensure these are NOT listed:
# - Any .xlsx files
# - data/extracted/ folder
# - .streamlit/secrets.toml
# - Any personal information
```

## After Successful Push

1. Go to https://github.com/BasimAlsaedi-UT/PGMiddleEastSupplyChainAnalyti
2. Verify all files are uploaded correctly
3. Check that no Excel files or sensitive data were uploaded
4. Update repository settings:
   - Add description
   - Add topics: streamlit, analytics, supply-chain, dashboard
   - Set visibility as needed

## For Future Updates

```bash
# Check status
git status

# Add changes
git add .

# Commit with descriptive message
git commit -m "Add: feature description"

# Push changes
git push
```

## Common Issues

### "src refspec main does not match any"
```bash
# Make sure you have at least one commit
git add .
git commit -m "Initial commit"
```

### "fatal: remote origin already exists"
```bash
# Remove and re-add
git remote remove origin
git remote add origin https://github.com/BasimAlsaedi-UT/PGMiddleEastSupplyChainAnalyti.git
```

### Large file errors
```bash
# Check file sizes
find . -type f -size +100M

# Add large files to .gitignore
echo "large_file.xlsx" >> .gitignore
```