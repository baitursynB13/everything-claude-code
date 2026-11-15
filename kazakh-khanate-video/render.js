// art/NN.svg -> clips/NN.jpg (2160x3840)
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const art = path.join(__dirname, 'art');
  const out = path.join(__dirname, 'clips');
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 2 });
  for (const f of fs.readdirSync(art).filter(n => n.endsWith('.svg')).sort()) {
    const svg = fs.readFileSync(path.join(art, f), 'utf8');
    await page.setContent(`<body style="margin:0;background:#000">${svg}</body>`);
    await page.screenshot({ path: path.join(out, f.replace('.svg', '.jpg')), type: 'jpeg', quality: 90 });
  }
  await browser.close();
})();
