import { createServer } from 'http';
import { readFileSync, existsSync } from 'fs';
import { extname, join } from 'path';
import { spawn } from 'child_process';

const port = Number(process.env.PORT || 3000);
const root = process.cwd();

const build = spawn('npx', ['esbuild', 'src/main.ts', '--bundle', '--outfile=dist/main.js', '--format=esm', '--sourcemap'], { stdio: 'inherit' });
build.on('close', () => {
  createServer((req, res) => {
    let file = req.url === '/main.js' ? 'dist/main.js' : 'index.html';
    const path = join(root, file);
    if (!existsSync(path)) {
      res.statusCode = 404;
      return res.end('Not found');
    }
    const type = extname(path) === '.js' ? 'text/javascript; charset=utf-8' : 'text/html; charset=utf-8';
    res.setHeader('Content-Type', type);
    res.end(readFileSync(path));
  }).listen(port, '0.0.0.0', () => console.log(`Angular SPA em ${port}`));
});
