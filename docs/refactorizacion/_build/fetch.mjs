import { createDecipheriv } from 'node:crypto';
import fs from 'node:fs';

const MASTER_KEY = process.env.MASTER_KEY;
const TOKEN_FILE = process.env.TOKEN_FILE;

function deriveKey(masterKey) {
  const raw = Buffer.from(masterKey, 'base64');
  if (raw.length === 32) return raw;
  return createHashFallback(masterKey);
}
function createHashFallback(s) {
  // sha256 via node
  return require('node:crypto').createHash('sha256').update(s, 'utf8').digest();
}

const raw = Buffer.from(MASTER_KEY, 'base64');
const key = raw.length === 32 ? raw : createDecipheriv && (await import('node:crypto')).createHash('sha256').update(MASTER_KEY, 'utf8').digest();

const file = JSON.parse(fs.readFileSync(TOKEN_FILE, 'utf8'));
const decipher = createDecipheriv('aes-256-gcm', key, Buffer.from(file.iv, 'base64'));
decipher.setAuthTag(Buffer.from(file.tag, 'base64'));
const plaintext = Buffer.concat([
  decipher.update(Buffer.from(file.data, 'base64')),
  decipher.final(),
]);
const tokenData = JSON.parse(plaintext.toString('utf8'));
const accessToken = tokenData.access_token || tokenData.accessToken || tokenData.access;

const IDS = {
  notas: '1a0d3e8fdce7dc43',
  funcionarios: '1a0d3e8886aca81c',
  becas: '1a0d3e7e8df9c160',
  agenda: '1a0d3e739fbb5894',
  contable: '1a0d3e6f55b9e025',
  procesos: '1a0d3e93af710ff9',
};

const OUT = process.env.OUT_DIR;

function decodeData(d) {
  return d ? Buffer.from(d, 'base64url').toString('utf8') : '';
}

function collectParts(part, acc) {
  const mime = (part.mimeType || '').toLowerCase();
  if (mime === 'text/plain' && part.body?.data) {
    acc.push(decodeData(part.body.data));
  }
  for (const p of part.parts || []) collectParts(p, acc);
}

function extractText(payload) {
  if (payload.body?.data && (payload.mimeType || '').toLowerCase() === 'text/plain') {
    return decodeData(payload.body.data);
  }
  const acc = [];
  collectParts(payload, acc);
  if (acc.length) return acc.join('\n');
  return payload.body?.data ? decodeData(payload.body.data) : '';
}

for (const [name, id] of Object.entries(IDS)) {
  const res = await fetch(
    `https://gmail.googleapis.com/gmail/v1/users/me/messages/${id}?format=full`,
    { headers: { Authorization: `Bearer ${accessToken}` } }
  );
  if (!res.ok) {
    console.error(name, res.status, await res.text());
    continue;
  }
  const msg = await res.json();
  const body = extractText(msg.payload);
  fs.writeFileSync(`${OUT}/${name}.txt`, body, 'utf8');
  const header = (n) => {
    const h = msg.payload.headers.find((x) => x.name.toLowerCase() === n);
    return h ? h.value : '';
  };
  console.log(
    name.padEnd(13),
    String(body.length).padStart(7),
    'chars |',
    header('subject')
  );
}
