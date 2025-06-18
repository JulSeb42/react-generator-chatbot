import { useState } from "react"
import axios from "axios"
import SyntaxHighlighter from "react-syntax-highlighter"
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism"
import { clsx } from "utils"
import type { IChat } from "./types"

type Message = { role: "user" | "assistant"; content: string }

export const Chat: FC<IChat> = ({}) => {
	const [input, setInput] = useState("")
	const [messages, setMessages] = useState<Array<Message>>([])
	const [loading, setLoading] = useState(false)

	const handleSend = async () => {
		if (!input.trim()) return
		setLoading(true)

		const userMessage: Message = { role: "user", content: input }
		setMessages(prev => [...prev, userMessage])

		try {
			const res = await axios.post("http://localhost:5000/chat", {
				message: input,
			})

			const botReply: Message = {
				role: "assistant",
				content: res.data.reply,
			}
			setMessages(prev => [...prev, botReply])
		} catch (error: any) {
			alert("Error: " + error.message)
		}

		setInput("")
		setLoading(false)
	}

	return (
		<div className={clsx()}>
			<div style={{ minHeight: 300, marginBottom: 20 }}>
				{messages.map((msg, idx) => (
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
				))}
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
