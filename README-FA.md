# کیهان | راه‌اندازی سایت و پنل مدیریت

صفحه اصلی: `index.html` — پنل مستقل: `/admin/` — بک‌اند: `worker/`.

## GitHub Pages
از Settings → Pages، گزینه Deploy from a branch، شاخه main و پوشه /(root) را انتخاب کنید.

## فعال‌سازی آمار واقعی
GitHub Pages بک‌اند ندارد؛ برای ذخیره آمار باید Cloudflare Worker و D1 راه‌اندازی شود:
1. یک D1 با نام kayhan-analytics بسازید.
2. شناسه دیتابیس را در worker/wrangler.toml جایگزین REPLACE_WITH_D1_DATABASE_ID کنید.
3. در پوشه worker دستور `wrangler d1 execute kayhan-analytics --remote --file=schema.sql` را اجرا کنید.
4. سه Secret ثبت کنید: ADMIN_PASSWORD، SESSION_SECRET (تصادفی و حداقل ۳۲ کاراکتر) و ALLOWED_ORIGIN با مقدار `https://chitaseee.github.io`.
5. برای هرکدام `wrangler secret put NAME` و سپس `wrangler deploy` را اجرا کنید.
6. آدرس Worker را در kayhan-config.js جایگزین مقدار نمونه کنید.

سایت: https://chitaseee.github.io/Cosmology/
پنل: https://chitaseee.github.io/Cosmology/admin/

رمز هرگز در HTML یا GitHub قرار نمی‌گیرد. مسیر پنل قابل حدس است اما آمار با رمز سمت سرور محافظت می‌شود. آمار از زمان فعال‌سازی شروع می‌شود و تعداد بارگذاری صفحات است، نه کاربران یکتا.
