import { clsx } from "utils"
import type { IAlert } from "./types"

export const Alert: FC<IAlert> = ({ children }) => {
	return (
		<div
			className={clsx(
				"flex flex-col gap-2 bg-red-50 p-4 border-1 border-red-500 border-solid rounded-lg w-full text-black",
			)}
		>
			{children}
		</div>
	)
}
