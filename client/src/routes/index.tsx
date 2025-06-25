import { useState, useEffect } from "react"
import { createFileRoute } from "@tanstack/react-router"
import { toast } from "react-toastify"
import { Page, Messaging } from "components"
import { chatService } from "api"
import type { Chat as ChatType } from "types"

const App = () => {
	const [chat, setChat] = useState<Array<ChatType>>([])
	const [isLoading, setIsLoading] = useState(false)

	const sessionId = localStorage.getItem("session_id")

	useEffect(() => {
		if (sessionId) {
			setIsLoading(true)
			chatService
				.sessionMessages(sessionId)
				.then(res => setChat(res.data))
				.catch(err => {
					toast.error("An error occurred, check console")
					console.log(err)
				})
				.finally(() => setIsLoading(false))
		}
	}, [sessionId])

	return (
		<Page title="Chat">
			<h1 className="font-black text-2xl">
				React code generator chatbot
			</h1>

			<Messaging
				chat={chat}
				setChat={setChat}
				isLoading={isLoading}
				setIsLoading={setIsLoading}
			/>
		</Page>
	)
}

export const Route = createFileRoute("/")({
	component: App,
})
