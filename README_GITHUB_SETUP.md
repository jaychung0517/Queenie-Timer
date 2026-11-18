# 星朵專注魔法屋 — GitHub Actions 100% 零點擊全自動更新設定指南

只要完成以下 3 個一次性設定，您的 `jaychung0517.github.io` 就會在**每天台灣時間 06:00 與 17:00** 全自動呼叫 Gemini API 生成 6 張全新熱門 IP 與鍾靈共舞圖並更新網頁，完全不需經過 Google Drive，也永遠不會再跳出授權視窗！

## 設定步驟（僅需 2 分鐘）

1. **上傳壓縮包內的所有檔案到您的 `jaychung0517.github.io` 儲存庫**：
   將解壓縮後的所有檔案與資料夾（包含 `index.html`、`daily_animations.json`、`animations/`、`scripts/generate_daily_animations.py` 與 `.github/workflows/daily_animation_update.yml`）上傳並覆蓋至您的 GitHub 儲存庫根目錄。

2. **設定您的 `GEMINI_API_KEY`**：
   - 前往您的 GitHub 儲存庫頁面 → **Settings** → 左側選單 **Secrets and variables** → **Actions**。
   - 點擊右上角綠色按鈕 **New repository secret**。
   - **Name** 填入：`GEMINI_API_KEY`
   - **Secret** 貼上您的 Gemini API 金鑰（可於 Google AI Studio 取得）→ 按下 **Add secret**。

3. **立即手動測試一次**：
   - 點選儲存庫上方的 **Actions** 分頁 → 左側點選 **每日早六點與晚五點全自動更新星朵動畫** → 點擊右側 **Run workflow** 按鈕。
   - 等待約 1 分鐘出現綠色勾勾後，重新整理 `https://jaychung0517.github.io/` 即可看到最新自動生成的 6 張動畫圖片！
