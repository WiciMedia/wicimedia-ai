// Renders the final MP4 from the page itself: every frame through the page's own exporter
// (WebCodecs + Mediabunny, 45 Mbps H.264), and the mixed narration + sound effects through
// its OfflineAudioContext. ffmpeg then encodes H.264 CRF 18 + AAC 192k.
//
// Usage: node tools/render-mp4.js <page.html> <narration.mp3> <mediabunny.min.mjs> <out.mp4>
// Get the Mediabunny bundle with: npm pack mediabunny@1.65.2 && tar xzf mediabunny-1.65.2.tgz
//   (file: package/dist/bundles/mediabunny.min.mjs)
// Uses the preinstalled Playwright Chromium; no `playwright install`.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
const [page, narr, mbPath, out] = process.argv.slice(2);
if (!out) { console.error('usage: node render-mp4.js <page.html> <narration.mp3> <mediabunny.min.mjs> <out.mp4>'); process.exit(1); }
(async () => {
  const tmp = fs.mkdtempSync(path.join(path.dirname(path.resolve(out)), 'render-'));
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1300, height: 1000 } });
  await p.route(/mediabunny\.min\.mjs$/, r => r.fulfill({ status: 200, contentType: 'text/javascript', body: fs.readFileSync(mbPath) }));
  const head = '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    + '<script>window.__NARR_DATA="data:audio/mpeg;base64,' + fs.readFileSync(narr).toString('base64') + '"</script></head><body>';
  fs.writeFileSync(path.join(tmp, 'page.html'), head + fs.readFileSync(page, 'utf8') + '</body></html>');
  await p.goto('file://' + path.join(tmp, 'page.html'));
  await p.waitForFunction(() => document.getElementById('veil').hidden === true, null, { timeout: 60000 });
  if (!(await p.evaluate(() => window.__glass.narrReady()))) throw new Error('narration did not decode');
  const wav = await p.evaluate(async () => { const buf = await window.__glass.renderAudioOffline(); const ch = [buf.getChannelData(0), buf.getChannelData(1)], n = buf.length, sr = buf.sampleRate;
    const ab = new ArrayBuffer(44 + n * 4), v = new DataView(ab); const w = (o, s) => { for (let i = 0; i < s.length; i++) v.setUint8(o + i, s.charCodeAt(i)); };
    w(0, 'RIFF'); v.setUint32(4, 36 + n * 4, true); w(8, 'WAVE'); w(12, 'fmt '); v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 2, true); v.setUint32(24, sr, true); v.setUint32(28, sr * 4, true); v.setUint16(32, 4, true); v.setUint16(34, 16, true); w(36, 'data'); v.setUint32(40, n * 4, true);
    let o = 44; for (let i = 0; i < n; i++) for (let c = 0; c < 2; c++) { const s = Math.max(-1, Math.min(1, ch[c][i])); v.setInt16(o, s < 0 ? s * 0x8000 : s * 0x7fff, true); o += 2; }
    let bin = ''; const u = new Uint8Array(ab); for (let i = 0; i < u.length; i += 0x8000) bin += String.fromCharCode.apply(null, u.subarray(i, i + 0x8000)); return btoa(bin); });
  fs.writeFileSync(path.join(tmp, 'mix.wav'), Buffer.from(wav, 'base64'));
  await p.evaluate(() => { window.__glassBitrate = 45e6; });
  await p.click('#export');
  await p.waitForFunction(() => !document.getElementById('dlRow').hidden || /failed/i.test(document.getElementById('expMsg').textContent), null, { timeout: 900000, polling: 1000 });
  console.log(await p.textContent('#expInfo'));
  const [dl] = await Promise.all([p.waitForEvent('download'), p.click('#download')]); await dl.saveAs(path.join(tmp, 'hq.mp4'));
  await b.close();
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', path.join(tmp, 'hq.mp4'), '-i', path.join(tmp, 'mix.wav'), '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-shortest', out], { stdio: 'inherit' });
  fs.rmSync(tmp, { recursive: true, force: true }); console.log('wrote', out);
})().catch(e => { console.error(e); process.exit(1); });
