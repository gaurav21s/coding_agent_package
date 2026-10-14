import React from 'react';
import { renderToPipeableStream } from 'react-dom/server';

/**
 * A simple component represented as a function.
 * Using React.createElement instead of JSX.
 */
function ListComponent() {
  return React.createElement(
    'ul',
    null,
    React.createElement('li', null, 'Item 1'),
    React.createElement('li', null, 'Item 2'),
    React.createElement('li', null, 'Item 3')
  );
}

// Create the stream from the component
const stream = renderToPipeableStream(React.createElement(ListComponent), {
  onShellReady() {
    // Pipe the stream to stdout
    stream.pipe(process.stdout);
  },
  onAllReady() {
    // Print 'done' once the stream has finished
    process.stdout.write('\ndone\n');
  },
  onError(error) {
    console.error(error);
  }
});
