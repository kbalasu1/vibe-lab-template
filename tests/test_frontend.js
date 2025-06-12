/**
 * @jest-environment jsdom
 */

import { JSDOM } from 'jsdom';
import { readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

describe('Frontend Tests', () => {
  let dom;
  let document;
  let window;

  beforeAll(() => {
    const html = readFileSync(resolve(__dirname, '../src/frontend/index.html'), 'utf8');
    dom = new JSDOM(html);
    document = dom.window.document;
    window = dom.window;
  });

  test('page has required elements', () => {
    expect(document.querySelector('#image-upload')).not.toBeNull();
    expect(document.querySelector('#analyze-button')).not.toBeNull();
    expect(document.querySelector('#results-content')).not.toBeNull();
  });

  test('upload button is initially disabled', () => {
    const uploadButton = document.querySelector('#analyze-button');
    expect(uploadButton.disabled).toBe(true);
  });
}); 