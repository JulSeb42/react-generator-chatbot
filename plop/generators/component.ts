import type { NodePlopAPI, ActionType } from "plop"
import { BASE_CLIENT_PATH, TEMPLATES_PATH } from "../utils/index.js"

export default (plop: NodePlopAPI) => {
	const { setGenerator } = plop

	setGenerator("component", {
		description: "Create a React component",
		prompts: [
			{ name: "name", type: "input", message: "Enter component's name" },
			{
				name: "tag",
				type: "input",
				message: "Enter HTML tag",
				default: "div",
			},
			{
				name: "ref",
				type: "confirm",
				message: "Add ref?",
				default: false,
			},
			{
				type: "input",
				name: "attribute",
				message: "Enter HTML attribute",
				default: (data: { tag: string }) => data.tag,
				when: data => data.ref,
			},
			{
				type: "confirm",
				name: "export",
				message: "Export this component from components folder?",
				default: true,
			},
		],
		// actions: [],
		actions: data => {
			const actions: Array<ActionType> = [
				"Creating new files",
				{
					type: "addMany",
					destination: `${BASE_CLIENT_PATH}/components/{{>pascalName}}`,
					templateFiles: `${TEMPLATES_PATH}/component/*.hbs`,
					base: `${TEMPLATES_PATH}/component`,
					verbose: true,
				},
			]

			if (data?.export) {
				actions.push("Exporting your new component", {
					type: "modify",
					path: `${BASE_CLIENT_PATH}/components/index.ts`,
					template: 'export * from "./{{>pascalName}}"\n$1',
					pattern:
						/(\/\* Prepend export components - DO NOT REMOVE \*\/)/g,
				})
			}

			return actions
		},
	})
}
