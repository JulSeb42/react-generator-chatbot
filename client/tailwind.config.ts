import type { Config } from "tailwindcss"

const config: Config = {
	content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
	theme: {
		extend: {
			fontFamily: {
				sans: ["var(--font-family-body)"],
			},
			animation: {},
			keyframes: {},
		},
	},
}

// eslint-disable-next-line
export default config
