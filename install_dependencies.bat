@echo off
echo Installing required dependencies...
echo.

echo Installing core dependencies...
pip install streamlit pandas numpy plotly openpyxl xlrd scipy seaborn matplotlib

echo.
echo Installing optional dependencies (may fail on some systems)...
pip install statsmodels prophet scikit-learn

echo.
echo Installation complete!
echo.
echo If some packages failed to install, the app will still run with reduced functionality.
pause