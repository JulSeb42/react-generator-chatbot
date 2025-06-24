import type { Chat } from "types"

export interface IMessaging {
	chat: Array<Chat>
	setChat: DispatchState<Array<Chat>>
	isLoading: boolean
	setIsLoading: DispatchState<boolean>
}
