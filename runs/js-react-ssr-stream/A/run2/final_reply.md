To stream React components to `stdout` in a Node.js environment using modern APIs, we use `renderToPipeableStream` from `react-dom/server`. This function provides a `pipe` method that can stream the output directly to a `Writable` stream like `process.stdout`.

Since we are using ES modules, we import `React` and `ReactDOMServer` directly. Note that `renderToPipeableStream` is the standard, non-deprecated way to perform server-side rendering in React 18/19.

Here is the `main.mjs` file:

```javascript
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
```

### How to run:
1. Ensure you have `react` and `react-dom` installed:
   `npm install react react-dom`
2. Save the code above as `main.mjs`.
3. Run the program:
   `node main.mjs`

This will output the HTML string of the `<ul>` list followed by the word "done" on a new line.