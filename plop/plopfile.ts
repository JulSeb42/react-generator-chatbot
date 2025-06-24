import type { NodePlopAPI } from "plop"
import figlet from "figlet"
import chalk from "chalk"
import { runCommand } from "./actions"
import {
	generateGenerator,
	generateComponent,
	generatePage,
	generateRoute,
	generateSingleComponent,
	/* Prepend import - DO NOT REMOVE */
} from "./generators"
import { pascalName, kebabName } from "./partials"
import { surroundBrackets, addOpenBrackets, addClosingBrackets } from "./utils"

export default (plop: NodePlopAPI) => {
	const { load } = plop

	console.log(
		chalk.blueBright(
			figlet.textSync("JulSeb CLI", { horizontalLayout: "full" }),
		),
	)

	load("plop-pack-remove") // With this helper you can remove files in your project. Full doc here https://github.com/TheSharpieOne/plop-pack-remove
	runCommand(plop) // With this helper you can run commands in a terminal => { type: "runCommand", command: "console.log("hello world")" }

	pascalName(plop) // Shortcut for {{ pascalCase name }}, use: {{>pascalName }}
	kebabName(plop) // Shortcut for {{ kebabCase name }}, use: {{>kebabName }}

	surroundBrackets(plop) // Surround with brackets in templates when needed
	addOpenBrackets(plop) // Add double open brackets {{ where needed
	addClosingBrackets(plop) // Add double closing brackets }} where needed

	generateGenerator(plop) // yarn plop:g
	generateComponent(plop) // yarn plop:c
	generatePage(plop) // yarn plop:p
	generateRoute(plop) // yarn plop:r
	generateSingleComponent(plop) // yarn plop:s
	/* Prepend function - DO NOT REMOVE */
}
