---
name: frontend-react
description: Build React web frontends to enterprise standards. Extends code-generation with React and UI specifics.
preferred_models:
  - claude-opus
  - claude-sonnet
allowed_tools:
  - filesystem.write
requires:
  - code-generation
success_criteria:
  - Every stored state value is independent; values derivable from props or state are computed during render
  - Every `useEffect` synchronizes with an external system and declares all reactive dependencies
  - Every rendered list uses stable unique keys from data, never array indexes or render-time generated values
  - Each form field keeps exactly one source of truth for its value across the field's lifetime
  - User content is rendered through React text interpolation unless sanitized HTML is explicitly required at the trust boundary
  - Components stay focused enough to scan; large JSX blocks or hook-heavy components are split by responsibility
tags:
  - react
  - frontend
  - ui
  - web
paths:
  - "**/*.tsx"
  - "**/*.jsx"
---

# Frontend (React)

Specialization of `code-generation` for React web frontends. The foundation rules apply unchanged; the rules below add what is specific to React state, effects, lists, forms, rendering, and component shape. Citations live in `frontend-react.sources.md` next to this file.

## When to use

Writing or modifying a React web UI — components, hooks, forms, lists, client-side state, rendering logic, or browser-facing presentation code. Applies whether the app is built with Create React App, Vite, Next.js, or a custom React setup. Not for React Native, backend-only work, or non-React frontend code — those belong to a different specialization or to `code-generation` alone.

## Rules

1. **Derive state; do not store what can be computed.** `useState` is for independent facts that change over time, not for values you can calculate from props, loader data, URL state, or other state during render. Storing derived values creates two sources of truth, stale renders, and extra update paths. If the calculation is cheap, compute it inline; if it is expensive, use `useMemo` only after measuring or when the cost is obvious.

2. **`useEffect` is the last resort.** Effects synchronize React with an external system — network, browser API, subscription, timer, third-party widget, analytics sink. Never use an Effect to derive render data and never use one to respond to a click, submit, or keystroke that has an event handler. When an Effect is justified, declare every reactive dependency and make cleanup mirror setup.

3. **List keys are stable and unique, never the array index.** Keys identify the same logical item across renders. Use database IDs, persistent local IDs, or IDs created when the item is created. Do not use `key={i}`, `Math.random()`, `Date.now()`, or generated values during render. Index keys break state, focus, and animations when items reorder, insert, or delete.

4. **Controlled inputs have one source of truth.** If a form field receives `value` or `checked`, it must also receive a synchronous `onChange` that updates that backing state. Do not switch between uncontrolled and controlled mode over the field's lifetime. Use `defaultValue` or `defaultChecked` only for intentionally uncontrolled fields, and keep submit parsing explicit at the boundary.

5. **Escape user content; `dangerouslySetInnerHTML` requires sanitization at the trust boundary.** React text interpolation escapes by default; prefer `{user.name}` and normal children. Only render HTML when the product truly needs HTML semantics, and sanitize once at the boundary where untrusted content becomes trusted HTML. Never pass raw user input, Markdown output, CMS content, or API HTML directly into `dangerouslySetInnerHTML`.

6. **Components stay small and focused.** Roughly 150 lines of JSX or 5 hooks is a soft ceiling — past it, split. Separate data loading, state transitions, form controls, list rows, and layout sections when they change for different reasons. A component should be easy to scan from props to returned JSX without tracking unrelated state machines in the same body.

## Examples

### Example 1: derived state stored in useState

Task: "Add a profile editor that shows a live display name preview from first and last name fields."

**Common AI failure:**

```tsx
import { useEffect, useState } from 'react';
export function ProfileEditor() {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [fullName, setFullName] = useState('');
  useEffect(() => {
    setFullName(`${firstName} ${lastName}`.trim());
  }, [firstName, lastName]);
  return (
    <form>
      <input value={firstName} onChange={e => setFirstName(e.target.value)} />
      <input value={lastName} onChange={e => setLastName(e.target.value)} />
      <p>Preview: {fullName}</p>
    </form>
  );
}
```

Why this fails: `fullName` is not independent state. It is fully determined by `firstName` and `lastName`, so storing it creates a second source of truth and forces an extra render with stale data before the Effect runs. The Effect is also unnecessary because no external system is being synchronized. Violates Rules 1 and 2.

**Correct pattern:**

```tsx
import { useState } from 'react';
export function ProfileEditor() {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const fullName = `${firstName} ${lastName}`.trim();
  return (
    <form>
      <input value={firstName} onChange={e => setFirstName(e.target.value)} />
      <input value={lastName} onChange={e => setLastName(e.target.value)} />
      <p>Preview: {fullName || 'Unnamed user'}</p>
    </form>
  );
}
```

Why this works: `fullName` is calculated during render from the current state, so it cannot drift out of sync. Removing the Effect removes the extra render pass and the dependency surface entirely. The only stored state is the user-editable input values, which are the independent facts.

---

### Example 2: array index as list key

Task: "Render a todo list where users can delete completed items."

**Common AI failure:**

```tsx
export function TodoList({ todos, onToggle, onDelete }) {
  return (
    <ul>
      {todos.map((todo, i) => (
        <li key={i}>
          <label>
            <input type="checkbox" checked={todo.done} onChange={() => onToggle(todo.id)} />
            {todo.title}
          </label>
          <button onClick={() => onDelete(todo.id)}>Delete</button>
        </li>
      ))}
    </ul>
  );
}
```

Why this fails: the key is the item's position, not the item. Delete the first todo and every later item receives a different key, so React may preserve the wrong checkbox state, focus, animation state, or child component state on the wrong row. The bug appears only after insert, delete, or reorder, which is exactly what this list supports. Violates Rule 3.

**Correct pattern:**

```tsx
export function TodoList({ todos, onToggle, onDelete }) {
  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id}>
          <label>
            <input type="checkbox" checked={todo.done} onChange={() => onToggle(todo.id)} />
            {todo.title}
          </label>
          <button onClick={() => onDelete(todo.id)}>Delete</button>
        </li>
      ))}
    </ul>
  );
}
```

Why this works: `todo.id` is stable for the logical todo, so React can preserve state with the correct row even when the array changes shape. The key comes from data rather than render order, so delete and reorder operations do not scramble identity.

---

### Example 3: `dangerouslySetInnerHTML` with user input

Task: "Render rich-text comments that users write in a Markdown editor."

**Common AI failure:**

```tsx
type Comment = { author: string; html: string };

export function CommentCard({ comment }: { comment: Comment }) {
  return (
    <article>
      <h3>{comment.author}</h3>
      <div dangerouslySetInnerHTML={{ __html: comment.html }} />
    </article>
  );
}
```

Why this fails: `comment.html` is user-controlled HTML. Passing it straight to `dangerouslySetInnerHTML` bypasses React's default escaping and allows injected event handlers, scripts through dangerous contexts, or malicious links to execute in the user's browser. The prop name says `html`, but nothing proves the content was sanitized. Violates Rule 5.

**Correct pattern:**

```tsx
import DOMPurify from 'dompurify';

type Comment = { author: string; rawHtml: string };

function sanitizeCommentHtml(rawHtml: string) {
  return { __html: DOMPurify.sanitize(rawHtml) };
}

export function CommentCard({ comment }: { comment: Comment }) {
  const sanitized = sanitizeCommentHtml(comment.rawHtml);
  return (
    <article>
      <h3>{comment.author}</h3>
      <div dangerouslySetInnerHTML={sanitized} />
    </article>
  );
}
```

Why this works: the unsafe boundary is explicit: raw HTML enters as `rawHtml`, is sanitized before it becomes the `{ __html }` object React requires, and only that sanitized object reaches `dangerouslySetInnerHTML`. The author is still rendered through normal React text interpolation, so it stays auto-escaped. A real project should keep DOMPurify or its approved equivalent patched and centralize this boundary.
