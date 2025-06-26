import Markdown from "markdown-to-jsx"
import { capitalize, formatDate } from "@julseb-lib/utils"
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
			<div className="flex flex-col gap-1">
				<div className="opacity-50 text-xs">
					{capitalize(message.role)} •{" "}
					{formatDate(new Date(message.created_at)) ===
					formatDate(new Date())
						? "Today"
						: formatDate(new Date(message.created_at))}
				</div>

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

				{message.image_url && <img src={message.image_url} />}
			</div>
		</div>
	)
}

interface IMessage {
	message: Chat
}
