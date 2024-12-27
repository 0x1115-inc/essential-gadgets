import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}', // All files in the `app` folder
    './components/**/*.{js,ts,jsx,tsx}', // All global components
    './features/**/*.{js,ts,jsx,tsx}', // Feature-specific components
  ],
  theme: {
    extend: {}, // Extend Tailwind's default theme if needed
  },
  plugins: [], // Add plugins if required
};

export default config;
