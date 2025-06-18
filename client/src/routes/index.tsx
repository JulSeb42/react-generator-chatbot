import { use, useEffect } from "react"
import axios from "axios"
import { createFileRoute } from "@tanstack/react-router"
import { BASE_API_URL } from "api/server-paths"

const App = () => {
	useEffect(() => {
		axios
			.get(BASE_API_URL)
			.then(res => console.log(res.data))
			.catch(err => console.log(err))
	}, [])

	return (
		<main>
			<h1>React code generator chatbot</h1>
		</main>
	)
}

export const Route = createFileRoute("/")({
	component: App,
})
