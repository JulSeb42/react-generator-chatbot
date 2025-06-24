import { clsx } from "utils"
import { Message } from "./Message"
import { Input } from "./Input"
import type { IMessaging } from "./types"

export const Messaging: FC<IMessaging> = ({
	chat,
	setChat,
	isLoading,
	setIsLoading,
}) => {
	return (
		<div
		className={clsx(
			"flex flex-col items-center gap-4 mx-auto p-4 border-1 border-white border-solid rounded-xl w-full max-h-[calc(100svh-48px*2-32px-24px)] grow",
		)}
		>
			<div className="flex flex-col gap-4 w-full overflow-y-scroll grow">
				{chat
					.sort((a, b) =>
						new Date(a.created_at) > new Date(b.created_at)
							? -1
							: 0,
					)
					.map(message => (
						<Message message={message} key={message._id} />
					))}

				{isLoading && <p>Thinking...</p>}
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
