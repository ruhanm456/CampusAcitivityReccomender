import { configure } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';

configure({
  getElementError: (message) => {
    const error = new Error(
      message?.split('\n').slice(0, 2).join('\n') // Keep only first 2 lines
    );
    error.name = 'TestingLibraryElementError';
    return error;
  },
});