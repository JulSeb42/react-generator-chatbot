import { toast } from "react-toastify"
import { Alert } from "components/Alert"
import { Button } from "components/Button"
import { chatService } from "api"
import type { Chat } from "types"

export const DeleteChat: FC<IDeleteChat> = ({
	isOpen,
	setIsOpen,
	setChats,
}) => {
	const session_id = localStorage.getItem("session_id")

	const handleDelete = () => {
		chatService
			.deleteSession(session_id!)
			.then(() => {
				toast.success("Your chat has been deleted")
				setChats([])
			})
			.catch(err => {
				console.log(err)
				toast.error("An error occurred, check console")
			})
			.finally(() => setIsOpen(false))
	}

	if (!isOpen) return null

	return (
		<Alert>
			<p>Are you sure you want to delete your chat?</p>

			<div className="flex gap-2">
				<Button type="button" color="danger" onClick={handleDelete}>
					Yes, delete the chat
				</Button>

				<Button
					type="button"
					variant="secondary"
					color="danger"
					onClick={() => setIsOpen(false)}
				>
					No, cancel
				</Button>
			</div>
		</Alert>
	)
}

interface IDeleteChat {
	isOpen: boolean
	setIsOpen: DispatchState<boolean>
	setChats: DispatchState<Array<Chat>>
}
