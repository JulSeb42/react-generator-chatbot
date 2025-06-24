import { useState, useRef, type KeyboardEvent } from "react"
import { BiSend } from "react-icons/bi"
import { toast } from "react-toastify"
import { chatService } from "api"
import type { Chat } from "types"

export const Input: FC<IInput> = ({
	chats,
	setChats,
	isLoading,
	setIsLoading,
}) => {
	const formRef = useRef<HTMLFormElement>(null)

	const [message, setMessage] = useState("")
	const sessionId = localStorage.getItem("session_id")

	const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
		if (e.key === "Enter" && !e.shiftKey) {
			e.preventDefault()
			if (message.length) handleSubmit(e as any) // Submit the form
		}
	}

	const handleSubmit = (e: FormEvent) => {
		e.preventDefault()

		setIsLoading(true)

		setChats([
			...chats,
			{
				message,
				session_id: sessionId ?? null,
				_id: "",
				role: "user",
				created_at: new Date().toString(),
			},
		])
		setMessage("")

		chatService
			.newChat({ message, session_id: sessionId })
			.then(res => {
				if (!sessionId)
					localStorage.setItem("session_id", res.data.session_id!)
				setChats([
					...chats,
					{
						message,
						session_id: sessionId ?? null,
						_id: "",
						role: "user",
						created_at: new Date().toString(),
					},
					res.data,
				])
			})
			.catch(err => {
				toast.error("An error occurred, check console")
				console.log(err)
			})
	}

	return (
		<form
			onSubmit={handleSubmit}
			className="flex items-end gap-2 w-full"
			ref={formRef}
		>
			<textarea
				className="flex backdrop-bg px-4 border-1 border-white border-solid rounded-lg outline-0 w-full min-h-[32px] field-sizing-content resize-none disabled:cursor-not-allowed"
				value={message}
				onChange={e => setMessage(e.target.value)}
				onKeyDown={handleKeyDown}
				rows={1}
				autoFocus
			/>

			<button
				type="submit"
				disabled={isLoading}
				className="inline-flex items-center h-[32px]"
			>
				<BiSend />
			</button>
		</form>
	)
}

interface IInput {
	chats: Array<Chat>
	setChats: DispatchState<Array<Chat>>
	isLoading: boolean
	setIsLoading: DispatchState<boolean>
}
