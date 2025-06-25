import { TypeAnimation } from "react-type-animation"

export const Loading = () => {
	return (
		<TypeAnimation
			sequence={[
				// Same substring at the start will only be typed out once, initially
				"Thinking.",
				500,
				"Thinking..",
				500,
				"Thinking...",
				500,
			]}
			wrapper="p"
			speed={50}
			repeat={Infinity}
			cursor={false}
		/>
	)
}
