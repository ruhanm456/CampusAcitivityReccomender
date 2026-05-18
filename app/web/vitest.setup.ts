import { configure } from '@testing-library/react';

configure({
  getElementError: (message) => {
    const error = new Error(
      message?.split('\n').slice(0, 2).join('\n') // Keep only first 2 lines
    );
    error.name = 'TestingLibraryElementError';
    return error;
  },
});