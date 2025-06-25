import Markdown from "markdown-to-jsx"
import { clsx } from "utils"
import { optionsMarkdown } from "./options-markdown"
import type { Chat } from "types"

export const Message: FC<IMessage> = ({ message }) => {
	return (
		<div
			className={clsx(
				"flex backdrop-bg p-2 rounded-lg w-fit max-w-[90%] md:max-w-[400px] [&>*>*]:max-w-full [&>*>*]:overflow-x-scroll",
				message.role === "user" ? "self-end" : "self-start",
			)}
		>
			<Markdown
				className={clsx(
					"max-w-full message",
					"[&>*]:max-w-full [&>*>*]:max-w-full",
					"[&>a]:underline",
				)}
				options={optionsMarkdown}
			>
				{message.message}
			</Markdown>
		</div>
	)
}

interface IMessage {
	message: Chat
}
