import { jest } from '@jest/globals';

// Add TextEncoder and TextDecoder polyfills
import { TextEncoder, TextDecoder } from 'util';
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// Mock browser APIs not available in Jest
global.FileReader = class {
    readAsDataURL() {
        this.onload && this.onload({
            target: {
                result: 'data:image/jpeg;base64,/9j/4AAQSkZJRg=='
            }
        });
    }
};

// Mock scrollIntoView
Element.prototype.scrollIntoView = jest.fn();

// Mock the fetch API
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({}),
  })
);

// Mock FileReader
class FileReaderMock {
  readAsDataURL() {
    setTimeout(() => {
      this.onload({ target: { result: 'data:image/jpeg;base64,test' } });
    }, 0);
  }
}
global.FileReader = FileReaderMock; 