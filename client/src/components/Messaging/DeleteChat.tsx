import { toast } from "react-toastify"
import { BiTrash } from "react-icons/bi"
import { chatService } from "api"
import { ButtonIcon } from "components/ButtonIcon"
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
		<ButtonIcon
			icon={<BiTrash />}
			onClick={handleDelete}
			tooltip="Delete chat"
			disabled={!chats.length}
			role="button"
			aria-label="Delete chat"
		/>
	)
}

interface IDeleteChat {
	chats: Array<Chat>
	setChats: DispatchState<Array<Chat>>
}
