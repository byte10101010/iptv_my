@echo off
:: Move to your repo folder
cd /d "D:\git_volume\iptv_my"

:: Run your Python script to update the M3U8 file
python generate_playlist.py

:: Add the file to git
git add .

:: Commit the changes
git commit -m "Auto-update: %date% %time%"

:: Push to GitHub (This will now work without asking for a password)
git push origin main
