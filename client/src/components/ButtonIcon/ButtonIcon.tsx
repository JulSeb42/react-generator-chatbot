import { useState } from "react"
import { clsx } from "utils"
import type { IButtonIcon } from "./types"

const BUTTON_CLASSES =
	"inline-flex items-center h-[32px] text-white disabled:text-gray-500 cursor-pointer"

export const ButtonIcon: FC<IButtonIcon> = ({ icon, tooltip, ...rest }) => {
	const [isVisible, setIsVisible] = useState(false)

	if (tooltip)
		return (
			<span
				className="relative cursor-pointer"
				onMouseEnter={() => setIsVisible(true)}
				onMouseLeave={() => setIsVisible(false)}
			>
				<span
					className={clsx(
						"-top-[24px] left-[50%] absolute backdrop-bg px-2 rounded-md w-fit text-center whitespace-pre -translate-x-[50%] no-scrollbar",
						"after:absolute after:z-10 after:border-solid after:border-4 after:top-[103%] after:left-[50%] after:-translate-x-[50%] after:border-transparent after:border-t-white-transparent",
						isVisible ? "opacity-100 visible" : "opacity-0 hidden",
					)}
				>
					{tooltip}
				</span>

				<span className="sr-only">{tooltip}</span>

				<button className={clsx(BUTTON_CLASSES)} {...rest}>
					{icon}
				</button>
			</span>
		)

	return (
		<button className={clsx(BUTTON_CLASSES)} {...rest}>
			{icon}
		</button>
	)
}
