// Add to the Remotion project's eslint.config.mjs: no string may be written straight into
// the film's JSX, so every on-screen line goes through line() and check_facts.py.
export const filmRules = {
  files: ["src/Film.tsx", "src/film/**/*.tsx"],
  rules: {
    "react/jsx-no-literals": ["error", { noStrings: true, ignoreProps: true }],
  },
};
// export default [...config, filmRules];
