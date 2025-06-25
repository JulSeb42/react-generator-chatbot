import SyntaxHighlighter from "react-syntax-highlighter"
import { a11yDark } from "react-syntax-highlighter/dist/esm/styles/hljs"
import type { MarkdownToJSX } from "markdown-to-jsx"

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

const Link = (props: HTMLAnchorElement) => {
	// @ts-ignore
	return <a {...props} target="_blank" rel="noreferrer noopener" />
}

export const optionsMarkdown: MarkdownToJSX.Options = {
	wrapper: Flex,
	overrides: {
		pre: { component: CodeBlock },
		a: { component: Link },
	},
}
