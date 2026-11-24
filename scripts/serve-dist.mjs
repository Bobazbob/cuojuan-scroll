import { createServer } from 'node:http';
import { createReadStream, existsSync, statSync } from 'node:fs';
import { extname, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../dist', import.meta.url));
const port = Number(process.argv[2] ?? 4173);
const mime = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8', '.png': 'image/png',
  '.ttf': 'font/ttf', '.woff2': 'font/woff2', '.txt': 'text/plain; charset=utf-8',
};

if (!existsSync(resolve(root, 'index.html'))) {
  console.error('缺少 dist/index.html，请先运行 npm run build，或使用附带的 dist。');
  process.exit(1);
}
if (!Number.isInteger(port) || port < 1 || port > 65535) {
  console.error('端口应为 1–65535 的整数。');
  process.exit(1);
}

createServer((request, response) => {
  let path;
  try {
    const route = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
    path = resolve(root, '.' + (route === '/' ? '/index.html' : route));
  } catch {
    response.writeHead(400).end();
    return;
  }
  if (!path.startsWith(root + sep) || !existsSync(path) || !statSync(path).isFile()) {
    response.writeHead(404).end('Not found');
    return;
  }
  response.writeHead(200, { 'Content-Type': mime[extname(path)] ?? 'application/octet-stream' });
  if (request.method === 'HEAD') {
    response.end();
  } else {
    createReadStream(path).pipe(response);
  }
}).listen(port, '127.0.0.1', () => console.log('错卷 · http://127.0.0.1:' + port));
