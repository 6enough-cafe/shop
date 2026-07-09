# Deploy thu muc web/ len GitHub Pages.
# 1) Sua BASE_URL trong config.js TRUOC.
# 2) Tao repo Public tren github.com (vd: juice-menu).
# 3) Sua $USER / $REPO ben duoi roi chay: powershell -File deploy-github-pages.ps1

$USER = "your-github-username"
$REPO = "juice-menu"

Set-Location $PSScriptRoot   # = thu muc web/

if (-not (Test-Path ".git")) { git init -b main }
git add index.html config.js make-qr.html .nojekyll
git commit -m "Deploy juice menu"

$remote = git remote
if (-not $remote) { git remote add origin "https://github.com/$USER/$REPO.git" }

git push -u origin main

Write-Host ""
Write-Host "Da push. Bay gio vao GitHub:" -ForegroundColor Green
Write-Host "  Settings -> Pages -> Source: Deploy from a branch -> main / (root) -> Save"
Write-Host ""
Write-Host "URL cong khai se la:" -ForegroundColor Green
Write-Host "  https://$USER.github.io/$REPO/"
Write-Host ""
Write-Host "DUNG QUEN: bat allow_cors tren ERPNext cho origin https://$USER.github.io" -ForegroundColor Yellow
