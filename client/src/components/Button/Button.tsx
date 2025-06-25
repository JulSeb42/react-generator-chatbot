import { clsx } from "utils"
import type { IButton, ButtonColor, ButtonVariant } from "./types"

export const Button: FC<IButton> = ({
	color = "primary",
	variant = "primary",
	...rest
}) => {
	return (
		<button
			className={clsx(
				"px-4 py-2 rounded-md font-bold",
				genVariant[variant][color],
			)}
			{...rest}
		/>
	)
}

const genVariant: Record<ButtonVariant, Record<ButtonColor, string>> = {
	primary: {
		primary: "bg-blue-500 text-white hover:bg-blue-300 active:bg-blue-600",
		danger: "bg-red-500 text-white hover:bg-red-300 active:bg-red-600",
	},
	secondary: {
		primary: "text-blue-500 hover:text-blue-300 active:text-blue-600",
		danger: "text-red-500 hover:text-red-300 active:text-red-600",
	},
}
