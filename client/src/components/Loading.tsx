import { TypeAnimation } from "react-type-animation"

export const Loading: FC<ILoading> = ({ string = "Thinking" }) => {
	return (
		<TypeAnimation
			sequence={[
				`${string}.`,
				500,
				`${string}..`,
				500,
				`${string}...`,
				500,
			]}
			wrapper="p"
			speed={50}
			repeat={Infinity}
			cursor={false}
			preRenderFirstString
		/>
	)
}

interface ILoading {
	string?: string
}
