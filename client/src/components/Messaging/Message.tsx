import Markdown, { type MarkdownToJSX } from "markdown-to-jsx"
import SyntaxHighlighter from "react-syntax-highlighter"
import { a11yDark } from "react-syntax-highlighter/dist/esm/styles/hljs"
import { clsx } from "utils"
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
					// "max-w-[600px]",
					// message.role === "user"
					// 	? "backdrop-bg  "
					// 	: "backdrop-bg p-2 rounded-lg",
					"[&>*]:max-w-full [&>*>*]:max-w-full",
				)}
				options={optionsMarkdown}
			>
				{message.message}
			</Markdown>
		</div>
	)
}

const CodeBlock = ({ children }: { children: Children }) => {
	return (
		<SyntaxHighlighter language="javascript" style={a11yDark}>
			{String((children as any).props.children).replace(/\n$/, "")}
		</SyntaxHighlighter>
	)
}

const Flex = ({ children }: { children?: Children }) => {
	return <div className="flex flex-col gap-2 message">{children}</div>
}

const optionsMarkdown: MarkdownToJSX.Options = {
	wrapper: Flex,
	overrides: {
		pre: {
			component: CodeBlock,
		},
	},
}

interface IMessage {
	message: Chat
}
