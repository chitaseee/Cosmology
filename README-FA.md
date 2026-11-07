# کیهان | راه‌اندازی سایت و پنل مدیریت

- سایت اصلی: https://chitaseee.github.io/Cosmology/
- صفحه فارسی: https://chitaseee.github.io/Cosmology/fa/
- صفحه انگلیسی: https://chitaseee.github.io/Cosmology/en/
- پنل مدیریت: https://chitaseee.github.io/Cosmology/admin/
- کد بک‌اند: پوشه `worker/`

## انتشار سایت

در GitHub از مسیر **Settings → Pages**، منبع انتشار را روی GitHub Actions قرار دهید. فایل `.github/workflows/pages.yml` با هر Push به شاخه `main` سایت را منتشر می‌کند.

## راه‌اندازی آمار و پنل مدیریت

GitHub Pages بک‌اند اجرا نمی‌کند. آمار و ورود مدیر به Cloudflare Worker و پایگاه داده D1 نیاز دارد.

### ۱. ساخت D1

یک پایگاه داده D1 با نام دقیق `kayhan-analytics` بسازید و شناسهٔ آن را در `worker/wrangler.toml` در مقدار `database_id` قرار دهید. شناسهٔ فعلی فایل باید با شناسهٔ واقعی دیتابیس حساب Cloudflare شما یکی باشد.

### ۲. تنظیم Secretهای خود Worker در Cloudflare

این سه مقدار باید در محیط Worker ثبت شوند؛ صرفاً قرار دادن آن‌ها در GitHub Actions کافی نیست:

- `ADMIN_PASSWORD`: رمز قوی و اختصاصی پنل مدیریت.
- `SESSION_SECRET`: یک مقدار تصادفی و محرمانه با حداقل ۳۲ کاراکتر.
- `ALLOWED_ORIGIN`: دقیقاً `https://chitaseee.github.io`؛ بدون مسیر `/Cosmology` و بدون اسلش انتهایی.

از پوشهٔ `worker` این دستورها را اجرا کنید و برای هرکدام مقدار محرمانهٔ مربوط را وارد کنید:

```bash
npx wrangler@4 secret put ADMIN_PASSWORD
npx wrangler@4 secret put SESSION_SECRET
npx wrangler@4 secret put ALLOWED_ORIGIN
```

### ۳. دسترسی GitHub Actions به Cloudflare

در مخزن GitHub از مسیر **Settings → Secrets and variables → Actions** دو Repository Secret زیر را بسازید:

- `CLOUDFLARE_API_TOKEN`: توکن API با دسترسی لازم برای انتشار Worker و اعمال Migrationهای D1.
- `CLOUDFLARE_ACCOUNT_ID`: شناسهٔ حساب Cloudflare.

این دو مقدار با Secretهای مرحلهٔ قبل فرق دارند. Workflow انتشار Worker برای اجرا به هر دو نیاز دارد.

### ۴. انتشار Worker و Migrationها

فایل `.github/workflows/deploy-worker.yml` به‌صورت دستی اجرا می‌شود. در GitHub به **Actions → Deploy Cosmology Worker → Run workflow** بروید. این Workflow ابتدا Migrationهای D1 را اعمال و سپس Worker را Deploy می‌کند.

### ۵. تنظیم نشانی Worker در سایت

پس از Deploy، نشانی واقعی Worker را در `kayhan-config.js` قرار دهید:

```js
window.KAYHAN_API_BASE = "https://YOUR-WORKER.YOUR-SUBDOMAIN.workers.dev";
```

نشانی نمونه را با آدرس واقعی Worker جایگزین کنید. سپس تغییر را در شاخهٔ `main` ثبت کنید تا GitHub Pages دوباره منتشر شود.

## نکات امنیتی و آمار

- رمز مدیر نباید در HTML، فایل JavaScript عمومی یا مخزن GitHub قرار بگیرد.
- مسیر پنل عمومی و قابل حدس است؛ حفاظت ورود باید توسط Worker انجام شود.
- آمار از زمان فعال‌شدن سرویس ثبت می‌شود و بازدیدهای گذشته قابل بازیابی نیستند.
- شمارنده تعداد بارگذاری صفحه را ثبت می‌کند، نه تعداد کاربران یکتا.
- اگر ورود پنل خطای اتصال داد، ابتدا نشانی Worker، سپس مقدار `ALLOWED_ORIGIN` و وجود Secretهای Worker و D1 را بررسی کنید.
