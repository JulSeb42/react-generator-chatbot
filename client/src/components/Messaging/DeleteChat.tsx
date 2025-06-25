import { toast } from "react-toastify"
import { BiTrash } from "react-icons/bi"
import { chatService } from "api"
import type { Chat } from "types"

export const DeleteChat: FC<IDeleteChat> = ({ chats, setChats }) => {
	const sessionId = localStorage.getItem("session_id")

	const handleDelete = () => {
		chatService
			.deleteSession(sessionId!)
			.then(() => {
				toast.success("Your chat has been deleted")
				setChats([])
			})
			.catch(err => {
				console.log(err)
				toast.error("An error occurred, check console")
			})
	}

	return (
		<button
			type="button"
			role="button"
			aria-label="Delete chat"
			className="inline-flex items-center h-[32px] disabled:text-gray-500"
			disabled={!chats.length}
			onClick={handleDelete}
		>
			<BiTrash />
		</button>
	)
}

interface IDeleteChat {
	chats: Array<Chat>
	setChats: DispatchState<Array<Chat>>
}
