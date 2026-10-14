To stream server-rendered React components to `process.stdout` in a Node.js environment, you should use the `renderToPipeableStream` function from `react-dom/server`. This function provides a `pipe` method that can stream the output directly to a writable stream, such as `process.stdout`.

The following program uses `React.createElement` to define a `<ul>` component with three `<li>` items and pipes the resulting stream to standard output.

```javascript
import React from 'react';
import { renderToPipeableStream } from 'react-dom/server';

/**
 * A simple component that renders a <ul> with 3 <li> items.
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

// Create the stream
const stream = renderToPipeableStream(React.createElement(ListComponent), {
  onShellReady() {
    // Pipe the stream to process.stdout
    stream.pipe(process.stdout);
  },
  onAllReady() {
    // Once the stream has finished, print 'done'
    process.stdout.write('\ndone\n');
  },
  onError(error) {
    console.error(error);
  }
});
```