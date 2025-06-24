import { useState } from "react"
import axios from "axios"
import SyntaxHighlighter from "react-syntax-highlighter"
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism"
import { clsx } from "utils"
import { chatService } from "api"
import type { Chat as ChatType } from "types"
import type { IChat } from "./types"

// type Message = { role: "user" | "assistant"; content: string }

export const Chat: FC<IChat> = ({ messages, setMessages }) => {
	const [input, setInput] = useState("")
	// const [messages, setMessages] = useState<Array<Message>>([])
	const [loading, setLoading] = useState(false)

	const handleSend = async () => {
		if (!input.trim()) return
		setLoading(true)

		const userMessage = { role: "user", content: input }
		setMessages(prev => [...prev, { role: "user", message: input }] as any)

		try {
			// const res = await axios.post(
			// 	"http://localhost:8000/chat/new-chat",
			// 	{
			// 		message: input,
			// 	},
			// )
			const res = await chatService.newChat(input)
			setMessages(
				prev =>
					[
						...prev,
						{ role: "assistant", content: res.data.message },
					] as any,
			)
		} catch (error: any) {
			alert("Error: " + error.message)
		}

		setInput("")
		setLoading(false)
	}

	return (
		<div className={clsx()}>
			<div style={{ minHeight: 300, marginBottom: 20 }}>
				{/* {messages.map((msg, idx) => (
					<div key={idx} style={{ margin: "1rem 0" }}>
						<strong>{msg.role === "user" ? "You" : "Bot"}:</strong>
						{msg.role === "assistant" &&
						msg.content.includes("```") ? (
							<CodeBlock text={msg.content} />
						) : (
							<pre style={{ whiteSpace: "pre-wrap" }}>
								{msg.content}
							</pre>
						)}
					</div>
				))} */}
				{loading && <p>Loading...</p>}
			</div>

			<textarea
				rows={3}
				value={input}
				onChange={e => setInput(e.target.value)}
				placeholder="Ask me to write some React code..."
				style={{ width: "100%", padding: 10 }}
			/>
			<button onClick={handleSend} disabled={loading}>
				{loading ? "Generating..." : "Send"}
			</button>
		</div>
	)
}

const CodeBlock = ({ text }: { text: string }) => {
	const match = text.match(/```(?:\w+)?\n([\s\S]*?)```/)
	const code = match ? match[1] : text

	return (
		<SyntaxHighlighter language="jsx" style={oneDark}>
			{code}
		</SyntaxHighlighter>
	)
}
