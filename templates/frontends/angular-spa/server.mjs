import { createServer } from 'http';
import { readFileSync, existsSync } from 'fs';
import { dirname, extname, join, resolve } from 'path';
import { build } from 'esbuild';

const port = Number(process.env.PORT || 3000);
const root = process.cwd();

const angularResourcePlugin = {
  name: 'angular-resource-plugin',
  setup(buildContext) {
    buildContext.onLoad({ filter: /src[\\/].*\.ts$/ }, async (args) => {
      let source = readFileSync(args.path, 'utf8');
      const baseDir = dirname(args.path);

      source = source.replace(/templateUrl:\s*['"](.+?)['"]/g, (_, templatePath) => {
        const template = readFileSync(resolve(baseDir, templatePath), 'utf8');
        return `template: ${JSON.stringify(template)}`;
      });

      source = source.replace(/styleUrl:\s*['"](.+?)['"]/g, (_, stylePath) => {
        const style = readFileSync(resolve(baseDir, stylePath), 'utf8');
        return `styles: [${JSON.stringify(style)}]`;
      });

      return { contents: source, loader: 'ts' };
    });
  }
};

build({
  entryPoints: ['src/main.ts'],
  bundle: true,
  outfile: 'dist/main.js',
  format: 'esm',
  sourcemap: true,
  tsconfig: 'tsconfig.json',
  plugins: [angularResourcePlugin]
}).then(() => {
  createServer((req, res) => {
    const url = req.url?.split('?')[0] || '/';
    const publicFiles = new Map([
      ['/main.js', 'dist/main.js'],
      ['/main.js.map', 'dist/main.js.map']
    ]);
    const file = publicFiles.get(url) || 'index.html';
    const path = join(root, file);
    if (!existsSync(path)) {
      res.statusCode = 404;
      return res.end('Not found');
    }
    const type = extname(path) === '.js'
      ? 'text/javascript'
      : extname(path) === '.map'
        ? 'application/json'
        : 'text/html';
    res.setHeader('Content-Type', type);
    res.end(readFileSync(path));
  }).listen(port, '0.0.0.0', () => console.log(`Angular SPA em ${port}`));
}).catch((error) => {
  console.error(error);
  process.exit(1);
});
