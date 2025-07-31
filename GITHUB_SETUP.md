# GitHub Setup Instructions

## Initial Setup (One-time)

1. **Initialize Git** (if not already done):
```bash
cd /mnt/c/Users/basim/Downloads/ExcelProblem/streamlit_app
git init
```

2. **Configure Git without author info**:
```bash
git config --local user.name "PG Analytics"
git config --local user.email "analytics@pg.com"
```

3. **Add remote repository**:
```bash
git remote add origin https://github.com/BasimAlsaedi-UT/PGMiddleEastSupplyChainAnalyti.git
```

4. **Add all files**:
```bash
git add .
```

5. **Create initial commit**:
```bash
git commit -m "Initial commit: P&G Supply Chain Analytics Dashboard"
```

6. **Push to GitHub**:
```bash
git branch -M main
git push -u origin main
```

## Excluding Files

The `.gitignore` file is configured to exclude:
- Python cache files
- Virtual environment
- Data files (CSV, Excel)
- Extracted data folder
- Personal information
- IDE settings

## Important Notes

- Do NOT commit the Excel data files
- The `data/extracted/` folder will be created automatically
- Sensitive information should be added to `.streamlit/secrets.toml`

## Updating the Repository

After making changes:
```bash
git add .
git commit -m "Your commit message"
git push
```

## Cloning on Another Machine

```bash
git clone https://github.com/BasimAlsaedi-UT/PGMiddleEastSupplyChainAnalyti.git
cd PGMiddleEastSupplyChainAnalyti
pip install -r requirements.txt
```