@echo off
echo Installing packages for Python 3.13...

echo Installing core packages...
pip install streamlit pandas numpy plotly openpyxl xlrd

echo Installing additional packages...
pip install scikit-learn altair folium scipy seaborn matplotlib

echo Installing Streamlit extensions...
pip install streamlit-aggrid streamlit-folium

echo Installing statsmodels (may take time)...
pip install statsmodels

echo Installing prophet (optional - may fail)...
pip install prophet || echo Prophet installation failed - continuing without it

echo.
echo Installation complete!
echo.
pause