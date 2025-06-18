import { createFileRoute } from "@tanstack/react-router"
import { Chat } from "components"

export const Route = createFileRoute("/")({
	component: App,
})

function App() {
	return (
		<main>
			<h1>React code generator chatbot</h1>

			<Chat />
		</main>
	)
}
