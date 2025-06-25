import { useEffect, useRef } from "react"
import { clsx } from "utils"
import { Message } from "./Message"
import { Input } from "./Input"
import { Loading } from "components/Loading"
import type { IMessaging } from "./types"

export const Messaging: FC<IMessaging> = ({
	chat,
	setChat,
	isLoading,
	setIsLoading,
}) => {
	const messagesEndRef = useRef<HTMLDivElement>(null)

	const scrollToBottom = () => {
		messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
	}

	useEffect(() => {
		scrollToBottom()
	}, [chat, isLoading])

	return (
		<div
			className={clsx(
				"flex flex-col items-center gap-4 mx-auto p-4 border-1 border-white border-solid rounded-xl w-full max-h-[calc(100svh-48px*2-32px-24px)] grow",
			)}
		>
			<div className="flex flex-col gap-4 w-full overflow-y-scroll grow">
				{!chat.length && (
					<div className="flex justify-center items-center w-full h-full">
						{isLoading ? (
							<Loading string="Getting chats" />
						) : (
							<p>Write your first message!</p>
						)}
					</div>
				)}

				{chat.map(message => (
					<Message message={message} key={message._id} />
				))}

				{isLoading && chat.length ? (
					<Loading string="Thinking" />
				) : null}

				<div ref={messagesEndRef} />
			</div>

			<hr className="bg-white border-none w-full h-0.5" />

			<Input
				chats={chat}
				setChats={setChat}
				isLoading={isLoading}
				setIsLoading={setIsLoading}
			/>
		</div>
	)
}
