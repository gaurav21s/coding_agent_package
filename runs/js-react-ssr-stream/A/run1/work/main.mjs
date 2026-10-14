import React from 'react';
import { renderToPipeableStream } from 'react-dom/server';

/**
 * A simple component representing a list of items.
 * Using React.createElement as requested (no JSX).
 */
const ListComponent = () => {
  return React.createElement(
    'ul',
    null,
    React.createElement('li', null, 'Item 1'),
    React.createElement('li', null, 'Item 2'),
    React.createElement('li', null, 'Item 3')
  );
};

/**
 * Stream the component to process.stdout.
 * renderToPipeableStream returns an object with a pipe method.
 */
const stream = renderToPipeableStream(React.createElement(ListComponent), {
  onAllReady() {
    // Pipe the stream to stdout
    stream.pipe(process.stdout);
    
    // Since pipe is synchronous in terms of setup, we listen for the 
    // finish event on the stream to print 'done'.
    process.stdout.on('finish', () => {
      process.stdout.write('\ndone\n');
    });
  },
  onError(error) {
    console.error(error);
  }
});
