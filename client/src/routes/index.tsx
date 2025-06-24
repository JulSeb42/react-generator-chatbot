import { useState, useEffect } from "react"
import { createFileRoute } from "@tanstack/react-router"
import { toast } from "react-toastify"
import { Messaging } from "components"
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
		<main className="flex flex-col gap-6 mx-auto p-12 w-full max-w-[90%] h-svh">
			<h1 className="font-black text-2xl">
				React code generator chatbot
			</h1>

			<Messaging
				chat={chat}
				setChat={setChat}
				isLoading={isLoading}
				setIsLoading={setIsLoading}
			/>

			{/* <button onClick={handleReactPage}>New React page</button> */}

			{/* {isLoading && <p>Loading...</p>} */}

			{/* <Chat messages={chat} setMessages={setChat} /> */}

			{/* <Chat />
			<button onClick={handleNewChat}>New chat</button>
			

			{sessionId && <button onClick={deleteChat}>Delete session</button>}
			 */}
		</main>
	)
}

export const Route = createFileRoute("/")({
	component: App,
})
