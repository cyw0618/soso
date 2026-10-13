const { chromium } = require('/tmp/claude-0/-home-user-soso/d5f096f2-6485-53e9-9306-680db283255b/scratchpad/entry/node_modules/playwright-core');
const fs = require('fs');
// 사용: node pass3.js model.glb outPrefix '{"yaw":-50,"nod":8,"roll":-6,...}'
(async () => {
  const [model, outPrefix, optsJson] = process.argv.slice(2);
  const opts = JSON.parse(optsJson || '{}');
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--disable-background-networking'] });
  const p = await b.newPage({ viewport: { width: 600, height: 600 } });
  p.on('pageerror', e => console.log('[pageerror]', e.message.slice(0, 300)));
  await p.goto('http://localhost:8766/render.html');
  await p.waitForFunction(() => window.__ready, null, { timeout: 30000 });
  await p.evaluate((u) => window.loadModel(u), '/' + model);
  const res = await p.evaluate((o) => window.shot3(o), opts);
  for (const k of Object.keys(res)) fs.writeFileSync(`${outPrefix}_${k}.png`, Buffer.from(res[k].split(',')[1], 'base64'));
  console.log('ok', Object.keys(res).join(','));
  await b.close();
})();
