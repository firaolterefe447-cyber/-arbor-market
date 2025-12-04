/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
      /* 1. Look in the root 'templates' folder (plural) */
      '../../templates/**/*.html',

      /* 2. Look in the root 'template' folder (singular - just in case) */
      '../../template/**/*.html',

      /* 3. Look inside your apps (marketplace, user, etc.) */
      '../../**/templates/**/*.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [
    /* We will keep plugins empty for now to prevent errors.
       We can add them back once the green buttons show up. */
  ],
}